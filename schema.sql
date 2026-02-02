-- Script untuk membuat tabel di Supabase (PostgreSQL)
-- Jalankan script ini di SQL Editor pada Dashboard Supabase Anda.

CREATE TABLE IF NOT EXISTS bookings (
    resi TEXT PRIMARY KEY,
    chat_id TEXT,
    nama TEXT,
    tipe TEXT,
    tgl TEXT,
    jml_kamar TEXT,
    orang TEXT,
    harga TEXT,
    qris_status TEXT,
    phone TEXT,
    email TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP,
    via TEXT,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    extended INTEGER DEFAULT 0,
    category TEXT DEFAULT 'booking'
);

-- Optional: Create Index for performance
CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
