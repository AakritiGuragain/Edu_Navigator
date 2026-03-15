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
from datetime import datetime

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
    full_name = db.Column(db.String(300))
    short_name = db.Column(db.String(50))
    type = db.Column(db.String(50))  # Government, Private, etc.
    affiliation = db.Column(db.String(200)) # TU, KU, PU, etc.
    established_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    scholarship_available = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(500))
    virtual_tour_url = db.Column(db.String(500))
    logo_url = db.Column(db.String(500))
    website = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    
    # New analytics/meta fields from updated JSON
    popularity_score = db.Column(db.Integer, default=0)
    total_students = db.Column(db.Integer)
    is_verified = db.Column(db.Boolean, default=True)
    
    # Relationships
    location = db.relationship('Location', backref='college', uselist=False, cascade='all, delete-orphan')
    hostel = db.relationship('Hostel', backref='college', uselist=False, cascade='all, delete-orphan')
    programs = db.relationship('Program', backref='college', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_programs=False, include_hostel=True):
        d = {
            'id': self.id,
            'name': self.name,
            'full_name': self.full_name,
            'short_name': self.short_name,
            'type': self.type,
            'affiliation': self.affiliation,
            'established_year': self.established_year,
            'description': self.description,
            'scholarship_available': self.scholarship_available,
            'image_url': self.image_url,
            'virtual_tour_url': self.virtual_tour_url,
            'logo_url': self.logo_url,
            'website': self.website,
            'popularity_score': self.popularity_score,
            'location': self.location.to_dict() if self.location else {},
        }
        if include_hostel:
            d['hostel'] = self.hostel.to_dict() if self.hostel else {'available': False}
        if include_programs:
            d['programs'] = [p.to_dict() for p in self.programs]
        return d


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    address = db.Column(db.String(300))
    city = db.Column(db.String(100))
    district = db.Column(db.String(100))
    province = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def to_dict(self):
        return {
            'address': self.address,
            'city': self.city,
            'district': self.district,
            'province': self.province,
            'coordinates': {'lat': self.latitude, 'lng': self.longitude}
        }

    def __repr__(self):
        return self.city or self.district or self.address or "Nepal"


class Hostel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    available = db.Column(db.Boolean, default=False)
    on_campus = db.Column(db.Boolean, default=False)
    capacity = db.Column(db.Integer)
    monthly_fee = db.Column(db.Float)
    gender = db.Column(db.String(50))  # Male, Female, Both
    meals_included = db.Column(db.Boolean, default=False)
    amenities = db.Column(db.Text)  # Comma separated list

    def to_dict(self):
        return {
            'available': self.available,
            'on_campus': self.on_campus,
            'capacity': self.capacity or 'N/A',
            'monthly_fee': self.monthly_fee or 'N/A',
            'gender': self.gender,
            'meals_included': self.meals_included,
            'amenities': [a.strip() for a in self.amenities.split(',')] if self.amenities else []
        }


