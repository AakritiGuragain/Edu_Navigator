import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, College

def verify():
    with app.app_context():
        college_count = College.query.count()
        print(f"Total Colleges in DB: {college_count}")
        if college_count > 3:
            print("SUCCESS: Colleges imported correctly.")
        else:
            print("FAILURE: College count is still low.")

if __name__ == '__main__':
    verify()
