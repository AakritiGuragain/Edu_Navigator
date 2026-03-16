# Education Navigator

Education Navigator is a comprehensive web platform designed to simplify the college selection process for students in Nepal. It provides a centralized hub to explore top colleges, compare academic programs, discover scholarship opportunities, and even construct a professional CV directly within the browser.

## Features

- **Dynamic Colleges & Programs Directory**: Browse a curated list of top colleges in Nepal. Explore detailed information on institutions, their locations, facilities, and the programs they offer.
- **Interactive Map**: View colleges on an interactive map using Leaflet.js. Easily see where campuses are located and find nearby academic options.
- **Advanced Search & Filtering**: Narrow down colleges and programs by name or location to find exactly what you are looking for.
- **CV Builder**: Utilize an integrated online tool to instantly generate a professional curriculum vitae (CV). Fill out a simple form with your personal details, education, experience, and skills, and preview your CV in real-time. You can then print or save it directly as a PDF.
- **Secure Authentication**: Register and log in securely. The application handles user sessions and passwords robustly.
- **User Dashboard & Profile Management**: Maintain your profile preferences and manage personalized recommendations based on your interests and location.

## Technology Stack

The application relies on a modern stack:

*   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
*   **Frontend**: HTML5, Vanilla CSS, JavaScript
*   **Database**: SQLite (managed with SQLAlchemy ORM)
*   **Maps API**: Leaflet.js
*   **Fonts/Typography**: Google Fonts (DM Sans)

## Project Structure

```
Education-Navigator/
├── education-navigator/
│   ├── app.py                  # Main Flask application and routes
│   ├── import_data.py          # Script to load data from JSON into SQLite
│   ├── sample_data.py          # Script to generate initial sample database entries
│   ├── static/
│   │   ├── css/style.css     # Main stylesheet
│   │   └── images/           # Application images and logo
│   └── templates/              # HTML frontend templates (Jinja)
│       ├── _base.html        # Example base template layout
│       ├── index.html        # Home page
│       ├── colleges.html     # Interactive colleges list and map
│       ├── cv_builder.html   # Online CV generation tool
│       └── ...
├── colleges.json               # Raw JSON data source for colleges/programs
├── requirements.txt            # Python dependencies
└── .gitignore                  # Git exclusions file
```

## Installation and Setup

Follow these steps to run the application locally:

### 1. Clone the repository

```bash
git clone https://github.com/AakritiGuragain/Edu_Navigator.git
cd Edu_Navigator
```

### 2. Set up a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
# venv\Scripts\activate   # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

The application uses SQLite. To create the database schema:

```bash
cd education-navigator
python -c "from app import db, app; app.app_context().push(); db.create_all()"
```

You can populate the database using the sample data script, or the import script if you have historical data configured.

```bash
python sample_data.py
# OR
python import_data.py
```

### 5. Run the Application

Start the Flask development server:

```bash
python app.py
```

The application will be accessible in your web browser at `http://localhost:5001/` (or `http://0.0.0.0:5001/`).
