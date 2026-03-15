import json
import os
import sys
from datetime import datetime

# Add the project root to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db, app, College, Event

def import_events():
    with app.app_context():
        print("Starting Event Data Import...")
        
        # Open events.json
        events_path = os.path.join(os.path.dirname(__file__), '..', 'events.json')
        if not os.path.exists(events_path):
            print(f"Error: {events_path} not found.")
            return

        with open(events_path, 'r') as f:
            data = json.load(f)

        events_list = data.get('events', [])
        print(f"Found {len(events_list)} events in JSON.")

        # Clear existing events
        Event.query.delete()
        print("Cleared existing events.")

        for ev_data in events_list:
            college_name = ev_data.get('college_name')
            college = None
            
            # Try to match college by name or short name
            if college_name:
                college = College.query.filter(
                    (College.name.ilike(college_name)) | 
                    (College.short_name.ilike(ev_data.get('college_short_name', '')))
                ).first()

            # Flattened Fields
            event = Event(
                event_id=ev_data.get('event_id'),
                college_id=college.id if college else None,
                college_name=college_name,
                title=ev_data.get('title'),
                type=ev_data.get('type'),
                start_date=ev_data.get('schedule', {}).get('start_date'),
                end_date=ev_data.get('schedule', {}).get('end_date'),
                start_time=ev_data.get('schedule', {}).get('start_time'),
                end_time=ev_data.get('schedule', {}).get('end_time'),
                venue_name=ev_data.get('venue', {}).get('name'),
                address=ev_data.get('venue', {}).get('address'),
                google_maps_link=ev_data.get('venue', {}).get('google_maps_link'),
                description=ev_data.get('details', {}).get('description'),
                registration_link=ev_data.get('details', {}).get('registration_link'),
                is_open_to_public=ev_data.get('details', {}).get('is_open_to_public', True),
                verified=ev_data.get('source', {}).get('verified', False),
                poster_url=ev_data.get('media', {}).get('poster_url'),
                is_featured=ev_data.get('meta', {}).get('is_featured', False),
                tags=', '.join(ev_data.get('tags', []))
            )
            
            db.session.add(event)
            print(f"Added Event: {event.title}")

        db.session.commit()
        print("All events imported successfully!")

if __name__ == '__main__':
    import_events()
