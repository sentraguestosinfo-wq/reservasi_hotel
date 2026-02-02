import sqlite3
import json
from datetime import datetime

def test_api():
    try:
        conn = sqlite3.connect('mercure_nexa.db', timeout=10)
        c = conn.cursor()
        
        # 1. Check Schema
        print("--- SCHEMA ---")
        c.execute("PRAGMA table_info(bookings)")
        columns = [row[1] for row in c.fetchall()]
        print(f"Columns: {columns}")
        
        # 2. Test Query
        print("\n--- TEST QUERY ---")
        query = "SELECT resi, nama, tipe, tgl, jml_kamar, harga, status, email, via, created_at, orang FROM bookings ORDER BY created_at DESC LIMIT 50"
        print(f"Executing: {query}")
        c.execute(query)
        rows = c.fetchall()
        print(f"Rows fetched: {len(rows)}")
        
        # 3. Test Processing
        print("\n--- PROCESSING ---")
        data = []
        for r in rows:
            print(f"Row: {r}")
            # Parse jam booking dari created_at
            jam_booking = '-'
            try:
                if r[9]: # created_at column
                    dt = datetime.strptime(r[9], '%Y-%m-%d %H:%M:%S.%f')
                    jam_booking = dt.strftime('%H:%M')
            except Exception as e1:
                print(f"Date parse error 1: {e1}")
                try:
                    # Fallback format check
                    dt = datetime.strptime(r[9], '%Y-%m-%d %H:%M:%S')
                    jam_booking = dt.strftime('%H:%M')
                except Exception as e2: 
                    print(f"Date parse error 2: {e2}")
                    pass

            item = {
                "resi": r[0],
                "nama": r[1],
                "tipe": r[2],
                "tgl": r[3],
                "jml_kamar": r[4],
                "harga": "{:,.0f}".format(float(r[5])) if r[5] else "0",
                "status": r[6],
                "email": r[7],
                "via": r[8],
                "jam_booking": jam_booking,
                "orang": r[10]
            }
            data.append(item)
            
        print("\n--- RESULT JSON ---")
        print(json.dumps(data, indent=2))
        
        conn.close()
        print("\nSUCCESS")
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")

if __name__ == "__main__":
    test_api()
