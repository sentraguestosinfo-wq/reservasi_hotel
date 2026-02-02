import sqlite3
conn = sqlite3.connect('mercure_nexa.db')
c = conn.cursor()
c.execute("SELECT resi, category, created_at, status FROM bookings WHERE resi LIKE 'RSV-%' LIMIT 20")
rows = c.fetchall()
print("Data Reservasi (RSV-):")
for r in rows:
    print(r)

print("-" * 30)

c.execute("SELECT resi, category, created_at, status FROM bookings WHERE category = 'reservation' LIMIT 20")
rows_cat = c.fetchall()
print("Data Category='reservation':")
for r in rows_cat:
    print(r)
conn.close()
