# Education Navigator — Work Distribution & Team Roles

**Team Size**: 5 members  
**Project**: Education Navigator (College Discovery Platform)  
**Duration**: Academic Project

---

## Team Roster & Responsibilities

### **Member 1: Full-Stack Lead / Backend Architect**
**Role**: Lead Backend Developer + Database Designer  
**Name**: *[Assign a team member]*

#### Responsibilities
- **Backend Architecture**:
  - Design and maintain Flask application structure
  - Create and maintain SQLAlchemy ORM models
  - Implement database schema and migrations
  - Optimize database queries and indexing
  - Implement API endpoints and authentication

- **Database**:
  - Database design and normalization
  - SQLite setup and optimization
  - Data validation and integrity checks
  - Backup and recovery procedures

- **Features Owned**:
  - User authentication (login/register)
  - User profile management (`/profile`, `/api/profile`)
  - Database seed and import scripts
  - Fee data parsing from Excel (`load_university_fees()`)
  - College data API endpoints

- **Code Ownership**:
  - `app.py` (main Flask app, models, routes)
  - `scripts/` directory
  - Database schema design
  - Backend API structure

#### What They'll Present in Q&A
- Database architecture and why we chose relational model
- How data flows from JSON/Excel into the database
- Authentication & authorization approach
- Performance optimizations (indexing, caching)
- Scalability considerations (how to handle 1000s of colleges)
- Challenging issues faced during backend implementation

---

### **Member 2: Frontend Lead / UI/UX Developer**
**Role**: Lead Frontend Developer + Designer  
**Name**: *[Assign a team member]*

#### Responsibilities
- **Frontend Architecture**:
  - Responsive design and CSS styling
  - Jinja2 template structure
  - Client-side JavaScript logic
  - Component-based template organization
  - Theme system (light/dark mode toggle)

- **Pages & Templates Owned**:
  - `templates/index.html` (landing page)
  - `templates/colleges.html` (college listing with map)
  - `templates/compare.html` (side-by-side comparison)
  - `templates/dashboard.html` (user dashboard)
  - `templates/profile.html` (user profile editor)
  - Layout & navigation components

- **Features Owned**:
  - College search & filtering (client-side)
  - Leaflet.js map integration
  - College card UI design
  - Comparison table layout
  - Form styling and validation
  - Responsive breakpoints

- **Code Ownership**:
  - `static/css/style.css` (all styling)
  - `static/js/main.js` (common JS utilities)
  - `templates/` (HTML structure & Jinja)
  - `static/images/` (logos, icons)
  - CSS variables and theme configuration

#### Deliverables
- Pixel-perfect UI matching design specs
- Mobile-first responsive design
- Accessibility compliance (WCAG)
- Performance optimization (CSS/JS minification)
- Cross-browser testing (Chrome, Safari, Firefox)

#### What They'll Present in Q&A
- Design decisions and responsive strategy
- How we achieved interactive filters on 100+ colleges
- Map integration challenges
- Performance optimization techniques
- Accessibility considerations
- Multi-device testing approach

---

### **Member 3: AI & Features Developer**
**Role**: AI Matching Engine + Feature Implementation  
**Name**: *[Assign a team member]*

#### Responsibilities
- **AI Recommendation Engine**:
  - Design and implement scoring algorithm
  - Maintain `ai_matcher.py`
  - User profile parsing
  - Recommendation ranking logic
  - Testing algorithm accuracy

- **Features Owned**:
  - AI match recommendations (`/api/ai-match`)
  - Recommendation results page (`templates/ai_match.html`)
  - Resume parser (simulated extraction)
  - Match reason explanations
  - Student profile handling

- **Algorithm Details**:
  - GPA compatibility scoring (35% weight)
  - Budget vs fees matching (25% weight)
  - Program preference matching (20% weight)
  - Scholarship availability factor (10% weight)
  - Location preference factor (10% weight)

- **Code Ownership**:
  - `ai_matcher.py`
  - `templates/ai_match.html`
  - `/api/ai-match` endpoint logic
  - `/api/upload_resume` endpoint (resume parsing)
  - Scoring tests and validation

#### What They'll Present in Q&A
- Algorithm design choices and why those weights?
- How accuracy is measured
- Edge cases (no match data, invalid profiles)
- Potential for machine learning integration
- User feedback on recommendation quality
- Real vs simulated AI (transparency with users)

---

### **Member 4: Data & Integration Developer**
**Role**: Data Management + Utilities  
**Name**: *[Assign a team member]*

#### Responsibilities
- **Data Pipeline**:
  - Manage college data sources (JSON files)
  - Excel parsing for fee information
  - Data validation and cleaning
  - Data import/export utilities
  - Scholarship and event data management

