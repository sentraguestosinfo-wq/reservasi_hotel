import sqlite3
conn = sqlite3.connect('mercure_nexa.db')
c = conn.cursor()
c.execute("SELECT tgl, tipe, category FROM bookings WHERE category='reservation' LIMIT 5")
rows = c.fetchall()
print("Reservations:", rows)
conn.close()
