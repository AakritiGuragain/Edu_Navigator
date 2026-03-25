import json
import os
import sys

# Add the project root to sys.path to import app and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, College, Location, Program, Hostel

def import_colleges(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    colleges = data.get('colleges', [])
    for c_data in colleges:
        name = c_data.get('name')
        if not name:
            continue

        # Check if college already exists
        existing_college = College.query.filter_by(name=name).first()
        if existing_college:
            print(f"Skipping {name} (already exists)")
            continue

        print(f"Importing {name}...")
        
        # Create College
        college = College(
            name=name,
            full_name=c_data.get('full_name', name),
            type=c_data.get('type'),
            affiliation=c_data.get('affiliated_university'),
            description=c_data.get('scholarship', {}).get('details', ''),
            scholarship_available=c_data.get('scholarship', {}).get('available', False),
            established_year=None, # Not explicitly in JSON top level but could be inferred or left blank
            popularity_score=80, # Default popularity
            is_verified=True
        )
        db.session.add(college)
        db.session.flush() # Get college.id

        # Create Location
        loc_data = c_data.get('location', {})
        coords = loc_data.get('coordinates', {})
        location = Location(
            college_id=college.id,
            address=loc_data.get('address'),
            city=loc_data.get('city'),
            district=loc_data.get('district'),
            province=loc_data.get('province'),
            latitude=coords.get('lat'),
            longitude=coords.get('lng')
        )
        db.session.add(location)

        # Create Hostel
        facilities = c_data.get('facilities', {})
        if facilities.get('hostel'):
            hostel = Hostel(
                college_id=college.id,
                available=True,
                on_campus=True, # Assumption
                capacity=None,
                monthly_fee=None,
                gender='Both',
                meals_included=True,
                amenities=''
            )
            db.session.add(hostel)

        # Create Programs
        programs = c_data.get('programs', [])
        for p_data in programs:
            program = Program(
                name=p_data.get('name'),
                college_id=college.id,
                description=p_data.get('category'),
                duration=f"{p_data.get('duration_years')} Years",
                fees=float(p_data.get('total_fee_npr', 0)),
                gpa_requirement=2.0, # Default
                field=p_data.get('category'),
                entrance_required=p_data.get('entrance_required', False),
                entrance_exam=p_data.get('entrance_exam')
            )
            db.session.add(program)

    db.session.commit()
    print("Import complete!")

if __name__ == '__main__':
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'colleges.json'))
    with app.app_context():
        import_colleges(json_path)
