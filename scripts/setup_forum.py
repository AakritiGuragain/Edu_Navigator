import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, ForumCategory

def setup_forum():
    with app.app_context():
        # Create all tables (will create new ones)
        db.create_all()
        
        # Seed categories if they don't exist
        categories = [
            ("Exams & Preparation", "Discuss entrance exams, syllabi, and study tips."),
            ("College Selection", "Get advice on which college fits your goals."),
            ("Student Life", "General discussions about campus life, hostels, and events."),
            ("Scholarships & Aid", "Exchange info on financial aid and application processes.")
        ]
        
        for name, desc in categories:
            if not ForumCategory.query.filter_by(name=name).first():
                cat = ForumCategory(name=name, description=desc)
                db.session.add(cat)
        
        db.session.commit()
        print("Forum setup and seeding complete!")

if __name__ == '__main__':
    setup_forum()
