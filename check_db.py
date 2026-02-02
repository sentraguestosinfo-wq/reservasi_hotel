import sqlite3
try:
    conn = sqlite3.connect('mercure_nexa.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(bookings)")
    columns = [row[1] for row in c.fetchall()]
    print(f"Columns: {columns}")
    if 'orang' in columns:
        print("Column 'orang' EXISTS.")
    else:
        print("Column 'orang' MISSING.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
