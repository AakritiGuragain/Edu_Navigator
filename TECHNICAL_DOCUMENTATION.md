# Education Navigator — Complete Technical Documentation

**Version**: 1.0  
**Date**: March 2026  
**Team Size**: 5 members  
**Status**: Active Development

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [User Journey](#user-journey)
3. [Tech Stack](#tech-stack)
4. [Database Schema](#database-schema)
5. [System Architecture](#system-architecture)
6. [Key Features](#key-features)
7. [Data Flow](#data-flow)
8. [API Reference](#api-reference)
9. [Deployment & Setup](#deployment--setup)

---

## Project Overview

**Education Navigator** is a web platform built for Nepali students to discover, compare, and choose colleges. The app combines college directory functionality with AI-powered recommendations, interactive maps, and direct comparison tools to help students make informed decisions about higher education.

### Core Value Proposition
- **Centralized discovery**: One platform to find all college information in Nepal
- **Data richness**: Fees, programs, facilities, hostel info, location, affiliation, scholarships
- **Intelligent matching**: AI-powered recommendations based on student profile (GPA, budget, preferences)
- **Comparison tools**: Side-by-side college analysis
- **Geospatial features**: Map-based college discovery with virtual tour links

### Target Users
- High school students (12th grade) in Nepal and abroad
- International students interested in Nepali colleges
- Parents and counselors assisting in college selection

---

## User Journey

### 1. **Landing & Home Page** (`/`)
- Unauthenticated users see:
  - Landing hero section with CTAs
  - Featured colleges carousel
  - Top scholarship opportunities
  - Quick statistics (total colleges, scholarships, events)
- Navigation: Institutions, AI Match, Exams, Resources

### 2. **Discovery & Browsing** (`/colleges`)
- User arrives at institution listing page
- **Features**:
  - Map view (Leaflet.js) showing college locations across Nepal
  - Search box for college/program names
  - Location filter (by district/city)
  - Grid card display with:
    - College name, type (Government/Private), affiliation
    - Key programs (up to 4)
    - Fee ranges
    - Hostel availability badge
    - "View on Map" and "Compare" buttons
- **Interactions**:
  - Click college card → detailed info
  - Select up to 3 colleges → "Compare Now" sticky bar appears
  - Filter by location → map re-renders

### 3. **AI-Powered Matching** (`/ai-match`)
- User logs in or provides profile info
- Profile includes: GPA, location preference, budget (max fees), subject interests
- AI matcher runs rule-based algorithm:
  - GPA compatibility (35%)
  - Budget match vs fees (25%)
  - Subject preference match (20%)
  - Scholarship availability (10%)
  - Location match (10%)
- Displays ranked programs with:
  - Match score
  - Match reasons ("Your GPA qualifies", "Scholarship available", etc.)
  - College details and link to detailed view

### 4. **Side-by-Side Comparison** (`/compare`)
- User selects up to 3 colleges to compare
- Table displays:
  - College logos (if available), name, image
  - Location & affiliation
  - Institution type
  - Fee ranges
  - Hostel facilities
  - Top programs (up to 4)
  - Remove button per college
- User can go back to browsing to add/remove colleges

### 5. **College Detail View** (on `/colleges` or modal)
- Full college profile:
  - Description, website, contact info
  - Full program list with fees and entrance exam requirements
  - Hostel info (capacity, monthly fee, gender, meals, amenities)
  - Scholarship details
  - Facilities (library, labs, WiFi, sports, etc.)
  - "Virtual Tour" link (opens Google Street View)

### 6. **User Dashboard** (`/dashboard`) — *After Login*
- Personalized profile dashboard:
  - Saved colleges (favorites/watchlist)
  - AI match recommendations
  - Saved comparison lists
  - Recent activity
  - Profile settings (GPA, budget, location, preferences)

### 7. **Additional Resources**
- **Scholarship Board** (`/scholarships`): Filterable scholarship listings
- **Events** (`/events`): Upcoming college fairs, entrance exams, webinars
- **Exam Prep** (`/exams`): IOE, CMAT, KUUMAT exam info with syllabus links
- **CV Builder** (`/cv_builder`): Template-based CV creation tool
- **Chat Widget** (visible on all pages): AI chat for answering student questions

---

## Tech Stack

### **Frontend**
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Markup** | Jinja2 HTML | Server-side template rendering |
| **Styling** | Custom CSS (SCSS compiled) | Responsive design, light/dark theme toggle |
| **Interaction** | Vanilla JavaScript | DOM manipulation, client-side filtering, form handling |
| **Maps** | Leaflet.js + OpenStreetMap | Interactive college location map |
| **Icons/Typography** | Google Fonts (DM Sans) | Font delivery & custom icons (Unicode) |

### **Backend**
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Flask | Lightweight web framework |
| **Server** | Werkzeug (built-in) | WSGI server |
| **ORM** | SQLAlchemy | Database abstraction layer |
| **Auth** | Flask-Login | Session management & user authentication |
| **Forms** | Flask-WTF + WTForms | Form validation & CSRF protection |
| **Security** | Werkzeug | Password hashing (pbkdf2), secure file upload |

### **Database**
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Database Engine** | SQLite 3 | Lightweight, file-based SQL database |
| **Connection Pool** | SQLAlchemy | Efficient DB connection management |
| **Location** | `instance/education_navigator.db` | Persistent data storage |

### **Data Processing**
| Tool | Purpose |
|------|---------|
| **Python 3.8+** | Backend runtime |
| **openpyxl** | Excel parsing (University Fees.xlsx) |
| **requests** | HTTP requests (optional, for logo fetching) |
| **beautifulsoup4** | HTML parsing (optional, for web scraping) |

### **Deployment**
| Component | Technology |
|-----------|-----------|
| **Local Dev** | Flask development server (`flask run` or `python app.py`) |
| **Port** | 5001 (configurable) |
| **Host** | 127.0.0.1 / 0.0.0.0 (configurable) |

---

## Database Schema

### **ER Diagram Overview**
```
┌─────────────┐        ┌──────────────┐        ┌──────────────┐
│   User      │        │   College    │────────│  Location    │
│             │        │              │        │              │
│  id (PK)    │        │  id (PK)     │        │  id (PK)     │
│  username   │        │  name        │        │  college_id  │
│  email      │        │  type        │        │  city        │
│  password   │        │  affiliation │        │  district    │
│  profile    │        │  pop_score   │        │  latitude    │
│             │        │              │        │  longitude   │
└─────────────┘        └──────────┬───┘        └──────────────┘
                                  │
                         ┌────────┴──────┐
                         │               │
                    ┌────▼────────┐  ┌──▼───────────┐
                    │   Program   │  │    Hostel    │
                    │             │  │              │
                    │  id (PK)    │  │  id (PK)     │
                    │  college_id │  │  college_id  │
                    │  name       │  │  available   │
                    │  fees       │  │  capacity    │
                    │  entrance   │  │  monthly_fee │
                    └─────────────┘  └──────────────┘

┌─────────────────┐      ┌──────────────┐
│   Scholarship   │      │    Event     │
│                 │      │              │
│  id (PK)        │      │  id (PK)     │
│  title          │      │  title       │
│  provider       │      │  start_date  │
│  description    │      │  location    │
│  deadline       │      │  description │
│  amount         │      │              │
└─────────────────┘      └──────────────┘

┌──────────────────┐
│   CVTemplate     │
│                  │
│  id (PK)         │
│  name            │
│  filename        │
│  uploaded_by     │
│  description     │
└──────────────────┘
```

### **Detailed Table Definitions**

#### **User**
```sql
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR(150) UNIQUE NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password_hash VARCHAR(256) NOT NULL,
  profile TEXT DEFAULT '{}'  -- JSON: {preferences, location, max_fees, gpa, etc.}
);
```

#### **College**
```sql
CREATE TABLE college (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(200) NOT NULL,
  full_name VARCHAR(300),
  short_name VARCHAR(50),
  type VARCHAR(50),  -- "Government", "Private", "Autonomous", etc.
  affiliation VARCHAR(200),  -- "TU", "KU", "PU", etc.
  established_year INTEGER,
  description TEXT,
  scholarship_available BOOLEAN DEFAULT 0,
  image_url VARCHAR(500),
  virtual_tour_url VARCHAR(500),
  logo_url VARCHAR(500),
  website VARCHAR(200),
  phone VARCHAR(50),
  email VARCHAR(100),
  popularity_score INTEGER DEFAULT 0,  -- 0-100
  total_students INTEGER,
  is_verified BOOLEAN DEFAULT 1
);
```

#### **Location**
```sql
CREATE TABLE location (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  college_id INTEGER NOT NULL UNIQUE,
  address VARCHAR(300),
  city VARCHAR(100),
  district VARCHAR(100),
  province VARCHAR(100),
  latitude FLOAT,
  longitude FLOAT,
  FOREIGN KEY (college_id) REFERENCES college(id) ON DELETE CASCADE
);
```

#### **Program**
```sql
CREATE TABLE program (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(200) NOT NULL,
  college_id INTEGER NOT NULL,
  description TEXT,
  duration VARCHAR(50),  -- "4 Years", "2 Years", etc.
  fees FLOAT,  -- in NPR
  gpa_requirement FLOAT,
  field VARCHAR(100),  -- "Engineering", "Management", "IT", etc.
  entrance_required BOOLEAN DEFAULT 0,
  entrance_exam VARCHAR(200),  -- "IOE", "CMAT", etc.
  FOREIGN KEY (college_id) REFERENCES college(id) ON DELETE CASCADE
);
```

#### **Hostel**
```sql
CREATE TABLE hostel (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  college_id INTEGER NOT NULL UNIQUE,
  available BOOLEAN DEFAULT 0,
  on_campus BOOLEAN DEFAULT 1,
  capacity INTEGER,
  monthly_fee FLOAT,
  gender VARCHAR(50),  -- "Male", "Female", "Both"
  meals_included BOOLEAN DEFAULT 0,
  amenities TEXT,  -- Comma-separated list
  FOREIGN KEY (college_id) REFERENCES college(id) ON DELETE CASCADE
);
```

#### **Scholarship**
```sql
CREATE TABLE scholarship (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(200) NOT NULL,
  provider VARCHAR(200),
  description TEXT,
  deadline DATETIME,
  amount VARCHAR(100),
  eligibility TEXT,
  apply_link VARCHAR(500),
  is_active BOOLEAN DEFAULT 1,
  category VARCHAR(50)  -- "Government", "International", "Private"
);
```

#### **Event**
```sql
CREATE TABLE event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  start_date DATETIME,
  end_date DATETIME,
  location VARCHAR(300),
  event_type VARCHAR(50),  -- "College Fair", "Exam", "Webinar"
  registration_link VARCHAR(500),
  is_active BOOLEAN DEFAULT 1
);
```

#### **CVTemplate**
```sql
CREATE TABLE cv_template (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(200) NOT NULL,
  filename VARCHAR(200) NOT NULL,
  description TEXT,
  uploaded_by INTEGER NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (uploaded_by) REFERENCES user(id)
);
```

---

## System Architecture

### **High-Level Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (BROWSER)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  HTML (Jinja2) + CSS + Vanilla JavaScript            │   │
│  │  - College cards, filters, map (Leaflet)             │   │
│  │  - Compare table, AI match results                   │   │
│  │  - Forms (login, profile, upload)                    │   │
│  │  - City/district search & location filter            │   │
│  │  - Chat widget (WebSocket optional)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         │ JSON (API), HTML (pages)
┌────────────────────────▼────────────────────────────────────┐
│               FLASK SERVER (BACKEND)                         │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Routes & Views                                      │   │
│  │ -----------                                         │   │
│  │ GET  /                    → index (landing)        │   │
│  │ GET  /colleges            → college listing page   │   │
│  │ GET  /compare?ids=...     → comparison table       │   │
│  │ GET  /ai-match            → AI match results       │   │
│  │ GET  /dashboard           → user dashboard         │   │
│  │ POST /api/ai-match        → recommendation engine  │   │
│  │ GET  /api/compare         → college comparison API │   │
│  │ POST /api/upload_resume   → resume parsing         │   │
│  │ POST /register, /login    → authentication         │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ▲                                    │
│                         │ calls                              │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Business Logic                                      │   │
│  │ ────────────────                                    │   │
│  │ • ai_matcher.py (scoring algorithm)                │   │
│  │ • College search & filtering                       │   │
│  │ • Fee calculation from Excel                       │   │
│  │ • User profile management                          │   │
│  │ • Authentication & authorization                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ▲                                    │
│                         │ SQLAlchemy                         │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ SQLAlchemy ORM Models                               │   │
│  │ ──────────────────────                              │   │
│  │ User, College, Location, Program, Hostel,           │   │
│  │ Scholarship, Event, CVTemplate                      │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL queries
                         │
┌────────────────────────▼────────────────────────────────────┐
│              SQLITE DATABASE                                 │
│  (instance/education_navigator.db)                          │
│                                                              │
│  Tables:                                                    │
│  • user (authentication & profiles)                        │
│  • college (main data)                                    │
│  • location (geo-coordinates)                             │
│  • program (degree offerings)                             │
│  • hostel (bunk & facility info)                          │
│  • scholarship (opportunities)                            │
│  • event (fairs, exams, webinars)                         │
│  • cv_template (user uploads)                             │
└─────────────────────────────────────────────────────────────┘
```

### **Data Flow: Request → Response**

1. **User navigates to `/colleges`**
   - Browser sends `GET /colleges`
   - Flask routes to `colleges()` view function

2. **View function execution**
   - Queries `College.query.order_by(College.name).all()`
   - Converts each college to dict with `to_dict(include_programs=True)`
   - Loads Excel fee data via `load_university_fees()`
   - Passes JSON-serialized data to template: `render_template('colleges.html', colleges_json=..., fees_json=...)`

3. **Template rendering**
   - Jinja2 renders HTML structure
   - Passes `colleges_json` to client-side JS as `<script>`

4. **Client-side JS rendering**
   - Parses `collegesData` JSON array
   - Builds college cards dynamically with `renderColleges()`
   - Attaches event handlers (search, filter, compare)
   - Initializes Leaflet map with college coordinates

5. **Filtering/search** (client-side)
   - User types in search box or changes location filter
   - JS calls `filterDynamicColleges()` (debounced)
   - Re-renders subset of colleges based on filters

6. **Comparison flow**
   - User clicks "Add to Compare" on up to 3 colleges
   - JS maintains `compareList` array
   - Shows sticky "Compare Now" bar
   - Redirects to `/compare?ids=1,5,18`

7. **Compare page**
   - Backend fetches `/api/compare?ids=1,5,18`
   - Returns JSON with college details
   - Frontend renders comparison table

---

## Key Features

### 1. **College Search & Discovery**
- **Search by name or program**: Real-time client-side filtering
- **Location filter**: Filter by district/city
- **Map view**: Interactive Leaflet.js map showing college pins
- **Card display**: Organized grid with key info (fees, type, programs)
- **Responsive**: Works on mobile, tablet, desktop

**Implementation**:
- Backend: `/api/colleges` endpoint (optional, mostly client-side)
- Frontend: `filterDynamicColleges()` function in `colleges.html`

### 2. **Side-by-Side Comparison**
- Compare up to 3 colleges at once
- Table shows: location, affiliation, type, fees, hostel, programs
- Click "Remove" to swap colleges
- Sticky bar at bottom for easy access

**Implementation**:
- Backend: `/api/compare?ids=1,2,3` endpoint
- Frontend: `renderTable()` in `compare.html`

### 3. **Map View with Virtual Tours**
- Leaflet.js map displaying college locations
- Click marker → popup with college name, program count
- "View on Map" button focuses on college location
- Virtual tour link (Google Street View by default)

**Implementation**:
- Backend: Location coordinates in DB
- Frontend: `initMap()`, `focusMap()` in `colleges.html`

### 4. **AI-Powered Recommendations**
- Rule-based scoring algorithm in `ai_matcher.py`
- Scoring factors:
  - GPA match (35%)
  - Fee affordability (25%)
  - Program interest match (20%)
  - Scholarship availability (10%)
  - Location preference (10%)
- Returns ranked programs with explanations

**Implementation**:
```python
# In ai_matcher.py:
def compute_match_score(student_profile, program, college):
    score = 0
    reasons = []
    
    # GPA check
    if program.gpa_requirement <= student_gpa:
        score += 35
        reasons.append("Your GPA qualifies")
    
    # Fee affordability
    if program.fees <= student_budget:
        score += 25
        reasons.append("Fits your budget")
    
    # ... more logic
    return score, reasons
```

### 5. **College Logo Display** (Optional)
- Logos stored in `static/logos/<college_name>.png`
- Fallback to initials placeholder if not found
- Fetched via `fetch_logos.py` (web scraping)

**Implementation**:
- Backend: Optional logo file check
- Frontend: `<img>` with onerror fallback to CSS-generated initials

### 6. **Hostel & Facilities Info**
- Hostel availability, capacity, monthly fees
- Gender-specific info
- Meals included flag
- Specific amenities list

**Implementation**:
- Model: `Hostel` table with college foreign key
- Display in: college detail view, comparison table

### 7. **Scholarship Board**
- Filterable list of scholarships
- Provider, deadline, amount, eligibility
- Application link
- Active/inactive status

**Data source**: `scripts/seed_scholarships.py` or manual entry

### 8. **Event Calendar**
- Upcoming college fairs, entrance exams, webinars
- Searchable by type or date
- Registration link

**Data source**: `data/events.json` → `scripts/import_events.py`

### 9. **User Profile & Dashboard**
- Store GPA, budget, location preference, subject interests
- Saved colleges/programs
- AI recommendations
- Recent activity

**Implementation**:
- Profile stored as JSON in `User.profile` column
- Updated at `/profile` page

### 10. **Chat Widget**
- Visible on all pages
- Rule-based Q&A for common questions
- Can escalate to recommendation engine
- Saves conversation history in user profile

---

## Data Flow

### **College Data Lifecycle**

#### **1. Data Ingestion**
```
┌──────────────────────────┐
│  data/colleges.json      │  ← Source of truth (structured JSON)
│  data/events.json        │
│  data/scholarships.json  │
│  University Fees.xlsx    │  ← Excel with fee data
└──────────────────────────┘
         ▼
    (Run import script)
         ▼
┌──────────────────────────┐
│  SQLite Database         │  ← Normalized relational data
│  (education_navigator    │
│   .db)                   │
└──────────────┬───────────┘
               │
```

#### **2. Data Retrieval**
```
Browser Request (GET /colleges)
       ▼
Flask Route (@app.route('/colleges'))
       ▼
Query Database:
  • College.query.all()
  • Location joins
  • Program subqueries
  • Hostel data
       ▼
Load External Fee Data:
  • openpyxl reads University Fees.xlsx
  • Builds fee_data dictionary by college name
       ▼
Convert to JSON:
  • colleges_data = [c.to_dict() for c in colleges]
  • json.dumps(colleges_data)
       ▼
Render Template:
  • Jinja2 injects JSON as <script> var
       ▼
Browser receives HTML + embedded JSON
```

#### **3. Client-Side Processing**
```
JS parses collegesData JSON
       ▼
User types in search box
       ▼
filterDynamicColleges():
  • Loops through collegesData
  • Tests name match
  • Tests location match
  • Builds filtered array
       ▼
renderColleges(filtered):
  • Creates <div> for each college
  • Builds card HTML
  • Attaches event listeners
  • Renders to DOM
       ▼
User sees filtered results
```

#### **4. Data Update Flow**
```
User edits profile (GPA, budget, etc.)
       ▼
POST /api/profile
       ▼
Flask: update User.profile JSON field
       ▼
COMMIT to database
       ▼
Response: {"success": true, "profile": {...}}
       ▼
JS updates local state
       ▼
Next /api/ai-match call uses updated profile
```

---

## API Reference

### **Public Endpoints** (no auth required)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/` | Landing page | HTML |
| `GET` | `/colleges` | College listing | HTML (rendered) |
| `GET` | `/colleges/<id>` | College detail | HTML or JSON |
| `GET` | `/compare` | Comparison page | HTML (template) |
| `POST` | `/api/compare` | Get college data for comparison | JSON `[{college}, ...]` |
| `GET` | `/scholarships` | Scholarship listing | HTML |
| `GET` | `/events` | Event calendar | HTML |
| `GET` | `/exams` | Entrance exam info | HTML |
| `POST` | `/register` | User signup | Redirect to `/login` |
| `POST` | `/login` | User signin | Redirect to `/dashboard` |

### **Authenticated Endpoints** (require `@login_required`)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/dashboard` | User dashboard | HTML |
| `GET` | `/profile` | Edit profile | HTML (form) |
| `PUT` | `/api/profile` | Save profile updates | JSON `{success, profile}` |
| `POST` | `/ai-match` | AI recommendations page | HTML |
| `GET` | `/api/ai-match` | AI match recommendations | JSON `[{program, score, reasons}, ...]` |
| `POST` | `/api/upload_resume` | Parse resume | JSON `{extracted_fields}` |
| `POST` | `/upload_cv` | Upload CV template | Redirect to `/cv_templates` |
| `GET` | `/api/cv_templates` | List CV templates | JSON `[...]` |

### **Example API Responses**

**`GET /api/compare?ids=1,2,3`**
```json
[
  {
    "id": 1,
    "name": "IOE Pulchowk Campus",
    "type": "Government",
    "location": {
      "city": "Lalitpur",
      "district": "Lalitpur",
      "coordinates": {"lat": 27.671, "lng": 85.324}
    },
    "programs": [
      {
        "id": 10,
        "name": "BE Computer Engineering",
        "fees": 450000,
        "entrance_exam": "IOE Entrance"
      }
    ],
    "hostel": {
      "available": true,
      "capacity": 500,
      "monthly_fee": 5000
    }
  }
]
```

**`GET /api/ai-match`**
```json
[
  {
    "program_id": 15,
    "program_name": "BBA",
    "college_name": "Shankar Dev Campus",
    "score": 87,
    "reasons": [
      "Your GPA qualifies (3.5 ≥ 2.8)",
      "Fits your budget",
      "Popular program in management"
    ]
  }
]
```

---

## Deployment & Setup

### **Development Setup**

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd Education-Navigator
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or: venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python scripts/recreate_db.py
   python scripts/seed_scholarships.py
   python scripts/import_events.py
   ```

5. **Run application**
   ```bash
   python app.py
   # or: flask run --reload
   ```
   - Opens on `http://127.0.0.1:5001`

### **Production Deployment** (Recommended Approach)

1. **Use a production WSGI server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 app:app
   ```

2. **Use environment variables**:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=<strong-secret-key>
   ```

3. **Reverse proxy** (nginx):
   ```nginx
   server {
       listen 80;
       server_name yourdomain.np;
   
       location / {
           proxy_pass http://127.0.0.1:5001;
       }
   }
   ```

4. **SSL/TLS** (Let's Encrypt):
   ```bash
   certbot --nginx -d yourdomain.np
   ```

---

## Troubleshooting & Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Database locked | Multiple writers | Use WAL mode: `app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'timeout': 15}}` |
| Long page load | Large colleges JSON | Implement pagination or lazy loading |
| Excel parsing fails | Missing `openpyxl` | `pip install openpyxl` |
| Logo images not showing | Files not in `static/logos/` | Run `python fetch_logos.py` |
| Map doesn't render | Leaflet not loading | Check CDN URL in template |

---

## Performance Considerations

1. **Database Indexing**: Add indexes on frequently searched columns
   ```sql
   CREATE INDEX idx_college_name ON college(name);
   CREATE INDEX idx_location_city ON location(city);
   ```

2. **Caching**: Use Flask-Caching for expensive queries
   ```python
   cache.cached(timeout=3600)(get_all_colleges)
   ```

3. **Pagination**: For large college lists
   ```python
   colleges = College.query.paginate(page=1, per_page=20)
   ```

4. **Lazy loading**: Load programs on demand, not all at once

---

## Security Checklist

- [ ] Change default `SECRET_KEY` in production
- [ ] Use HTTPS/SSL
- [ ] Sanitize file uploads (already done with `secure_filename`)
- [ ] Validate user input on both client and server
- [ ] Use CSRF tokens in forms (Flask-WTF handles this)
- [ ] Hash passwords with Werkzeug (already done)
- [ ] Limit file upload size (already set to 10MB)
- [ ] Implement rate limiting on APIs
- [ ] Enable CORS only for trusted origins

---

## Future Enhancements

- [ ] Real SMS notifications for scholarship deadlines
- [ ] Integration with college APIs for live data
- [ ] Mobile app (React Native or Flutter)
- [ ] Advanced analytics (which colleges are most popular, etc.)
- [ ] Mentor matching (current students → prospective students)
- [ ] Video tour integration (host college webinars)
- [ ] Integration with entrance exam platforms
- [ ] Machine learning for better recommendations (beyond rule-based)

---

**Last Updated**: March 2026  
**Maintained by**: Education Navigator Dev Team