- **Scripts & Tools**:
  - `scripts/recreate_db.py` (database reset)
  - `scripts/seed_scholarships.py` (populate scholarships)
  - `scripts/import_events.py` (load events)
  - `scripts/advanced_import.py` (advanced data import)
  - `fetch_logos.py` (college logo web scraper)

- **Features Owned**:
  - Scholarship board (`/scholarships`)
  - Event calendar (`/events`)
  - Exam preparation info (`/exams`)
  - College logo fetching and display
  - Entrance exam data management

- **Data Sources**:
  - `data/colleges.json`
  - `data/events.json`
  - `data/scholarships.json`
  - `data/universities.json`
  - `data/hostels.json`
  - `data/University Fees.xlsx`

- **Code Ownership**:
  - `scripts/` directory
  - `data/` directory and JSON structures
  - `fetch_logos.py`
  - Web scraping utilities
  - Data validation functions
  - Import/export logic

#### What They'll Present in Q&A
- Data collection and validation process
- Challenges with data quality from multiple sources
- Logo fetching challenges (web scraping)
- How we handle data updates and versioning
- Scalability of data pipeline (1000s of colleges)
- API integrations options (if any)

---

### **Member 5: Backend Developer - Advanced Features & Optimization**
**Role**: Backend Engineer (Advanced Features, Performance, Security)  
**Name**: *[Assign a team member]*

#### Responsibilities
- **Advanced Backend Features**:
  - Implement complex business logic
  - Handle edge cases and error scenarios
  - Build advanced filtering and search capabilities
  - Implement caching strategies
  - Optimize database queries

- **Performance & Optimization**:
  - Database query optimization and indexing
  - API response time optimization
  - Implement pagination for large datasets
  - Caching layer (Redis/in-memory)
  - Load time optimization

- **Security & Validation**:
  - Input validation and sanitization
  - SQL injection prevention
  - Authentication & authorization enhancements
  - CORS configuration
  - Rate limiting and abuse prevention

- **Features Owned**:
  - Advanced AI matching optimizations
  - Search algorithm improvements
  - Bulk data import/export functionality
  - API performance enhancements
  - Database optimization

- **Code Ownership**:
  - `app.py` (shared with Member 1, focus on advanced features)
  - Performance-critical routes and endpoints
  - Caching logic and optimization
  - Security middleware
  - Advanced query builders and ORM optimizations

#### What They'll Present in Q&A
- Performance bottlenecks identified and optimizations applied
- Caching strategies implemented
- Database optimization techniques used
- Security measures and vulnerability prevention
- Scalability considerations for handling more colleges/users
- Complex features: search algorithm, matching optimization

---

## Collaboration Framework

### **Code Organization**

| Component | Owner | Collaborators | Review By |
|-----------|-------|---------------|-----------|
| `app.py` | Member 1 | Member 3, 4 | Member 5 |
| `ai_matcher.py` | Member 3 | Member 1 | Member 5 |
| `templates/` | Member 2 | All | Member 5 |
| `static/css/` | Member 2 | All | Member 5 |
| `static/js/` | Member 2 | Member 1 | Member 5 |
| `scripts/` | Member 4 | Member 1 | Member 5 |
| `data/` | Member 4 | All (data sources) | Member 5 |
| `fetch_logos.py` | Member 4 | Member 2 (UI) | Member 1 |
| Performance/Optimization | Member 5 | Member 1 | Member 1 |

### **Weekly Sync Points**

- **Monday 10am**: Sprint planning & blockers
- **Wednesday 3pm**: Mid-week check-in & demo
- **Friday 5pm**: Demo to stakeholders + retrospective

### **Communication Channels**

- **Slack**: Daily updates, quick questions
- **GitHub Issues**: Feature requests, bugs
- **GitHub PRs**: Code review (all members review)
- **Shared Docs**: Google Docs for specs, notes

### **Git Workflow**

1. Create feature branch: `git checkout -b feature/college-search`
2. Make commits with clear messages
3. Open PR with description & testing notes
4. At least 1 code review approval required
5. Merge to main after approval
6. Deploy from main branch

---

## Key Metrics & Success Criteria

### **By Member**

**Member 1 (Backend Lead)**
- ✅ All CRUD endpoints working
- ✅ Database queries optimized (< 500ms)
- ✅ Zero data loss on production
- ✅ Authentication secure & tested

**Member 2 (Frontend Lead)**
- ✅ All pages responsive on mobile
- ✅ Page load time < 3 seconds
- ✅ 95+ Lighthouse accessibility score
- ✅ Works on Chrome, Safari, Firefox

