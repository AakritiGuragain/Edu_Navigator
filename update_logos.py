import sqlite3

def main():
    try:
        conn = sqlite3.connect('instance/education_navigator.db')
        cursor = conn.cursor()
        
        # 1. Pulchowk
        cursor.execute("UPDATE college SET logo_url = '/static/images/logos/Pulchowk_Campus__TU-IOE.jpg', image_url = '/static/images/logos/Pulchowk_Campus__TU-IOE.jpg' WHERE name LIKE '%Pulchowk%'")
        
        # 2. KUSOM
        cursor.execute("UPDATE college SET logo_url = '/static/images/logos/KU_School_of_Management__KUSOM.png', image_url = '/static/images/logos/KU_School_of_Management__KUSOM.png' WHERE name LIKE '%Kathmandu University School of Management%'")
        
        # 3. St. Xavier's (since we don't have its logo, let's leave it, but it will fallback to logo1.png)
        
        conn.commit()
        print(f"Updated {cursor.rowcount} rows.")
        conn.close()
        print("Successfully updated database.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
