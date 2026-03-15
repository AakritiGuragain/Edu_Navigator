from app import app, db
import os

db_path = 'instance/education_navigator.db'

def recreate():
    if os.path.exists(db_path):
        os.remove(db_path)
    
    with app.app_context():
        db.create_all()
    print("Database recreated successfully with updated schema.")

if __name__ == "__main__":
    recreate()
