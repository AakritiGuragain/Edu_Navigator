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
import re
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'edu-navigator-secret-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///education_navigator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
AVATAR_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'avatars')
os.makedirs(AVATAR_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB max upload

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
AVATAR_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_avatar(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in AVATAR_EXTENSIONS


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
    photo = FileField('Profile Photo', validators=[Optional()])
    preferences = StringField('Subject Interests (comma-separated)',
                               validators=[Optional()],
                               description='e.g. Computer Science, Engineering, Business')
    gpa = StringField('GPA', validators=[Optional()], render_kw={"type": "number", "step": "0.1", "min": "0", "max": "4.0", "placeholder": "e.g. 3.5"})
    location = StringField('Preferred Location', validators=[Optional()])
    max_fees = StringField('Max Annual Fees (NPR)', validators=[Optional()], render_kw={"type": "number", "step": "1000", "min": "0", "placeholder": "e.g. 800000"})
    wants_scholarship = SelectField('Needs Scholarship', choices=[('no', 'No'), ('yes', 'Yes')], validators=[Optional()])
    submit = SubmitField('Update Profile')



# ─────────────────────────────────────────────
#   AI MATCHING ENGINE (USP)
# ─────────────────────────────────────────────

def _fetch_programs_with_colleges():
    """Fetch all programs with their colleges (runs in app context where db is bound)."""
    from sqlalchemy.orm import joinedload
    programs = Program.query.options(joinedload(Program.college)).all()
    return [(p, p.college) for p in programs if p.college]


def get_recommendations(user, limit=10):
    """
    Uses the AI matcher to get personalized college-program recommendations
    based on GPA, budget, preferences, scholarship need, and location.
    """
    from ai_matcher import get_ai_matches
    programs_data = _fetch_programs_with_colleges()
    return get_ai_matches(user, limit=limit, include_reasons=False, programs_data=programs_data)


# ─────────────────────────────────────────────
#   PAGE ROUTES
# ─────────────────────────────────────────────

_seed_done = False

@app.before_request
def _maybe_seed():
    global _seed_done
    if _seed_done:
        return
    try:
        db.create_all()
        if College.query.count() == 0:
            seed_sample_colleges()
    except Exception:
        pass
    _seed_done = True


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
    # Sign up bonus
    if user.email: score += 10
    
    # Check if they have specific preferences set
    if profile_data.get('hostel_needed'): score += 10
    
    # Milestone: Exams Explored (simulated)
    # We could add an 'activity_log' in the future, for now let's check profile complexity
    if len(profile_data) > 5: score += 20
    
    return min(100, score)


@app.route('/dashboard')
@login_required
def dashboard():
    recommendations = get_recommendations(current_user, limit=6)
    readiness = get_readiness_score(current_user)
    
    milestones = [
        {"title": "Complete Smart Profile", "completed": readiness >= 30, "points": 30},
        {"title": "Explore Entrance Roadmap", "completed": True, "points": 20}, # Everyone gets this for free for now
        {"title": "Research 3+ Colleges", "completed": len(recommendations) >= 3, "points": 20}
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
        if form.photo.data and form.photo.data.filename:
            file = form.photo.data
            if allowed_avatar(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M')}.{ext}"
                filepath = os.path.join(AVATAR_FOLDER, filename)
                file.save(filepath)
                profile_data['photo_url'] = f"uploads/avatars/{filename}"
            else:
                flash('Photo must be JPG, PNG, GIF or WebP.', 'error')
        raw_prefs = form.preferences.data or ''
        prefs = [p.strip() for p in str(raw_prefs).split(',') if p.strip()]
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

    # Pre-populate form (handle list or legacy string)
    prefs_raw = profile_data.get('preferences', [])
    form.preferences.data = ', '.join(prefs_raw) if isinstance(prefs_raw, list) else (prefs_raw or '')
    form.gpa.data = str(profile_data.get('gpa', '')) if profile_data.get('gpa', 0.0) != 0.0 else ''
    form.wants_scholarship.data = 'yes' if profile_data.get('wants_scholarship') else 'no'
    form.location.data = profile_data.get('location', '')
    form.max_fees.data = str(profile_data.get('max_fees', '')) if profile_data.get('max_fees', 0) != 0 else ''
    return render_template('profile.html', form=form)


def load_university_fees():
    """Load fee data from the Excel sheet and return a map of college -> fee info."""
    try:
        import openpyxl
    except ImportError:
        # openpyxl is optional; if missing, skip fee display.
        return {}

    fee_file = os.path.join(app.root_path, 'data', 'University Fees.xlsx')
    if not os.path.exists(fee_file):
        return {}

    wb = openpyxl.load_workbook(fee_file, data_only=True)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows or len(rows) < 4:
        return {}

    # Find header row (search for 'S.n')
    header_idx = None
    for i, r in enumerate(rows[:10]):
        if r and r[0] and str(r[0]).strip().lower() in ('s.n', 's.n.', 's.n'):
            header_idx = i
            break

    if header_idx is None or header_idx + 1 >= len(rows):
        return {}

    headers = [str(c).strip() if c is not None else '' for c in rows[header_idx]]
    fee_columns = {i: h for i, h in enumerate(headers) if h and h.lower() not in ('s.n', 'sn', 'serial', 'colleges')}

    fee_data = {}
    for row in rows[header_idx+1:]:
        if not row or not row[1]:
            continue
        college_name = str(row[1]).strip()
        if not college_name:
            continue
        row_data = {}
        for idx, col_name in fee_columns.items():
            value = row[idx] if idx < len(row) else None
            if value is None:
                continue
            text = str(value).strip()
            if not text or text.lower() in ('nan', 'none'):
                continue
            row_data[col_name] = text
        if row_data:
            fee_data[college_name] = row_data
    return fee_data


@app.route('/institutions')
@app.route('/colleges')
def colleges():
    all_colleges = College.query.order_by(College.name).all()
    colleges_data = [c.to_dict(include_programs=True, include_hostel=True) for c in all_colleges]
    fees_data = load_university_fees()
    return render_template('colleges.html', colleges_json=json.dumps(colleges_data), fees_json=json.dumps(fees_data))


@app.route('/programs')
def programs():
    # Redirect to the unified institutions view
    return redirect(url_for('colleges'))



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



@app.route('/ai-match')
def ai_match():
    """Standalone AI College Matcher page — separate from the chatbot."""
    return render_template('ai_match.html')


@app.route('/scholarships')
def scholarships():
    all_scholarships = Scholarship.query.filter_by(is_active=True).order_by(Scholarship.deadline.asc()).all()
    return render_template('scholarships.html', scholarships=all_scholarships, now=datetime.now())


@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    if not current_user.is_authenticated:
        # Fallback for non-authenticated users
        if "best" in message or "top" in message or "recommend" in message:
            top_colleges = College.query.order_by(College.popularity_score.desc()).limit(3).all()
            names = [c.name for c in top_colleges]
            response = f"Check out these top-rated colleges in Nepal: {', '.join(names)}. Log in to get personalized recommendations and save your chat history!"
        elif "fee" in message or "cost" in message or "budget" in message:
            response = "The fees vary by program. Generally, government colleges are much more affordable (NPR 2-4 lakhs total) compared to private or foreign-affiliated ones (NPR 8-15 lakhs)."
        elif "hostel" in message:
            response = "Most major constituent campuses have on-campus hostels, though seats are limited. Look for the 🏠 badge on college cards!"
        elif "event" in message or "upcoming" in message or "happen" in message:
            response = "Check out our new Event Board for upcoming tech fests, seminars, and more!"
        else:
            response = "I am your Education Navigator AI! I can help you find colleges. For a personalized experience and Chat Memory, please sign up and build your profile!"
        return jsonify({'response': response})
        
    profile_data = current_user.get_profile_dict()
    chat_history = profile_data.get('chat_history', [])
    
    response = ""
    profile_updated = False
    
    # 1. Update memory context from the new message
    gpa_match = re.search(r'(?:my\s+)?gpa\s+(?:is\s+)?([0-4](?:\.\d+)?)', message)
    if not gpa_match:
        gpa_match = re.search(r'([0-4](?:\.\d+)?)\s+gpa', message)
    if gpa_match:
        try:
            gpa = float(gpa_match.group(1))
            if 0 <= gpa <= 4.0:
                profile_data['gpa'] = gpa
                profile_updated = True
        except ValueError:
            pass
            
    # Budget extraction
    budget_match = re.search(r'(?:budget|fee|fees|cost).*?(?:is|around|max)?\s*(\d{1,3}(?:,\d{3})*(?:000|k|lakhs?))', message)
    if budget_match:
        val_str = budget_match.group(1).replace(',', '')
        val = 0
        if 'k' in val_str: val = float(val_str.replace('k', '')) * 1000
        elif 'lakh' in val_str: val = float(val_str.replace('lakhs', '').replace('lakh', '')) * 100000
        else:
            try: val = float(val_str)
            except: pass
        if val > 0:
            profile_data['max_fees'] = val
            profile_updated = True
            
    # Subjects extraction
    subjects = ['computer science', 'engineering', 'business', 'management', 'medical', 'nursing', 'arts', 'science', 'it']
    found_subjects = [sub for sub in subjects if sub in message and ("study" in message or "interest" in message or "want" in message or "like" in message)]
    if found_subjects:
        prefs = set(profile_data.get('preferences', []))
        for sub in found_subjects:
            prefs.add(sub.title())
        profile_data['preferences'] = list(prefs)
        profile_updated = True

    if profile_updated:
        current_user.profile = json.dumps(profile_data)
        db.session.commit()
        response += "I've updated your profile with the new details! "

    # 2. Add message to memory
    chat_history.append({"role": "user", "content": message})
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]
        
    # Analyze conversational state
    last_bot_msg = ""
    for msg in reversed(chat_history[:-1]):
        if msg['role'] == 'assistant':
            last_bot_msg = msg['content'].lower()
            break
            
    # Personalization contexts
    has_gpa = profile_data.get('gpa', 0.0) > 0
    has_prefs = len(profile_data.get('preferences', [])) > 0
    context_parts = []
    if has_gpa: context_parts.append(f"your GPA of {profile_data['gpa']}")
    if has_prefs: context_parts.append(f"your interest in {', '.join(profile_data['preferences'])}")
    if profile_data.get('max_fees'): context_parts.append(f"budget of NPR {profile_data['max_fees']}")
    context_str = " and ".join(context_parts) if context_parts else "your basic profile"

    # Generate customized response — chatbot passes match requests to the AI Matcher (separate system)
    match_page_link = '<a href="/ai-match" style="color:#1e40af;font-weight:600;">AI Match page</a>'
    if "recommend" in message or "best" in message or "top" in message or "match" in message or "find" in message:
        response += f"I've passed your request to our AI College Matcher. Go to the {match_page_link} to see your personalized college recommendations."
    elif "college" in message and ("suggest" in message or "which" in message or "help" in message):
        response += f"For personalized college suggestions, use our AI College Matcher. Visit the {match_page_link} to get matches tailored to your profile."
            
    elif "gpa" in message:
        if profile_data.get('gpa'):
            response += f"Got it! With your GPA of {profile_data['gpa']}, I can start matching you with programs. Would you like some college recommendations?"
        else:
            response += "What is your GPA? If you tell me, I'll memorize it and use it finding the perfect colleges for you."
            
    elif "fee" in message or "cost" in message or "budget" in message:
        if profile_data.get('max_fees'):
            response += f"Noted! I'll remember your budget is NPR {profile_data['max_fees']} for future recommendations. Need a list of colleges within that budget?"
        else:
            response += "What is your maximum budget per year? Share it, and I'll keep it in mind so you only see affordable colleges!"
            
    elif "profile" in message or "my info" in message or "what do you know" in message:
        if context_parts:
            response += f"From our past conversations and your profile, I have personalized your preferences to: {context_str}."
        else:
            response += "Your profile is still quite empty! Tell me your GPA, interested subjects, or budget!"
            
    elif "yes" in message or "sure" in message or "please" in message:
        if "ai match" in last_bot_msg or "match" in last_bot_msg:
            response += "Great! Go to the AI Match page to see your personalized college list. You can also check your dashboard for a preview."
        else:
            response += "Great! How else can I assist you with your education journey today?"
            
    elif "event" in message or "upcoming" in message:
        upcoming_events = Event.query.filter(Event.verified == True).limit(2).all()
        if upcoming_events:
            names = [e.title for e in upcoming_events]
            response += f"There are some exciting upcoming events: {', '.join(names)}."
        else:
            response += "No upcoming events right now, but I'll remember you're interested!"
            
    else:
        if not response:
            response = f"I'm keeping track of {context_str}. You can ask me for college recommendations, ask about scholarships, or just tell me more details like your GPA or budget to refine your profile!"
            
    # Save bot message to memory
    chat_history.append({"role": "assistant", "content": response.strip()})
    profile_data['chat_history'] = chat_history
    current_user.profile = json.dumps(profile_data)
    db.session.commit()

    return jsonify({'response': response.strip()})


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


@app.route('/api/ai-match', methods=['GET'])
def api_ai_match():
    """
    AI-powered college matching: returns personalized matches with compatibility
    scores and match reasons. Supports search by college name, program, or field.
    """
    from ai_matcher import get_ai_matches, get_match_summary
    limit = min(50, request.args.get('limit', 15, type=int))
    search = request.args.get('q', '').strip()
    user = current_user if current_user.is_authenticated else None
    profile = user.get_profile_dict() if user else {}
    programs_data = _fetch_programs_with_colleges()
    matches = get_ai_matches(user, limit=limit, include_reasons=True, search_query=search or None, programs_data=programs_data)
    summary = get_match_summary(profile)
    return jsonify({
        'matches': matches,
        'profile_summary': summary,
        'count': len(matches)
    })


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
#   SEED SAMPLE DATA
# ─────────────────────────────────────────────

def seed_sample_colleges():
    """Add sample colleges and programs if database is empty."""
    if College.query.first():
        return
    # IOE Pulchowk - flagship engineering college
    c1 = College(
        name="IOE Pulchowk Campus",
        full_name="Institute of Engineering, Pulchowk Campus",
        short_name="Pulchowk",
        type="Government",
        affiliation="Tribhuvan University",
        established_year=1972,
        description="Premier engineering college in Nepal. Offers BE programs in various disciplines.",
        scholarship_available=True,
        popularity_score=95,
        total_students=2500,
        logo_url='/static/images/logos/Pulchowk_Campus__TU-IOE.jpg',
        image_url='/static/images/logos/Pulchowk_Campus__TU-IOE.jpg'
    )
    db.session.add(c1)
    db.session.flush()
    loc1 = Location(college_id=c1.id, city="Lalitpur", district="Lalitpur", province="Bagmati", latitude=27.6710, longitude=85.3240)
    db.session.add(loc1)
    db.session.add(Program(name="BE Computer Engineering", college_id=c1.id, description="Bachelor in Computer Engineering", duration="4 Years", fees=450000, gpa_requirement=3.2, field="Computer Science", entrance_required=True, entrance_exam="IOE Entrance"))
    db.session.add(Program(name="BE Civil Engineering", college_id=c1.id, description="Bachelor in Civil Engineering", duration="4 Years", fees=420000, gpa_requirement=3.0, field="Engineering", entrance_required=True, entrance_exam="IOE Entrance"))
    db.session.add(Program(name="BE Electronics & Communication", college_id=c1.id, description="Bachelor in Electronics", duration="4 Years", fees=440000, gpa_requirement=3.1, field="Engineering", entrance_required=True, entrance_exam="IOE Entrance"))

    # Kathmandu University - private
    c2 = College(
        name="Kathmandu University School of Management",
        full_name="KUSOM",
        short_name="KUSOM",
        type="Private",
        affiliation="Kathmandu University",
        established_year=1993,
        description="Leading management school offering BBA, MBA programs.",
        scholarship_available=True,
        popularity_score=88,
        total_students=1200,
        logo_url='/static/images/logos/KU_School_of_Management__KUSOM.png',
        image_url='/static/images/logos/KU_School_of_Management__KUSOM.png'
    )
    db.session.add(c2)
    db.session.flush()
    loc2 = Location(college_id=c2.id, city="Lalitpur", district="Lalitpur", province="Bagmati", latitude=27.6150, longitude=85.5380)
    db.session.add(loc2)
    db.session.add(Program(name="BBA", college_id=c2.id, description="Bachelor of Business Administration", duration="4 Years", fees=850000, gpa_requirement=2.8, field="Management"))
    db.session.add(Program(name="BBM", college_id=c2.id, description="Bachelor of Business Management", duration="4 Years", fees=820000, gpa_requirement=2.8, field="Management"))

    # St. Xavier's - liberal arts
    c3 = College(
        name="St. Xavier's College",
        full_name="St. Xavier's College, Maitighar",
        short_name="SXC",
        type="Private",
        affiliation="Tribhuvan University",
        established_year=1988,
        description="Liberal arts and science college in Kathmandu.",
        scholarship_available=True,
        popularity_score=82,
        total_students=3000,
    )
    db.session.add(c3)
    db.session.flush()
    loc3 = Location(college_id=c3.id, city="Kathmandu", district="Kathmandu", province="Bagmati", latitude=27.7000, longitude=85.3167)
    db.session.add(loc3)
    db.session.add(Program(name="BSc Computer Science", college_id=c3.id, description="Bachelor of Science in Computer Science", duration="4 Years", fees=550000, gpa_requirement=2.9, field="Computer Science"))
    db.session.add(Program(name="BBA", college_id=c3.id, description="Bachelor of Business Administration", duration="4 Years", fees=520000, gpa_requirement=2.8, field="Management"))

    db.session.commit()


def ensure_college_program(college_name, program_name, **kwargs):
    """Ensure a specific program exists for a college, adding it if missing."""
    college = College.query.filter(College.name.ilike(f"%{college_name}%")).first()
    if not college:
        return False
    existing = next((p for p in college.programs if p.name and p.name.strip().lower() == program_name.strip().lower()), None)
    if existing:
        return False

    program = Program(
        name=program_name,
        college_id=college.id,
        description=kwargs.get('description', program_name),
        duration=kwargs.get('duration', '4 Years'),
        fees=kwargs.get('fees', 0.0),
        gpa_requirement=kwargs.get('gpa_requirement'),
        field=kwargs.get('field', 'IT'),
        entrance_required=kwargs.get('entrance_required', True),
        entrance_exam=kwargs.get('entrance_exam', 'Internal Selection')
    )
    db.session.add(program)
    db.session.commit()
    return True


# ─────────────────────────────────────────────
#   MAIN
# ─────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_sample_colleges()
        # Ensure King's College includes the IT program (BSIT) so it shows up in the comparison view.
        ensure_college_program(
            college_name="King's College",
            program_name='BSIT',
            description='Bachelor of Science in Information Technology',
            duration='4 Years',
            fees=1600000,
            field='IT',
            entrance_required=True,
            entrance_exam='Internal Selection'
        )
    app.run(host='0.0.0.0', debug=True, port=5001)