**Member 3 (AI Developer)**
- ✅ Recommendations match user expectations
- ✅ Algorithm tested with 100+ sample profiles
- ✅ Match reasons clearly explain scores
- ✅ Edge cases handled gracefully

**Member 4 (Data Developer)**
- ✅ All data sources successfully imported
- ✅ Data accuracy verified for 50+ colleges
- ✅ Logo fetch success rate > 80%
- ✅ No data duplication issues

**Member 5 (Backend Optimization)**
- ✅ Database queries optimized (< 500ms)
- ✅ Caching strategy implemented
- ✅ API response times < 200ms
- ✅ Security vulnerabilities addressed

---

## Feature Ownership Matrix

| Feature | Primary Owner | Secondary Support | Tested By |
|---------|---------------|-------------------|-----------|
| User Auth | Member 1 | Member 5 | Member 1 |
| College Search | Member 2 | Member 5 | Member 1 |
| Map View | Member 2 | - | Member 2 |
| Compare Tool | Member 2 | Member 1 | Member 1 |
| AI Matching | Member 3 | Member 5 | Member 1 |
| Scholarships | Member 4 | Member 2 | Member 1 |
| Events | Member 4 | Member 2 | Member 1 |
| Exams | Member 4 | Member 3 | Member 1 |
| Logo Display | Member 4 | Member 2 | Member 1 |
| Dashboard | Member 1 | Member 2 | Member 1 |
| CV Tools | Member 1 | Member 2 | Member 1 |

---

## Presentation Assignment Summary

| Slide | Topic | Presenter | Time |
|-------|-------|-----------|------|
| 1 | Problem Statement - College Selection Crisis | **Member 1** | 1 min |
| 2 | Existing Solutions & Gaps | **Member 1** | 30 sec |
| 3 | Our Solution Overview | **Member 2** | 1.5 min |
| 4 | System Architecture & Tech Stack | **Member 1** | 1 min |
| 5a | Feature Demo: College Search & Map | **Member 2** | 2 min |
| 5b | Feature Demo: Comparison & AI Match | **Member 3** | 2 min |
| 5c | Feature Demo: Dashboard & Recommendations | **Member 4** | 1.5 min |
| 5d | Performance & Optimization Showcase | **Member 5** | 1 min |
| 6 | Learning Outcomes & Technical Challenges | **All members** | 1 min |
| 7 | Q&A (Team Discussion) | **All members** | 3 min |

---

## What Each Member Should Know

### **Member 1 Expertise Areas**
- Blueprint of entire backend
- Why we chose SQLite (and when to migrate to PostgreSQL)
- Database normalization and relationship design
- ORM best practices
- API design principles
- How to scale from 100 to 100,000 colleges

### **Member 2 Expertise Areas**
- Responsive design techniques
- CSS architecture (variables, media queries)
- JavaScript DOM manipulation
- Leaflet.js integration
- Accessibility standards (WCAG)
- Performance optimization (CLS, LCP, FID)
- Browser compatibility matrix

### **Member 3 Expertise Areas**
- Scoring algorithm logic and weights
- Statistical analysis of matches
- How to improve accuracy
- Edge cases in recommendations
- Future pivot to machine learning
- A/B testing strategies for algorithm

### **Member 4 Expertise Areas**
- Data pipeline architecture
- Web scraping ethics and practices
- JSON schema design
- Data validation patterns
- ETL processes
- Master data management

### **Member 5 Expertise Areas**
- Database optimization and indexing strategies
- Query performance analysis and tuning
- Caching patterns and implementation (Redis, in-memory)
- API performance optimization
- Security best practices and vulnerability prevention
- Load testing and scalability analysis

---

## Onboarding New Team Members

1. **First day**: Read this document + `TECHNICAL_DOCUMENTATION.md`
2. **Second day**: Setup local dev environment (see `README.md`)
3. **Third day**: Get code review from primary owner of assigned feature
4. **First week**: Make first PR (small fix or feature)
5. **First month**: Take ownership of a small feature end-to-end

---

## Escalation Path

**Issue Type** → **Primary Owner** → **Escalate to** → **Final Decision**

- Backend bug → Member 1 → Member 5 → Lead
- Frontend bug → Member 2 → Member 1 → Lead
- Algorithm issue → Member 3 → Member 1 → Lead
- Data issue → Member 4 → Member 1 → Lead
- Performance issue → Member 5 → Member 1 → Lead

---

**Document Version**: 1.0  
**Last Updated**: March 2026  
**Maintained by**: Team Lead (Member 1)

*This document should be updated at the beginning of each sprint.*
