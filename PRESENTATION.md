# Presentation Plan — Education Navigator

## ⏱️ Timing (Total: 15 minutes)

1. **Problem statement (business problem)** — 1:00
2. **Existing solutions or gap** — 0:30
3. **Your proposed solution (how it solves the problem)** — 1:30
4. **System architecture & tech stack** — 1:00
5. **Key features + demo** — 5:30
6. **Each member’s contribution / role** — 0:30
7. **Learning outcome** — 1:00
8. **Q&A** — 4:00

---

## 1. Problem statement (business problem) — 1:00
- Students in Nepal struggle to find and compare colleges, programs, fees, scholarships, and events across scattered sources.
- Existing resources are fragmented (websites, social media, word-of-mouth), making research slow and inconsistent.
- Students need a single platform to explore, compare, and plan their academic pathway.

---

## 2. Existing solutions or gap — 0:30
- There are portals and forums, but they often:
  - Lack personalization (one-size-fits-all recommendations)
  - Don’t integrate scholarships, events, and CV preparation
  - Require manual searching and a lot of scrolling

---

## 3. Your proposed solution (how it solves the problem) — 1:30
- **Education Navigator** is a web platform that consolidates colleges, programs, scholarships, and events in one place.
- Students create profiles (GPA, budget, interests, location) and get **personalized college recommendations**.
- The platform includes a **chat assistant**, **AI match engine**, **CV builder**, and **compare tool** to streamline decision-making.

---

## 4. System architecture and tech stack — 1:00
- **Backend:** Flask + SQLAlchemy + SQLite
- **Frontend:** Jinja2 templates + vanilla JS + CSS
- **AI Matching:** Rule-based scoring engine (`ai_matcher.py`) that uses GPA, budget, preferences, scholarships, and location
- **Data pipelines:** Import scripts for colleges/events/scholarships using JSON

### Architecture Diagram
```mermaid
graph TD
    A[User Browser] --> B[Flask App (app.py)]
    B --> C[Authentication (Flask-Login)]
    B --> D[Routes & APIs]
    D --> E[AI Matcher (ai_matcher.py)]
    D --> F[Templates (Jinja2)]
    D --> G[Static Files (CSS/JS)]
    E --> H[Database (SQLite)]
    H --> I[Models: User, College, Program, etc.]
    B --> J[Data Import Scripts]
    J --> K[JSON Data Sources (data/)]
    K --> H
```

---

## 5. Key features + demo — 5:30
### Key Features to Highlight
- **Personalized AI matching:** `ai_matcher.py` scores programs and surfaces match reasons
- **Chat assistant:** In-app AI chat (`/api/chat`) that remembers context and updates profile
- **College browsing:** Map + filters, compare view
- **Scholarships & events:** aggregated and searchable
- **CV builder + templates:** Upload and download resumes and templates

### Demo flow (suggested)
1. Register & login
2. Update profile (GPA, interests, budget)
3. Visit **AI Match** and show recommendations + match reasons
4. Open the **chat widget**, ask about schools/fees, show memory update
5. Show **Compare** view (pick 2-3 colleges)
6. Show **Scholarships** + **Events** pages

---

## 6. Each member’s contribution / role — 0:30
- Person A: Product planning & project coordination
- Person B: Backend APIs + database models
- Person C: Frontend UI/UX + templates
- Person D: AI matcher + chat assistant
- Person E: Data pipelines + seed/import tooling

---

## 7. Learning outcome — 1:00
- Delivered a full-stack product end-to-end (web app + backend + data pipelines)
- Gained experience with production-style web architecture (Flask, DB, auth, APIs)
- Built a small “AI” recommender that links user profile to data
- Improved collaboration through role-based division and documentation

---

## 8. Q&A — 4:00
- Be ready to answer:
  - How does the matching algorithm work?
  - Where could we plug in a real ML model/LLM?
  - How would you scale the platform (more data, users)?
  - What would you add next (mobile app, notifications, real-time updates)?
