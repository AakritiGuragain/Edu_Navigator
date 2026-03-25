import pytest
from app import app, db, User, College, Program, Location, LOGIN_ATTEMPTS
from ai_matcher import compute_match_scores
import json
import io

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create a test user
            user = User(username="testuser", email="test@example.com")
            user.set_password("validpassword")
            db.session.add(user)
            db.session.commit()
            yield client
        with app.app_context():
            db.drop_all()

# --- Login Test Cases ---

def test_L_01_valid_login(client):
    """L-01 Valid login: Correct email + password -> User redirected to /dashboard"""
    res = client.post('/login', data={'email': 'test@example.com', 'password': 'validpassword'}, follow_redirects=True)
    assert res.status_code == 200
    assert b'dashboard' in res.data.lower() or b'logout' in res.data.lower()

def test_L_02_invalid_password(client):
    """L-02 Invalid password: Correct email + wrong password -> Error: "Invalid credentials" """
    res = client.post('/login', data={'email': 'test@example.com', 'password': 'wrongpassword'})
    assert b'Invalid credentials' in res.data

def test_L_03_non_existent_user(client):
    """L-03 Non-existent user: Unregistered email -> Error: "User not found" """
    res = client.post('/login', data={'email': 'unregistered@example.com', 'password': 'somepassword'})
    assert b'User not found' in res.data

def test_L_04_empty_fields(client):
    """L-04 Empty fields: No email & password -> Validation error shown"""
    res = client.post('/login', data={'email': '', 'password': ''})
    assert b'Email required error' in res.data
    assert b'Password required error' in res.data

def test_L_05_only_email_entered(client):
    """L-05 Only email entered: Password required error"""
    res = client.post('/login', data={'email': 'test@example.com', 'password': ''})
    assert b'Password required error' in res.data

def test_L_06_only_password_entered(client):
    """L-06 Only password entered: Email required error"""
    res = client.post('/login', data={'email': '', 'password': 'validpassword'})
    assert b'Email required error' in res.data

def test_L_07_invalid_email_format(client):
    """L-07 Invalid email format: Email format error"""
    res = client.post('/login', data={'email': 'user@com', 'password': 'validpassword'})
    assert b'Email format error' in res.data

def test_L_08_leading_trailing_spaces(client):
    res = client.post('/login', data={'email': ' test@example.com ', 'password': 'validpassword'}, follow_redirects=True)
    assert b'dashboard' in res.data.lower() or b'logout' in res.data.lower()

def test_L_9_multiple_login_attempts(client):
    for _ in range(5):
        client.post('/login', data={'email': 'test@example.com', 'password': 'wrong'})
    res = client.post('/login', data={'email': 'test@example.com', 'password': 'wrong'})
    assert b'Too many failed attempts' in res.data

def test_L_10_case_sensitivity(client):
    LOGIN_ATTEMPTS.clear()
    res = client.post('/login', data={'email': 'TEST@EXAMPLE.COM', 'password': 'validpassword'}, follow_redirects=True)
    assert b'dashboard' in res.data.lower() or b'logout' in res.data.lower()


# --- AI Matching Logic Test Cases ---

@pytest.fixture
def sample_college_program():
    college = {
        "id": 1,
        "name": "Tech University",
        "scholarship_available": True,
        "popularity_score": 80,
        "location": {"city": "Kathmandu", "district": "Kathmandu"}
    }
    program = {
        "id": 1,
        "name": "BSc Computer Science",
        "field": "CS",
        "fees": 500000,
        "gpa_requirement": 3.0,
        "description": "Tech program"
    }
    return program, college

def test_AI_01_perfect_match(sample_college_program):
    """AI-01 Perfect match -> Highest match score"""
    prog, coll = sample_college_program
    profile = {"gpa": 3.8, "max_fees": 600000, "preferences": ["Computer Science", "CS"], "location": "Kathmandu"}
    scores = compute_match_scores(profile, prog, coll)
    assert scores["compatibility_score"] > 90

def test_AI_02_low_gpa(sample_college_program):
    """AI-02 Low GPA -> Lower ranking"""
    prog, coll = sample_college_program
    profile = {"gpa": 2.0, "max_fees": 600000, "preferences": ["CS"], "location": "Kathmandu"}
    scores = compute_match_scores(profile, prog, coll)
    assert scores["gpa_score"] < 50

def test_AI_03_budget_mismatch(sample_college_program):
    """AI-03 Budget mismatch -> Score reduced"""
    prog, coll = sample_college_program
    profile = {"gpa": 3.5, "max_fees": 100000, "preferences": ["CS"], "location": "Kathmandu"}
    scores = compute_match_scores(profile, prog, coll)
    assert scores["budget_score"] < 100

def test_AI_04_subject_mismatch(sample_college_program):
    """AI-04 Subject mismatch -> Low ranking"""
    prog, coll = sample_college_program
    profile = {"gpa": 3.5, "max_fees": 600000, "preferences": ["Medical", "Biology"], "location": "Kathmandu"}
    scores = compute_match_scores(profile, prog, coll)
    assert scores["program_score"] == 0

