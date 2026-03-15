import sys
import os
from datetime import datetime, timedelta

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Scholarship

def seed_scholarships():
    with app.app_context():
        # Clear existing
        Scholarship.query.delete()
        
        data = [
            {
                "title": "MoEST General Scholarship 2026",
                "provider": "Ministry of Education, Nepal",
                "description": "Annual scholarship for meritorious students pursuing Bachelor's degrees in any field.",
                "deadline": datetime.now() + timedelta(days=45),
                "amount": "Full Tuition + NRS 5,000 monthly",
                "eligibility": "GPA > 3.2, Graduate of a Government School",
                "apply_link": "https://moest.gov.np/scholarships",
                "category": "Government"
            },
            {
                "title": "Indian Embassy Golden Jubilee Scholarship",
                "provider": "Embassy of India, Kathmandu",
                "description": "Prestigious scholarship for Nepali students to study in Nepal.",
                "deadline": datetime.now() + timedelta(days=20),
                "amount": "NRS 4,000 - 6,000 per month",
                "eligibility": "Class 12 GPA > 3.5, Age < 22",
                "apply_link": "https://www.indembkathmandu.gov.np",
                "category": "International"
            },
            {
                "title": "CAN Federation IT Scholarship",
                "provider": "CAN Federation",
                "description": "Scholarship specifically for IT and Engineering students across 7 provinces.",
                "deadline": datetime.now() + timedelta(days=12),
                "amount": "50% - 100% Tuition Waiver",
                "eligibility": "Nepali Citizen, Interested in ICT",
                "apply_link": "https://www.can.org.np",
                "category": "Private"
            },
            {
                "title": "Presidential Scholarship for Young Leaders",
                "provider": "Office of the President",
                "description": "For students who demonstrate excellent leadership in community service.",
                "deadline": datetime.now() + timedelta(days=5),
                "amount": "Full Ride",
                "eligibility": "Volunteer experience required, recommendations",
                "apply_link": "https://president.gov.np",
                "category": "Government"
            }
        ]
        
        for item in data:
            s = Scholarship(**item)
            db.session.add(s)
            
        db.session.commit()
        print(f"Imported {len(data)} scholarships successfully.")

if __name__ == "__main__":
    seed_scholarships()
