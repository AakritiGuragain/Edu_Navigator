from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'edu-navigator-secret-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///education_navigator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB max upload

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─────────────────────────────────────────────
#   MODELS
# ─────────────────────────────────────────────

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # JSON string for user preferences, e.g. {"preferences": ["Computer Science"], "location": "Kathmandu", "max_fees": 60000}
    profile = db.Column(db.Text, default='{}')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_profile_dict(self):
        try:
            return json.loads(self.profile or '{}')
        except Exception:
            return {}


class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    programs = db.relationship('Program', backref='college', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_programs=False):
        d = {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
        }
        if include_programs:
            d['programs'] = [p.to_dict() for p in self.programs]
        return d


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.String(50))
    fees = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'college_id': self.college_id,
            'college': self.college.name if self.college else '',
            'college_location': self.college.location if self.college else '',
            'description': self.description,
            'duration': self.duration,
            'fees': self.fees,
        }


class CVTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'filename': self.filename,
            'description': self.description,
        }


@login_manager.user_loader
def load_user(user_id):
    # SQLAlchemy 2.x compatible
    return db.session.get(User, int(user_id))


# ─────────────────────────────────────────────
#   FORMS
# ─────────────────────────────────────────────

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Create Account')


class ProfileForm(FlaskForm):
    preferences = StringField('Subject Interests (comma-separated)',
                               validators=[Optional()],
                               description='e.g. Computer Science, Engineering, Business')
    location = StringField('Preferred Location', validators=[Optional()])
    max_fees = StringField('Max Annual Fees (NRS)', validators=[Optional()])
    submit = SubmitField('Update Profile')


class CVUploadForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    file = FileField('CV Template File (PDF, DOC, DOCX)', validators=[DataRequired()])
    submit = SubmitField('Upload Template')


# ─────────────────────────────────────────────
#   RECOMMENDATION ENGINE
# ─────────────────────────────────────────────

def get_recommendations(user, limit=10):
    """
    Score every program against the user's profile preferences.
    Scoring:
      +3 per matching keyword in name or description
      +2 if college location matches preferred location
      # -1 per NRS 100,000 over max_fees (penalise expensive programs)
    Returns a sorted list of top programs as dicts.
    """
    profile = user.get_profile_dict()
    preferences = [p.strip().lower() for p in profile.get('preferences', []) if p.strip()]
    preferred_location = profile.get('location', '').strip().lower()
    try:
        max_fees = float(profile.get('max_fees', 0))
    except (ValueError, TypeError):
        max_fees = 0

    programs = Program.query.all()
    scored = []
    for program in programs:
        score = 0
        name_lower = program.name.lower()
        desc_lower = (program.description or '').lower()
        college_loc = (program.college.location or '').lower() if program.college else ''

        # Keyword matching
        for keyword in preferences:
            if keyword in name_lower:
                score += 3
            if keyword in desc_lower:
                score += 1

        # Location bonus
        if preferred_location and preferred_location in college_loc:
            score += 2

        # Fee penalty
        if max_fees and program.fees and program.fees > max_fees:
            over = (program.fees - max_fees) / 100000
            score -= over

        if score > 0 or not preferences:
            scored.append((score, program))

    # Sort by score descending first, then by program name
    scored.sort(key=lambda x: (-x[0], x[1].name))
    return [p.to_dict() for _, p in scored[:limit]]


# ─────────────────────────────────────────────
#   PAGE ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    recommendations = get_recommendations(current_user, limit=6)
    return render_template('dashboard.html', recommendations=recommendations)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    profile_data = current_user.get_profile_dict()

    if form.validate_on_submit():
        prefs = [p.strip() for p in form.preferences.data.split(',') if p.strip()]
        profile_data['preferences'] = prefs
        profile_data['location'] = form.location.data.strip()
        try:
            profile_data['max_fees'] = float(form.max_fees.data) if form.max_fees.data else 0
        except ValueError:
            profile_data['max_fees'] = 0
        current_user.profile = json.dumps(profile_data)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    # Pre-populate form
    form.preferences.data = ', '.join(profile_data.get('preferences', []))
    form.location.data = profile_data.get('location', '')
    form.max_fees.data = str(profile_data.get('max_fees', ''))
    return render_template('profile.html', form=form)


