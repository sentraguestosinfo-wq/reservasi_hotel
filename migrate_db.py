import sqlite3
import os

db_path = r"c:\Users\user\Desktop\Nexa Hotel Bandung\mercure_nexa.db"
print(f"Connecting to DB at: {db_path}")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check columns
c.execute("PRAGMA table_info(bookings)")
columns = [row[1] for row in c.fetchall()]
print(f"Current columns: {columns}")

# Add 'category' if missing
if 'category' not in columns:
    print("Adding 'category' column...")
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN category TEXT DEFAULT 'booking'")
        print("Success.")
    except Exception as e:
        print(f"Failed to add category: {e}")

# Add 'orang' if missing
if 'orang' not in columns:
    print("Adding 'orang' column...")
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN orang TEXT")
        print("Success.")
    except Exception as e:
        print(f"Failed to add orang: {e}")

conn.commit()
conn.close()
print("Migration completed.")
