# Work Distribution (5-Person Student Team — Technical Roles Only)

This doc outlines a recommended split of technical responsibilities for a 5-person university student team building Education Navigator. (No PM role; all technical work distributed among students.)

---

## 🏗️ Role 1: Backend Engineer (Core Platform)
**Focus:** Flask backend, database schema, API design, authentication.

**Key responsibilities**
- Maintain and extend `app.py` models and routes.
- Implement new API endpoints and secure existing ones.
- Manage database migrations and seed/import scripts.
- Unit-test core business logic (matcher, profile scoring).
- Optimize performance for queries and API responses.

---

## 🎨 Role 2: Frontend Engineer (UX/UI)
**Focus:** Templates, styling, frontend interactions, responsive layout.

**Key responsibilities**
- Build/maintain Jinja templates in `templates/`.
- Improve UI/UX and accessibility (form validation, layout).
- Implement search/filtering UX on pages like colleges and AI match.
- Enhance mobile/responsive experience and visual polish.
- Work with backend APIs to present data cleanly.

---

## 🤖 Role 3: AI/Matching Engineer
**Focus:** Matching engine, personalization, chat assistant.

**Key responsibilities**
- Maintain `ai_matcher.py` and matching scoring logic.
- Enhance chat assistant logic (`/api/chat`) and add memory features.
- Improve recommendation relevance using profile signals.
- Add support for advanced matching (e.g., program clustering, NLP). 
- Ensure match engine performs well at scale.

---

## 📊 Role 4: Data Engineer
**Focus:** Data pipelines, imports, seed data, and external integrations.

**Key responsibilities**
- Build/maintain import scripts (`scripts/advanced_import.py`, `scripts/import_events.py`).
- Curate and validate datasets in `data/` (colleges, events, scholarships).
- Automate data refresh workflows (e.g., scheduled imports, validation checks).
- Integrate external APIs or data sources (e.g., official college lists, events feeds).
- Ensure data quality and manage dataset versioning.

---

## 🔧 Role 5: Full-Stack Engineer (Integration & Deployment)
**Focus:** Bridging frontend/backend, deployment, testing, and cross-cutting concerns.

**Key responsibilities**
- Assist with API integration between frontend and backend.
- Set up deployment pipelines (e.g., basic Docker, Heroku, or local hosting).
- Write end-to-end tests and integration tests.
- Handle cross-cutting features like authentication flows, error handling.
- Coordinate code reviews and ensure consistent coding standards across the team.

---

## 🧩 Collaboration Notes
- Pair frontend/backend to define API contracts early.
- Use a shared Kanban board (e.g., GitHub Projects) to track tasks by role.
- Define clear “Definition of Done” for features (code + tests + docs + validation).
- Rotate code reviews to spread knowledge and avoid bottlenecks.