@app.route('/colleges')
def colleges():
    json_path = os.path.join(app.root_path, 'data', 'colleges.json')
    colleges_data = []
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            colleges_data = json.load(f).get('colleges', [])
    except Exception as e:
        print(f"Error loading colleges json: {e}")
    return render_template('colleges.html', colleges_json=json.dumps(colleges_data))


@app.route('/programs')
def programs():
    college_id = request.args.get('college_id', type=int)
    if college_id:
        all_programs = Program.query.filter_by(college_id=college_id).order_by(Program.name).all()
    else:
        all_programs = Program.query.order_by(Program.name).all()
    all_colleges = College.query.order_by(College.name).all()
    return render_template('programs.html', programs=all_programs, colleges=all_colleges,
                           selected_college_id=college_id)


@app.route('/cv_templates')
def cv_templates():
    templates = CVTemplate.query.all()
    return render_template('cv_templates.html', templates=templates)


@app.route('/upload_cv', methods=['GET', 'POST'])
@login_required
def upload_cv():
    form = CVUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if not allowed_file(file.filename):
            flash('Only PDF, DOC, and DOCX files are allowed.', 'error')
            return render_template('upload_cv.html', form=form)
        filename = secure_filename(file.filename)
        # Avoid filename collision
        base, ext = os.path.splitext(filename)
        counter = 1
        target = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        while os.path.exists(target):
            filename = f"{base}_{counter}{ext}"
            target = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1
        file.save(target)
        template = CVTemplate(
            name=form.name.data,
            filename=filename,
            description=form.description.data,
            uploaded_by=current_user.id
        )
        db.session.add(template)
        db.session.commit()
        flash('CV Template uploaded successfully!', 'success')
        return redirect(url_for('cv_templates'))
    return render_template('upload_cv.html', form=form)


@app.route('/download_cv/<int:template_id>')
def download_cv(template_id):
    template = db.session.get(CVTemplate, template_id)
    if template is None:
        flash('Template not found.', 'error')
        return redirect(url_for('cv_templates'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], template.filename, as_attachment=True)


@app.route('/cv_builder')
def cv_builder():
    return render_template('cv_builder.html')


# ─────────────────────────────────────────────
#   API ENDPOINTS
# ─────────────────────────────────────────────

@app.route('/api/colleges', methods=['GET'])
def api_colleges():
    q = request.args.get('q', '').strip()
    location = request.args.get('location', '').strip()
    program_type = request.args.get('program_type', '').strip()

    query = College.query
    if q:
        query = query.filter(College.name.ilike(f'%{q}%'))
    if location:
        query = query.filter(College.location.ilike(f'%{location}%'))
    if program_type:
        query = query.join(Program).filter(Program.name.ilike(f'%{program_type}%'))

    colleges = query.order_by(College.name).all()
    return jsonify([c.to_dict() for c in colleges])


@app.route('/api/colleges/<int:college_id>', methods=['GET'])
def api_college_detail(college_id):
    college = db.session.get(College, college_id)
    if college is None:
        return jsonify({'error': 'College not found'}), 404
    return jsonify(college.to_dict(include_programs=True))


@app.route('/api/colleges', methods=['POST'])
@login_required
def api_create_college():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    college = College(
        name=data['name'],
        location=data.get('location', ''),
        description=data.get('description', '')
    )
    db.session.add(college)
    db.session.commit()
    return jsonify(college.to_dict()), 201


