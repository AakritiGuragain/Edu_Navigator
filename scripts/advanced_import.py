import json
import os
from app import app, db, College, Program, Location, Hostel

def import_advanced_data():
    # Authoritative master file
    master_file = 'data/colleges_master.json'

    if not os.path.exists(master_file):
        print(f"Error: {master_file} not found.")
        return

    with open(master_file, 'r') as f:
        master_data = json.load(f)

    with app.app_context():
        print("Recreating database schema...")
        db.drop_all()
        db.create_all()
        db.session.commit()

        colleges = master_data.get('colleges', [])
        print(f"Importing {len(colleges)} colleges from master dataset...")

        for c_data in colleges:
            basic = c_data.get('basic_info', {})
            loc = c_data.get('location', {})
            contact = c_data.get('contact', {})
            meta = c_data.get('meta', {})
            
            # Use reliable Street View format to avoid "Space" view issues
            lat = loc.get('latitude')
            lng = loc.get('longitude')
            # Fallback for virtual tour link if specific ones are missing or broken
            reliable_tour = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lng}"
            
            # 1. Create College
            image_urls = c_data.get('images', {}).get('static_fallback_urls', [])
            image_url = image_urls[0] if image_urls else None
            
            # IDs might be numeric strings "col_001" or integers. Stripping "col_" prefix.
            raw_id = c_data.get('id', '0')
            if isinstance(raw_id, str) and '_' in raw_id:
                clean_id = int(raw_id.split('_')[1])
            else:
                clean_id = int(raw_id)

            college = College(
                id=clean_id,
                name=basic.get('name'),
                full_name=basic.get('full_name'),
                short_name=basic.get('short_name'),
                type=basic.get('type'),
                affiliation=basic.get('affiliation'),
                established_year=basic.get('established_year'),
                description=c_data.get('description') or f"Premier institutional campus in {loc.get('district', 'Nepal')}.",
                scholarship_available=c_data.get('scholarship', {}).get('available', False) or len(c_data.get('scholarships_available', [])) > 0,
                image_url=image_url,
                virtual_tour_url=reliable_tour, # Forcing the reliable format
                logo_url=basic.get('logo_url'),
                website=contact.get('website'),
                phone=contact.get('phone'),
                email=contact.get('email'),
                popularity_score=meta.get('popularity_score', 50),
                total_students=meta.get('total_students')
            )
            db.session.add(college)
            db.session.flush()

            # 2. Create Location
            location = Location(
                college_id=college.id,
                address=loc.get('address'),
                city=loc.get('municipality') or loc.get('city'),
                district=loc.get('district'),
                province=loc.get('province'),
                latitude=lat,
                longitude=lng
            )
            db.session.add(location)

            # 3. Create Hostel (using hostel_detailed from merge)
            h_info = c_data.get('hostel_detailed') or c_data.get('facilities', {}).get('hostel_info')
            if h_info:
                fees_h = h_info.get('fees', {})
                monthly_fee = 0
                if isinstance(fees_h.get('monthly_fee'), (int, float)):
                    monthly_fee = fees_h.get('monthly_fee')
                elif isinstance(h_info.get('monthly_fee'), (int, float)):
                    monthly_fee = h_info.get('monthly_fee')
                
                meals_raw = fees_h.get('meals_included', h_info.get('meals_included', False))
                meals_included = True if str(meals_raw).lower() in ['true', 'yes', '1'] else False
                
                hostel = Hostel(
                    college_id=college.id,
                    available=h_info.get('available', True),
                    on_campus=h_info.get('on_campus', True),
                    capacity=h_info.get('capacity') if isinstance(h_info.get('capacity'), int) else None,
                    monthly_fee=monthly_fee,
                    gender=h_info.get('gender'),
                    meals_included=meals_included,
                    amenities=",".join(h_info.get('amenities', [])) if isinstance(h_info.get('amenities'), list) else ""
                )
                db.session.add(hostel)

            # 4. Create Programs
            for p_data in c_data.get('programs', []):
                admission = p_data.get('admission', {})
                
                # Resilient fee extraction
                total_fee = 0
                if 'total_fee_npr' in p_data:
                    total_fee = p_data['total_fee_npr']
                elif 'fees' in p_data and 'total_program_fee' in p_data['fees']:
                    total_fee = p_data['fees']['total_program_fee']
                
                program = Program(
                    name=p_data.get('name'),
                    college_id=college.id,
                    description=p_data.get('category') or p_data.get('field') or "Academic Program",
                    duration=f"{p_data.get('duration_years', 4)} Years",
                    fees=float(total_fee) if total_fee else 0.0,
                    gpa_requirement=admission.get('min_gpa') if isinstance(admission, dict) else None,
                    field=p_data.get('category') or p_data.get('field'),
                    entrance_required=p_data.get('entrance_required', False) or (isinstance(admission, dict) and admission.get('entrance_exam_required', False)),
                    entrance_exam=p_data.get('entrance_exam') or (isinstance(admission, dict) and admission.get('entrance_exam_name'))
                )
                db.session.add(program)

        db.session.commit()
        print("Advanced data migration completed successfully!")

if __name__ == '__main__':
    import_advanced_data()
