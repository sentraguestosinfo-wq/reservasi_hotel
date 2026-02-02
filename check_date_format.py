import sqlite3
conn = sqlite3.connect('mercure_nexa.db')
c = conn.cursor()
c.execute("SELECT tgl, tipe, category FROM bookings LIMIT 5")
rows = c.fetchall()
for row in rows:
    print(row)
conn.close()