@app.route('/api/colleges/<int:college_id>', methods=['PUT'])
@login_required
def api_update_college(college_id):
    college = db.session.get(College, college_id)
    if college is None:
        return jsonify({'error': 'College not found'}), 404
    data = request.get_json()
    college.name = data.get('name', college.name)
    college.location = data.get('location', college.location)
    college.description = data.get('description', college.description)
    db.session.commit()
    return jsonify(college.to_dict())


@app.route('/api/colleges/<int:college_id>', methods=['DELETE'])
@login_required
def api_delete_college(college_id):
    college = db.session.get(College, college_id)
    if college is None:
        return jsonify({'error': 'College not found'}), 404
    db.session.delete(college)
    db.session.commit()
    return jsonify({'message': 'College deleted'})


@app.route('/api/programs', methods=['GET'])
def api_programs():
    college_id = request.args.get('college_id', type=int)
    q = request.args.get('q', '').strip()

    query = Program.query
    if q:
        query = query.filter(Program.name.ilike(f'%{q}%'))
    if college_id:
        query = query.filter_by(college_id=college_id)

    programs = query.order_by(Program.name).all()
    return jsonify([p.to_dict() for p in programs])


@app.route('/api/programs/<int:program_id>', methods=['GET'])
def api_program_detail(program_id):
    program = db.session.get(Program, program_id)
    if program is None:
        return jsonify({'error': 'Program not found'}), 404
    return jsonify(program.to_dict())


@app.route('/api/programs', methods=['POST'])
@login_required
def api_create_program():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('college_id'):
        return jsonify({'error': 'name and college_id are required'}), 400
    college = db.session.get(College, data['college_id'])
    if college is None:
        return jsonify({'error': 'College not found'}), 404
    program = Program(
        name=data['name'],
        college_id=data['college_id'],
        description=data.get('description', ''),
        duration=data.get('duration', ''),
        fees=data.get('fees')
    )
    db.session.add(program)
    db.session.commit()
    return jsonify(program.to_dict()), 201


@app.route('/api/programs/<int:program_id>', methods=['PUT'])
@login_required
def api_update_program(program_id):
    program = db.session.get(Program, program_id)
    if program is None:
        return jsonify({'error': 'Program not found'}), 404
    data = request.get_json()
    program.name = data.get('name', program.name)
    program.college_id = data.get('college_id', program.college_id)
    program.description = data.get('description', program.description)
    program.duration = data.get('duration', program.duration)
    program.fees = data.get('fees', program.fees)
    db.session.commit()
    return jsonify(program.to_dict())


@app.route('/api/programs/<int:program_id>', methods=['DELETE'])
@login_required
def api_delete_program(program_id):
    program = db.session.get(Program, program_id)
    if program is None:
        return jsonify({'error': 'Program not found'}), 404
    db.session.delete(program)
    db.session.commit()
    return jsonify({'message': 'Program deleted'})


@app.route('/api/recommendations', methods=['GET'])
@login_required
def api_recommendations():
    results = get_recommendations(current_user, limit=10)
    return jsonify(results)


@app.route('/api/profile', methods=['GET'])
@login_required
def api_get_profile():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'profile': current_user.get_profile_dict()
    })


@app.route('/api/profile', methods=['PUT'])
@login_required
def api_update_profile():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'JSON body required'}), 400
    profile_data = current_user.get_profile_dict()
    if 'preferences' in data:
        profile_data['preferences'] = data['preferences']
    if 'location' in data:
        profile_data['location'] = data['location']
    if 'max_fees' in data:
        try:
            profile_data['max_fees'] = float(data['max_fees'])
        except (ValueError, TypeError):
            return jsonify({'error': 'max_fees must be a number'}), 400
    current_user.profile = json.dumps(profile_data)
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'profile': profile_data})


@app.route('/api/cv_templates', methods=['GET'])
def api_cv_templates():
    templates = CVTemplate.query.all()
    return jsonify([t.to_dict() for t in templates])


# ─────────────────────────────────────────────
#   MAIN
# ─────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True, port=5001)