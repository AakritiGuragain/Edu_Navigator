import json
import sqlite3
import os

db_path = 'instance/education_navigator.db'
colleges_path = 'data/colleges.json'

def import_data():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing data manually via script
    cursor.execute("DELETE FROM program")
    cursor.execute("DELETE FROM college")
    conn.commit()

    # Load JSON files
    with open(colleges_path, 'r', encoding='utf-8') as f:
        colleges_data = json.load(f).get('colleges', [])

    for c in colleges_data:
        # Insert College
        name = c.get('name')
        location = f"{c.get('location', {}).get('city', '')}, {c.get('location', {}).get('district', '')}"
        
        # Build a description
        desc_parts = []
        if 'type' in c: desc_parts.append(c['type'])
        if 'affiliated_university' in c: desc_parts.append(f"Affiliated: {c['affiliated_university']}")
        if 'scholarship' in c and 'details' in c['scholarship']: desc_parts.append(f"Scholarships: {c['scholarship']['details']}")
        description = " | ".join(desc_parts)

        cursor.execute(
            "INSERT INTO college (name, location, description) VALUES (?, ?, ?)",
            (name, location, description)
        )
        college_id = cursor.lastrowid

        # Insert Programs
        for p in c.get('programs', []):
            duration = f"{p.get('duration_years', '')} years" if 'duration_years' in p else None
            fees = p.get('total_fee_npr')
            p_desc_parts = []
            if 'category' in p: p_desc_parts.append(p['category'])
            if 'seats' in p: p_desc_parts.append(f"Seats: {p['seats']}")
            p_desc = " | ".join(p_desc_parts)

            cursor.execute(
                "INSERT INTO program (name, college_id, description, duration, fees) VALUES (?, ?, ?, ?, ?)",
                (p.get('name'), college_id, p_desc, duration, fees)
            )

    conn.commit()
    conn.close()
    print("Data imported successfully!")

if __name__ == '__main__':
    import_data()