class Scholarship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(200))
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    amount = db.Column(db.String(100))
    eligibility = db.Column(db.Text)
    apply_link = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(50))  # Government, International, Private

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'provider': self.provider,
            'description': self.description,
            'deadline': self.deadline.strftime('%Y-%m-%d') if self.deadline else 'No Deadline',
            'amount': self.amount,
            'eligibility': self.eligibility,
            'apply_link': self.apply_link,
            'is_active': self.is_active,
            'category': self.category
        }


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.String(50))
    fees = db.Column(db.Float)
    gpa_requirement = db.Column(db.Float)
    field = db.Column(db.String(100)) # Engineering, Management, etc.
    entrance_required = db.Column(db.Boolean, default=False)
    entrance_exam = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'college_id': self.college_id,
            'college': self.college.name if self.college else '',
            'description': self.description,
            'duration': self.duration,
            'fees': self.fees,
            'gpa_requirement': self.gpa_requirement,
            'field': self.field,
            'entrance_required': self.entrance_required,
            'entrance_exam': self.entrance_exam
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


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(50), unique=True)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=True)
    college_name = db.Column(db.String(200))
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))
    venue_name = db.Column(db.String(200))
    address = db.Column(db.String(300))
    google_maps_link = db.Column(db.String(500))
    description = db.Column(db.Text)
    registration_link = db.Column(db.String(500))
    is_open_to_public = db.Column(db.Boolean, default=True)
    verified = db.Column(db.Boolean, default=False)
    poster_url = db.Column(db.String(500))
    is_featured = db.Column(db.Boolean, default=False)
    tags = db.Column(db.Text) # Comma separated

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'college_name': self.college_name or (self.college.name if self.college else 'Unknown'),
            'title': self.title,
            'type': self.type.replace('_', ' ').title(),
            'start_date': self.start_date,
            'end_date': self.end_date,
            'time': f"{self.start_time} - {self.end_time}" if self.start_time and self.end_time else self.start_time,
            'venue': self.venue_name,
            'address': self.address,
            'google_maps_link': self.google_maps_link,
            'description': self.description,
            'registration_link': self.registration_link,
            'is_open_to_public': self.is_open_to_public,
            'verified': self.verified,
            'poster_url': self.poster_url,
            'is_featured': self.is_featured,
            'tags': [t.strip() for t in self.tags.split(',')] if self.tags else []
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
    gpa = StringField('GPA', validators=[Optional()], render_kw={"type": "number", "step": "0.1", "min": "0", "max": "4.0", "placeholder": "e.g. 3.5"})
    location = StringField('Preferred Location', validators=[Optional()])
    max_fees = StringField('Max Annual Fees (NPR)', validators=[Optional()], render_kw={"type": "number", "step": "1000", "min": "0", "placeholder": "e.g. 800000"})
    wants_scholarship = SelectField('Needs Scholarship', choices=[('no', 'No'), ('yes', 'Yes')], validators=[Optional()])
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
    Score every program against the user's profile preferences using the weighted algorithm:
      - GPA Match (40%)
      - Budget vs Fees (30%)
      - Program Match (20%)
      - Scholarship Availability (10%)
    Returns a sorted list of top programs as dicts.
    Returns a sorted list of top programs as dicts.
    """
    weights = {'gpa': 40, 'budget': 30, 'program': 20, 'scholarship': 10}
    
    profile = user.get_profile_dict()
    student_gpa = profile.get('gpa', 0.0)
    preferences = [p.strip().lower() for p in profile.get('preferences', []) if p.strip()]
    wants_scholarship = profile.get('wants_scholarship', False)
    try:
        max_fees = float(profile.get('max_fees', 0))
    except (ValueError, TypeError):
        max_fees = 0.0

    programs = Program.query.all()
    scored = []
    
    for program in programs:
        college = program.college
        # 1. GPA Match (Weight 40%)
        req_gpa = program.gpa_requirement or 0.0
        if req_gpa == 0:
            gpa_score = 100
        elif student_gpa >= req_gpa:
            gpa_score = 100
        else:
            gap = req_gpa - student_gpa
            gpa_score = max(0, 100 - (gap * 50))
            
        # 2. Budget vs Fees (Weight 30%)
        fees = program.fees or 0.0
        if fees == 0 or max_fees == 0:
            budget_score = 100
        elif fees <= max_fees:
            budget_score = 100
        else:
            excess = fees - max_fees
            budget_penalty = (excess / max_fees) * 100
            budget_score = max(0, 100 - budget_penalty)
            
        # 3. Program/Field Match (Weight 20%)
        # Check against field or name
        name_lower = program.name.lower()
        field_lower = (program.field or '').lower()
        desc_lower = (program.description or '').lower()
        
        if not preferences:
            program_score = 100
        else:
            match_found = any(p in name_lower or p in field_lower or p in desc_lower for p in preferences)
            program_score = 100 if match_found else 0
                
        # 4. Scholarship & Popularity (Weight 10%)
        # Bonus for popularity score (0-100) and scholarship
        pop_score = college.popularity_score if college else 50
        scholarship_bonus = 20 if (college and college.scholarship_available and wants_scholarship) else 0
        final_meta_score = min(100, (pop_score * 0.8) + scholarship_bonus)

        # Total Weighting
        total_score = (
            (gpa_score * 0.4) + 
            (budget_score * 0.3) + 
            (program_score * 0.2) + 
            (final_meta_score * 0.1)
        )
        
        if wants_scholarship:
            if col_scholarship:
                scholarship_score = 100
            else:
                scholarship_score = 0
        else:
            scholarship_score = 100
            
        # Total Score
        total_score = (
            (gpa_score * weights['gpa'] / 100) +
            (budget_score * weights['budget'] / 100) +
            (program_score * weights['program'] / 100) +
            (scholarship_score * weights['scholarship'] / 100)
        )
        
        if total_score > 0 or not preferences:
            p_dict = program.to_dict()
            p_dict['compatibility_score'] = round(total_score, 2)
            scored.append((total_score, p_dict))

    # Sort by score descending first, then by program name
    scored.sort(key=lambda x: (-x[0], x[1]['name']))
    return [p_dict for _, p_dict in scored[:limit]]


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


def get_readiness_score(user):
    score = 0
    profile_data = user.get_profile_dict()
    
    # 1. Profile Completeness (30%)
    if profile_data.get('subject_interest'): score += 10
    if profile_data.get('gpa'): score += 10
    if profile_data.get('budget_max'): score += 10
    
    # 2. Key Actions (40%)
    # Check if user has uploaded a CV (stub for now based on if they have a CVTemplate interaction or similar)
    # Since we don't have a 'activities' table yet, we'll use a simple heuristic
    if user.email: score += 10 # Sign up bonus
    
    # Check if they have specific preferences set
    if profile_data.get('hostel_needed'): score += 10
    
    # Milestone: Exams Explored (simulated)
    # We could add an 'activity_log' in the future, for now let's check profile complexity
    if len(profile_data) > 5: score += 20
    
    # Milestone: CV Uploaded
    # Let's assume the user model has a cv_path or similar in the future.
    
    return min(100, score)


@app.route('/dashboard')
@login_required
def dashboard():
    recommendations = get_recommendations(current_user, limit=6)
    readiness = get_readiness_score(current_user)
    
    milestones = [
        {"title": "Complete Smart Profile", "completed": readiness >= 30, "points": 30},
        {"title": "Explore Entrance Roadmap", "completed": True, "points": 20}, # Everyone gets this for free for now
        {"title": "Research 3+ Colleges", "completed": len(recommendations) >= 3, "points": 20},
        {"title": "Prepare & Upload CV", "completed": False, "points": 30}
    ]
    
    return render_template('dashboard.html', 
                           recommendations=recommendations, 
                           readiness=readiness,
                           milestones=milestones)


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
            profile_data['gpa'] = float(form.gpa.data) if form.gpa.data else 0.0
        except ValueError:
            profile_data['gpa'] = 0.0
            
        profile_data['wants_scholarship'] = form.wants_scholarship.data == 'yes'

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
    form.gpa.data = str(profile_data.get('gpa', '')) if profile_data.get('gpa', 0.0) != 0.0 else ''
    form.wants_scholarship.data = 'yes' if profile_data.get('wants_scholarship') else 'no'
    form.location.data = profile_data.get('location', '')
    form.max_fees.data = str(profile_data.get('max_fees', '')) if profile_data.get('max_fees', 0) != 0 else ''
    return render_template('profile.html', form=form)


@app.route('/institutions')
@app.route('/colleges')
def colleges():
    all_colleges = College.query.order_by(College.name).all()
    colleges_data = [c.to_dict(include_programs=True, include_hostel=True) for c in all_colleges]
    return render_template('colleges.html', colleges_json=json.dumps(colleges_data))


@app.route('/programs')
def programs():
    # Redirect to the unified institutions view
    return redirect(url_for('colleges'))


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


# Entrance Exam Readiness Module Data
EXAMS_DATA = {
    'ioe': {
        'name': 'IOE Entrance Exam',
        'tag': 'IOE PREP',
        'description': 'Entrance exam for Bachelor of Engineering programs in TU affiliated and constituent campuses.',
        'syllabus_link': 'https://entrance.ioe.edu.np/syllabus',
        'past_papers_link': 'https://entrance.ioe.edu.np/previous-papers',
        'recommended_books': ['M.K. Publishers Engineering Entrance Preparation', 'PEA Question Bank'],
        'subjects': ['Physics', 'Chemistry', 'Math', 'English'],
        'exam_date': 'June 20, 2025',
        'total_marks': '140 (Physics · Chemistry · Math)',
        'app_fee': 'NPR 2,000',
        'stat_label': 'Applicants 2024',
        'stat_value': '25,000+',
        'competition': 'High competition',
        'competition_level': 'high'
    },
    'cmat': {
        'name': 'CMAT',
        'tag': 'CMAT PREP',
        'description': 'Common Management Admission Test for BBA, BBM, BHM, and BTTM programs under Tribhuvan University.',
        'syllabus_link': 'https://fomecd.edu.np/cmat-syllabus',
        'past_papers_link': 'https://edusanjal.com/exam/cmat-past-questions/',
        'recommended_books': ['KEC CMAT Preparation', 'Top-up CMAT'],
        'subjects': ['Verbal Ability', 'Quantitative Ability', 'Logical Reasoning', 'General Awareness'],
        'exam_date': 'May 15, 2025',
        'total_marks': '100 (MCQ format)',
        'app_fee': 'NPR 1,000',
        'stat_label': 'Pass rate 2024',
        'stat_value': '68%',
        'competition': 'Moderate',
        'competition_level': 'moderate'
    },
    'pahs': {
        'name': 'PAHS Medical Entrance',
        'tag': 'PAHS PREP',
        'description': 'Admission test for MBBS, BDS, and Nursing programs at Patan Academy of Health Sciences.',
        'syllabus_link': 'https://pahs.edu.np/admission/syllabus/',
        'past_papers_link': 'https://edusanjal.com/exam/mbbs-entrance-questions-pahs/',
        'recommended_books': ['Medical Entrance Comprehensive Guide', 'PAHS Success Pack'],
        'subjects': ['Physics', 'Chemistry', 'Biology', 'General Knowledge'],
        'conducted_by': 'PAHS, Lalitpur',
        'programs_covered': 'MBBS · BDS · Nursing',
        'stat_label': 'Avg starting salary',
        'stat_value': 'NPR 8,00,000/yr',
        'competition': 'Very competitive',
        'competition_level': 'very-high'
    }
}


@app.route('/exams')
def exams():
    return render_template('exams.html', exams=EXAMS_DATA)


@app.route('/exams/<exam_type>')
def exam_detail(exam_type):
    exam = EXAMS_DATA.get(exam_type.lower())
    if not exam:
        flash('Exam information not found.', 'error')
        return redirect(url_for('exams'))
    return render_template('exam_detail.html', exam=exam, exam_type=exam_type)


@app.route('/events')
def events():
    all_events = Event.query.order_by(Event.start_date.asc()).all()
    events_data = [e.to_dict() for e in all_events]
    return render_template('events.html', events=events_data)


@app.route('/compare')
def compare():
    ids = request.args.get('ids', '')
    return render_template('compare.html', college_ids=ids)


@app.route('/api/compare')
def api_compare():
    ids_str = request.args.get('ids', '')
    if not ids_str:
        return jsonify({'error': 'No college IDs provided'}), 400
    
    try:
        ids = [int(x) for x in ids_str.split(',') if x.strip()]
    except ValueError:
        return jsonify({'error': 'Invalid college IDs'}), 400
        
    colleges = College.query.filter(College.id.in_(ids)).all()
    # Maintain order of requested IDs
    id_map = {c.id: c for c in colleges}
    ordered_colleges = [id_map[i] for i in ids if i in id_map]
    
    return jsonify([c.to_dict(include_programs=True, include_hostel=True) for c in ordered_colleges])


@app.route('/api/upload_resume', methods=['POST'])
@login_required
def api_upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # For this demonstration, we'll "read" the resume by scanning for keywords
    # In a production app, we would use pdfplumber or an AI API
    content = ""
    try:
        # Basic text scan if it's a text file, else simulated scan
        if file.filename.endswith('.txt'):
            content = file.read().decode('utf-8').lower()
        else:
            # Simulated AI extraction for PDF/Doc based on filename/metadata
            # We'll assume the user is helpful for this demo
            content = file.filename.lower() + " bachelor engineering 3.8 gpa computer science"
            
        profile_data = current_user.get_profile_dict()
        
        # Simple extraction logic
        extracted = {}
        if "engineer" in content or "civil" in content: extracted["subject_interest"] = "Engineering"
        elif "computer" in content or "it" in content or "software" in content: extracted["subject_interest"] = "Information Technology"
        elif "medical" in content or "doctor" in content: extracted["subject_interest"] = "Medical"
        elif "management" in content or "business" in content: extracted["subject_interest"] = "Management"
        
        # GPA Extraction (looks for numbers like 3.x or 4.0)
        gpa_match = re.search(r'([0-4]\.\d+)', content)
        if gpa_match:
            extracted["gpa"] = float(gpa_match.group(1))

        # Update profile
        profile_data.update(extracted)
        current_user.profile = json.dumps(profile_data)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Magic Match complete! Your profile has been updated.',
            'extracted': extracted
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/scholarships')
def scholarships():
    all_scholarships = Scholarship.query.filter_by(is_active=True).order_by(Scholarship.deadline.asc()).all()
    return render_template('scholarships.html', scholarships=all_scholarships, now=datetime.now())


@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Simple rule-based logic for the AI advisor
    response = ""
    
    if "best" in message or "top" in message or "recommend" in message:
        # Get recommendations based on current user or general top colleges
        if current_user.is_authenticated:
            recs = get_recommendations(current_user, limit=3)
            if recs:
                names = [r['college'] for r in recs]
                response = f"Based on your profile, I recommend looking at {', '.join(names)}. They match your GPA and subject interests!"
            else:
                response = "I'd love to help! Could you update your profile with your GPA and interests so I can give you a better recommendation?"
        else:
            top_colleges = College.query.order_by(College.popularity_score.desc()).limit(3).all()
            names = [c.name for c in top_colleges]
            response = f"Check out these top-rated colleges in Nepal: {', '.join(names)}."
            
    elif "fee" in message or "cost" in message or "budget" in message:
        response = "The fees vary by program. Generally, government colleges are much more affordable (NPR 2-4 lakhs total) compared to private or foreign-affiliated ones (NPR 8-15 lakhs). You can filter programs by budget on our Programs page!"
        
    elif "hostel" in message:
        response = "Most major constituent campuses like Pulchowk and TU Kirtipur have on-campus hostels, though seats are limited. Private colleges like KIST and NCIT also offer hostel facilities. Look for the \ud83c\udfe0 badge on college cards!"
        
    elif "event" in message or "upcoming" in message or "happen" in message:
        upcoming_events = Event.query.filter(Event.verified == True).limit(3).all()
        if upcoming_events:
            names = [e.title for e in upcoming_events]
            response = f"There are some exciting events coming up! Check out: {', '.join(names)}. You can see the full list on our new Event Board!"
        else:
            response = "We don't have any verified upcoming events right now, but stay tuned! You can browse the Community Event Board for recent submissions."

    elif "ioe" in message or "engineering" in message:
        response = "Engineering in Nepal is highly competitive. The IOE Entrance Exam is usually held in June. Constituent colleges like Pulchowk are the most sought after. Would you like to see the Entrance Exam Roadmap?"
        
    else:
        response = "I am your Education Navigator AI! I can help you find colleges, understand fee structures, or prepare for entrance exams. Try asking 'What are the best engineering colleges?' or 'Which colleges have hostels?'"

    return jsonify({'response': response})


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