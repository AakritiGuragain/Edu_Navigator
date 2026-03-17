# Education Navigator — Workflow & Architecture

## 🧭 What is this project?
Education Navigator is a Flask-based web platform designed for students in Nepal to explore colleges, programs, scholarships, events, and build a CV—all in one place. The app includes an AI-driven matching engine that recommends a personalized list of colleges/programs based on a student’s profile (GPA, budget, preferences, location, scholarship need).

---

## 🧱 Tech Stack

### Backend (Python)
- **Framework:** Flask (single `app.py` application entrypoint)
- **Database:** SQLite (via SQLAlchemy ORM)
- **Forms/Validation:** Flask-WTF + WTForms
- **Authentication:** Flask-Login
- **Security:** Werkzeug password hashing + secure filename handling for uploads

### Frontend
- **Templates:** Jinja2 HTML templates in `templates/`
- **Styling:** Custom CSS in `static/css/style.css`
- **JS:** Vanilla JS in `static/js/main.js` + per-page inline JS
- **Maps:** Leaflet.js (used on the college map page) – loaded from templates

### Data & Content
- **Seed/sample data:** Stored in JSON files under `data/` (colleges, events, scholarships, hostels, etc.)
- **File uploads:** Saved to `static/uploads/` (CV templates, resumes)

---

## 🗂️ Project Structure (High Level)

- `app.py` — main Flask app; defines models, routes, APIs, forms, and core business logic.
- `ai_matcher.py` — “AI” matching engine (rule-based scoring algorithm) used to recommend programs.
- `templates/` — UI pages (index, colleges, dashboard, chat widget, ai-match, etc.).
- `static/` — CSS, JS, images, uploads.
- `data/` — JSON data sources used for seed/import scripts.
- `scripts/` — utility scripts to reset DB, seed scholarships, import events, and import an advanced dataset.

---

## 🚀 How it Runs (Execution Flow)

### 1) Starting the app
- Run the app with:
  ```bash
  python app.py
  ```
- The app listens by default on `http://0.0.0.0:5001`.

### 2) Database setup + seeding
- On first request (before first request hook), the app creates the SQLite DB (`education_navigator.db`) and seeds
  sample colleges/programs via `seed_sample_colleges()`.
- The database lives under the default path configured in `app.config['SQLALCHEMY_DATABASE_URI']`.

### 3) Authentication & Profile
- Users register/login via `/register` and `/login`.
- Profile data is stored inside the `User.profile` JSON field (preferences, GPA, budget, location, scholarship need).
- Profile editing happens at `/profile` and updates the JSON field.

### 4) Pages + UI flows
- `/` — Home
- `/dashboard` — Personalized dashboard (requires login)
- `/colleges` (also `/institutions`) — Browse all colleges + programs
- `/ai-match` — AI-driven match list (calls `/api/ai-match`)
- `/scholarships` — Scholarship list (seeded via `scripts/seed_scholarships.py`)
- `/events` — Event board (seeded via `scripts/import_events.py`)
- `/cv_builder` — CV Builder UI
- `/upload_cv` — Upload a CV template (PDF/DOC/DOCX)

### 5) API Endpoints (key ones)
- `GET /api/colleges` — search/list colleges
- `GET /api/colleges/<id>` — college details
- `GET /api/programs` — program listing
- `GET /api/recommendations` — server-side recommendations for logged-in user
- `GET /api/ai-match` — AI match engine (returns ranked results + reasons)
- `POST /api/chat` — chat widget backend
- `POST /api/upload_resume` — resume parser stub (simulated extraction)

---

## 🤖 Key Feature: AI Matching Engine

The “AI” in this project is implemented in `ai_matcher.py`.

### How it works
1. It collects student profile data from `User.profile` (GPA, preferences, budget, location, scholarship need).
2. It computes compatibility scores for each program in the database using rule-based scoring:
   - GPA match (35%)
   - Budget vs fees (25%)
   - Program/field preference match (20%)
   - Scholarship availability (10%)
   - Location preference (10%)
3. It returns a sorted list of programs with score and “match reasons”.

### Used by
- `/api/ai-match` (full reasons list)
- `get_recommendations()` in `app.py` (limited results for dashboard)

---

## 🔧 Data Import / Maintenance Scripts

| Script | Purpose | How to run |
|---|---|---|
| `scripts/recreate_db.py` | Drops/creates SQLite DB schema from models | `python scripts/recreate_db.py` |
| `scripts/seed_scholarships.py` | Seeds sample scholarships table | `python scripts/seed_scholarships.py` |
| `scripts/import_events.py` | Imports events from `events.json` into DB | `python scripts/import_events.py` |
| `scripts/advanced_import.py` | Imports a master college dataset (`data/colleges_master.json` expected) into DB | `python scripts/advanced_import.py` |

---

## 📦 Adding / Updating Content

### Colleges & Programs
- By default, the app seeds a small sample list of colleges/programs via `seed_sample_colleges()`.
- To import real data, use `scripts/advanced_import.py` against a `data/colleges_master.json` dataset.

### Events
- Events are loaded from `events.json` using `scripts/import_events.py`.

### Scholarships
- Scholarships are created via `scripts/seed_scholarships.py`.

---

## 🧪 Development Notes

- The app uses **Flask’s debug mode** when run directly (`app.run(debug=True)` in `app.py`).
- Uploaded files (CVs) are stored under `static/uploads/`.
- The chat widget saves conversation context into the user’s profile JSON (`chat_history`).
- The AI matcher and chat logic are intentionally rule-based to avoid external API dependencies.

---

## 🛠️ How to Extend / Customize

### Add a new feature (example)
1. Add a new model in `app.py` (follow SQLAlchemy style).
2. Create a new database migration (or re-create DB during development).
3. Add a route + template under `templates/`.
4. Connect it to the front-end via navigation in templates, or add API endpoints.

### Add a new data source
1. Add JSON to `data/`.
2. Write a script in `scripts/` to import it.
3. Run the script to populate the DB.

---

## 📌 Where to Look First
- `app.py` — app setup, routes, models, match engine hooks
- `ai_matcher.py` — scoring logic & recommendation engine
- `templates/` — UI pathways and components (especially `chat_widget.html`)
- `static/` — styling + theme toggle + small UI helpers
- `scripts/` — data seeding / import utilities

---

## 🔗 Endpoint → Template Wiring (Page Flow)
This section maps the main **Flask routes** to the **templates** they render, so you can quickly trace which UI page is backed by which endpoint.

- `/` → `templates/index.html` (home)
- `/dashboard` → `templates/dashboard.html` (user dashboard)
- `/colleges` (also `/institutions`) → `templates/colleges.html` (college list + map)
- `/ai-match` → `templates/ai_match.html` (AI matcher UI)
- `/scholarships` → `templates/scholarships.html` (scholarship list)
- `/events` → `templates/events.html` (events board)
- `/exams` → `templates/exams.html`, `/exams/<exam_type>` → `templates/exam_detail.html`
- `/profile` → `templates/profile.html` (edit user profile)
- `/login` → `templates/login.html` and `/register` → `templates/register.html`
- `/cv_builder` → `templates/cv_builder.html`, `/upload_cv` → `templates/upload_cv.html`
- `/compare` → `templates/compare.html` (uses `/api/compare` for data)

> Most pages include the `templates/chat_widget.html` include for the AI chat sidebar widget.

---

If you'd like, I can also generate a simplified architecture diagram or add a short section describing how pages are wired together (e.g., which endpoints feed which templates).