def test_AI_05_location_match(sample_college_program):
    """AI-05 Location match -> Score increases"""
    prog, coll = sample_college_program
    profile_match = {"gpa": 3.5, "max_fees": 600000, "preferences": ["CS"], "location": "Kathmandu"}
    profile_miss = {"gpa": 3.5, "max_fees": 600000, "preferences": ["CS"], "location": "Pokhara"}
    score_match = compute_match_scores(profile_match, prog, coll)
    score_miss = compute_match_scores(profile_miss, prog, coll)
    assert score_match["location_score"] > score_miss["location_score"]

def test_AI_6_empty_user_profile(sample_college_program):
    """AI-6 Empty user profile -> No results or default"""
    prog, coll = sample_college_program
    scores = compute_match_scores({}, prog, coll)
    assert isinstance(scores["compatibility_score"], (int, float))

def test_AI_7_extreme_gpa(sample_college_program):
    """AI-7 Extreme GPA -> Should not break logic"""
    prog, coll = sample_college_program
    profile = {"gpa": 4.0, "max_fees": 600000}
    scores = compute_match_scores(profile, prog, coll)
    assert scores["gpa_score"] == 100

def test_AI_8_zero_budget(sample_college_program):
    """AI-8 Zero budget -> Default to 100 since user hasn't set a budget"""
    prog, coll = sample_college_program
    profile = {"gpa": 3.5, "max_fees": 0}
    scores = compute_match_scores(profile, prog, coll)
    assert scores["budget_score"] == 100 # No budget limit set

    prog_free = dict(prog, fees=0)
    scores_free = compute_match_scores(profile, prog_free, coll)
    assert scores_free["budget_score"] == 100

def test_AI_9_missing_college_data():
    """AI-9 Missing college data -> Skip or handle safely"""
    prog = {"name": "Test", "gpa_requirement": 3.0}
    coll = {"name": "Test College"}
    profile = {"gpa": 3.5}
    scores = compute_match_scores(profile, prog, coll)
    assert "compatibility_score" in scores

def test_AI_10_invalid_data_type(sample_college_program):
    """AI-10 Invalid data type -> Validation error/Handled safely"""
    prog, coll = sample_college_program
    profile = {"gpa": "invalid_string", "max_fees": "unknown"}
    scores = compute_match_scores(profile, prog, coll)
    assert scores["gpa_score"] < 100

def test_AI_11_match_reason_display(sample_college_program):
    prog, coll = sample_college_program
    profile = {"gpa": 3.5}
    scores = compute_match_scores(profile, prog, coll)
    reasons = " ".join(scores["match_reasons"])
    assert "Your GPA" in reasons or "meets" in reasons

def test_AI_12_scholarship_reason(sample_college_program):
    prog, coll = sample_college_program
    profile = {"gpa": 3.5, "wants_scholarship": True}
    scores = compute_match_scores(profile, prog, coll)
    reasons = " ".join(scores["match_reasons"])
    assert "scholarship" in reasons.lower()

def test_AI_13_minimum_gpa_requirement(sample_college_program):
    prog, coll = sample_college_program
    profile = {"gpa": 1.5}
    scores = compute_match_scores(profile, prog, coll)
    assert scores["compatibility_score"] == 0
    assert "minimum gpa" in " ".join(scores["match_reasons"]).lower()

def test_AI_14_engineering_requirement(sample_college_program):
    prog, coll = sample_college_program
    prog["field"] = "Engineering"
    profile = {"gpa": 2.0}
    scores = compute_match_scores(profile, prog, coll)
    assert scores["compatibility_score"] == 0

def test_AI_15_any_d_grade_exclusion(sample_college_program):
    """AI-15 Any D-grade blocks all results regardless of GPA"""
    from ai_matcher import get_ai_matches
    prog, coll = sample_college_program
    # We need real models or mock them for get_ai_matches
    # For now, let's just test that it returns an empty list if has_d_grades is True
    class MockObj:
        def __init__(self, data): self.data = data
        def to_dict(self, **kwargs): return self.data
        @property
        def field(self): return self.data.get('field')
        @property
        def name(self): return self.data.get('name')
        @property
        def gpa_requirement(self): return self.data.get('gpa_requirement')
        @property
        def location(self): 
            class Loc: 
                city='Kathmandu'; district='Kathmandu'
            return Loc()
        @property
        def logo_url(self): return ""

    user_profile = {"gpa": 4.0, "has_d_grades": True, "preferences": ["CS"], "location": "Kathmandu"}
    class MockUser:
        def get_profile_dict(self): return user_profile
    
    matches = get_ai_matches(MockUser(), programs_data=[(MockObj(prog), MockObj(coll))])
    assert len(matches) == 0

def test_AI_16_zero_gpa_exclusion(sample_college_program):
    """AI-16 GPA of 0 blocks all matches"""
    from ai_matcher import get_ai_matches
    prog, coll = sample_college_program
    class MockObj:
        def __init__(self, data): self.data = data
        def to_dict(self, **kwargs): return self.data
        @property
        def field(self): return self.data.get('field')
        @property
        def name(self): return self.data.get('name')
        @property
        def gpa_requirement(self): return self.data.get('gpa_requirement')
        @property
        def location(self): 
            class Loc: 
                city='Kathmandu'; district='Kathmandu'
            return Loc()
        @property
        def logo_url(self): return ""

    user_profile = {"gpa": 0, "preferences": ["CS"], "location": "Kathmandu"}
    class MockUser:
        def get_profile_dict(self): return user_profile
    
    matches = get_ai_matches(MockUser(), programs_data=[(MockObj(prog), MockObj(coll))])
    assert len(matches) == 0