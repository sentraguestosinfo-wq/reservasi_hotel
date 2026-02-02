import sqlite3

try:
    conn = sqlite3.connect('mercure_nexa.db')
    c = conn.cursor()
    
    # Check columns
    print("Columns in bookings table:")
    c.execute("PRAGMA table_info(bookings)")
    columns = c.fetchall()
    col_names = [col[1] for col in columns]
    for col in columns:
        print(col)
        
    print("\nChecking if required columns exist:")
    required = ['resi', 'nama', 'tipe', 'tgl', 'jml_kamar', 'harga', 'status', 'email', 'via', 'created_at', 'orang']
    missing = [r for r in required if r not in col_names]
    
    if missing:
        print(f"MISSING COLUMNS: {missing}")
    else:
        print("All required columns are present.")
        
    # Try the exact query used in app.py
    print("\nTesting query...")
    try:
        c.execute("SELECT resi, nama, tipe, tgl, jml_kamar, harga, status, email, via, created_at, orang FROM bookings ORDER BY created_at DESC LIMIT 50")
        rows = c.fetchall()
        print(f"Query successful. Returned {len(rows)} rows.")
    except Exception as e:
        print(f"QUERY FAILED: {e}")

    conn.close()

except Exception as e:
    print(f"Database connection error: {e}")
