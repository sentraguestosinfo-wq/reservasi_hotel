#!/usr/bin/env python3
import telebot
from telebot import types
from flask import Flask, render_template, request, jsonify, send_file, redirect, make_response
from datetime import datetime, timedelta

import os
import data  # Import data.py
import urllib.parse
import time
import calendar
from fpdf import FPDF
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import socket
from supabase import create_client, Client

# --- KONFIGURASI ---
# Force IPv4 to prevent IPv6 connection issues on Vercel
try:
    old_getaddrinfo = socket.getaddrinfo
    def new_getaddrinfo(*args, **kwargs):
        responses = old_getaddrinfo(*args, **kwargs)
        return [response for response in responses if response[0] == socket.AF_INET]
    socket.getaddrinfo = new_getaddrinfo
    print("IPv4 Forced for socket connections.")
    print("App Version: 2.1 - Fix Handler Clash & Calendar")
except Exception as e:
    print(f"Failed to force IPv4: {e}")

# GANTI DENGAN TOKEN BOT ANDA
API_TOKEN = '8556104756:AAGVZJyvrxV4P-yN486BH7K5SR_f8jRZDLw' 
# URL Aplikasi (Vercel)
APP_URL = 'https://reservasi-hotel-seven.vercel.app'

# SUPABASE CONFIG (REST API MODE)
SUPABASE_URL = "https://relkgipocdukdusakdtv.supabase.co"
# Note: Using SERVICE_ROLE key is risky for frontend but okay for backend server. 
# Better to use env vars, but hardcoded here as per user style.
SUPABASE_KEY = "sb_secret_qc2aaevA7-UEx_YNS93uVQ__JwiQVP4" 
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# KONFIGURASI EMAIL
GMAIL_USER = 'sentraguest.os@gmail.com'
# PERHATIAN: Ganti dengan App Password Gmail Anda (bukan password login biasa)
# Cara buat App Password: Akun Google > Keamanan > Verifikasi 2 Langkah > App Passwords
GMAIL_APP_PASSWORD = 'ajgeakaeomfjilqb' 


app = Flask(__name__, static_folder='static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

bot = telebot.TeleBot(API_TOKEN)
STAFF_FO_IDS = [784633296] # ID Staff yang akan menerima notifikasi

def format_guest_name(name):
    try:
        n = (name or '').strip()
        low = n.lower()
        if low.startswith('mr ') or low.startswith('mr.') or low.startswith('mrs ') or low.startswith('mrs.'):
            return n
        return f"Mr/Mrs {n}"
    except:
        return f"Mr/Mrs {name}"


@app.route('/')
def index():
    # Kirim data dari data.py ke template HTML
    return render_template('index.html', 
                           rooms=data.ROOMS, 
                           facilities=data.FACILITIES, 
                           malls=data.MALLS, 
                           atms=data.ATMS)

@app.route('/reservasi')
def reservasi_page():
    return render_template('reservasi.html', 
                           rooms=data.ROOMS, 
                           facilities=data.FACILITIES, 
                           malls=data.MALLS, 
                           atms=data.ATMS)

@app.route('/sw.js')
def sw():
    return app.send_static_file('sw.js')

@app.route('/qris_image')
def qris_image():
    # Sajikan file qris.jpeg dari root directory (Safe for Vercel)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    qris_path = os.path.join(base_dir, 'qris.jpeg')
    
    if os.path.exists(qris_path):
        return send_file(qris_path, mimetype='image/jpeg')
    else:
        return "QRIS image not found", 404

# --- REDIRECT HANDLER UNTUK WHATSAPP ---
@app.route('/wa_redirect')
def wa_redirect():
    try:
        resi = request.args.get('resi')
        staff_id = request.args.get('id')
        msg_id = request.args.get('mid')
        
        if not resi:
            return "Invalid request: Missing resi", 400
            
        # 1. Ambil data booking
        try:
            response = supabase.table('bookings').select('phone, nama').eq('resi', resi).execute()
            if not response.data:
                return "Booking not found", 404
            
            result = response.data[0]
            phone_db = result['phone']
            nama_db = result['nama']
            
            # Update status QRIS
            supabase.table('bookings').update({'qris_status': 'sent'}).eq('resi', resi).execute()
            
        except Exception as e:
             return f"Database Error: {e}", 500
            
        # 2. Update Telegram Message (Hapus tombol Kirim QRIS & Kirim Konfirmasi)
        if staff_id and msg_id:
            try:
                # Kirim notifikasi konfirmasi sukses ke staff (Seperti di Telegram)
                bot.send_message(staff_id, f"✅ QRIS berhasil dikirim ke tamu dengan Resi {resi}.")

                # Update markup agar tombol Kirim WA hilang
                markup = types.InlineKeyboardMarkup()
                
                clean_phone = ''.join(filter(str.isdigit, str(phone_db)))
                if clean_phone.startswith('0'):
                    clean_phone = '62' + clean_phone[1:]
                
                # Hanya sisakan tombol Chat Tamu (WhatsApp)
                btn_chat_wa = types.InlineKeyboardButton("💬 Chat Tamu (WhatsApp)", url=f"https://wa.me/{clean_phone}")
                markup.add(btn_chat_wa)
                
                bot.edit_message_reply_markup(chat_id=staff_id, message_id=msg_id, reply_markup=markup)
            except Exception as e:
                print(f"Failed to update Telegram message from redirect: {e}")

        # 3. Redirect ke WhatsApp
        clean_phone = ''.join(filter(str.isdigit, str(phone_db)))
        if clean_phone.startswith('0'):
            clean_phone = '62' + clean_phone[1:]
            
        wa_text = f"Halo {format_guest_name(nama_db)}, ini dari Mercure Bandung Nexa Supratman (Resi: {resi}).\n\nBerikut Link QRIS untuk pembayaran:\n{APP_URL}/qris_image\n\nMohon konfirmasi jika sudah transfer. Terima kasih 🙏"
        
        wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_text)}"
        
        return redirect(wa_link)
        
    except Exception as e:
        return f"System Error: {e}", 500

def send_booking_email(to_email, booking_data):
    if not to_email or to_email == '-' or 'GANTI' in GMAIL_APP_PASSWORD:
        print("Skipping email sending: Invalid email or password not set.")
        return

    try:
        display_name = format_guest_name(booking_data['nama'])
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = f"Konfirmasi Booking - {booking_data['resi']} - Mercure Bandung Nexa"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; text-align: left; color: #333;">
            <h2 style="color: #512D6D;">Konfirmasi Booking</h2>
            <p>Halo <strong>{display_name}</strong>,</p>
            <p>Terima kasih telah melakukan pemesanan di Mercure Bandung Nexa Supratman.<br>
            Berikut adalah detail reservasi Anda:</p>
            
            <table style="width: 100%; max-width: 600px; border-collapse: collapse; margin-bottom: 20px;">
                <tr><td style="padding: 5px; font-weight: bold;">No. Resi</td><td style="padding: 5px;">: {booking_data['resi']}</td></tr>
                <tr><td style="padding: 5px; font-weight: bold;">Tgl Check-in</td><td style="padding: 5px;">: {booking_data['tgl']}</td></tr>
                <tr><td style="padding: 5px; font-weight: bold;">Tipe Kamar</td><td style="padding: 5px;">: {booking_data['tipe']}</td></tr>
                <tr><td style="padding: 5px; font-weight: bold;">Jumlah Kamar</td><td style="padding: 5px;">: {booking_data['jml_kamar']}</td></tr>
                <tr><td style="padding: 5px; font-weight: bold;">Jumlah Tamu</td><td style="padding: 5px;">: {booking_data['orang']}</td></tr>
                <tr><td style="padding: 5px; font-weight: bold;">Total Harga</td><td style="padding: 5px;">: Rp {booking_data['total_harga']}</td></tr>
            </table>
            
            <p>Mohon simpan bukti ini untuk proses Check-in.<br>
            Harap segera melakukan pembayaran dalam waktu <strong>2 JAM</strong> setelah booking ini dibuat. Jika melewati batas waktu tersebut, sistem akan otomatis membatalkan booking Anda.</p>
            
            <p>Jika belum melakukan pembayaran, silakan hubungi staff kami atau lakukan pembayaran di resepsionis.</p>
            
            <br>
            <p>Salam Hangat,<br>
            <strong>Mercure Bandung Nexa Supratman</strong></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_USER, to_email, text)
        server.quit()
        print(f"Email konfirmasi terkirim ke {to_email}")
    except Exception as e:
        print(f"Gagal kirim email: {e}")

def send_qris_email(to_email, booking_data):
    if not to_email or to_email == '-' or 'GANTI' in GMAIL_APP_PASSWORD:
        return

    try:
        display_name = format_guest_name(booking_data['nama'])
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = f"Link Pembayaran QRIS - {booking_data['resi']} - Mercure Bandung Nexa"

        # Link QRIS (Direct Image or Page)
        # Using qris_image endpoint
        qris_link = f"{APP_URL}/qris_image"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; text-align: left; color: #333;">
            <h2 style="color: #512D6D;">Link Pembayaran QRIS</h2>
            <p>Halo <strong>{display_name}</strong>,</p>
            <p>Terima kasih atas reservasi Anda (Resi: {booking_data['resi']}).</p>
            
            <p>Silakan klik link di bawah ini untuk melihat QRIS Pembayaran:</p>
            <p><a href="{qris_link}" style="background-color: #512D6D; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Lihat QRIS Pembayaran</a></p>
            <p style="font-size: 12px; color: #777;">Atau buka link ini: <a href="{qris_link}">{qris_link}</a></p>
            
            <p><strong>Total Tagihan: Rp {booking_data['total_harga']}</strong></p>
            
            <p>Setelah melakukan pembayaran, mohon balas email ini atau informasikan ke staff kami.</p>
            
            <br>
            <p>Salam Hangat,<br>
            <strong>Mercure Bandung Nexa Supratman</strong></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_USER, to_email, text)
        server.quit()
        print(f"Email QRIS terkirim ke {to_email}")
    except Exception as e:
        print(f"Gagal kirim email QRIS: {e}")

@app.route('/submit_reservasi', methods=['POST'])
def submit_reservasi():
    try:
        data_req = request.json
        # Wajib Email
        email = data_req.get('email', '-')
        if not email or email == '-':
            return jsonify({"status": "error", "message": "Email wajib diisi untuk Reservasi"}), 400

        chat_id = 'unknown' # Reservasi via Web
        phone = str(data_req.get('phone', '-'))
        resi = f"RSV-{datetime.now().strftime('%y%m%d%H%M')}"
        
        current_time = datetime.now()
        booking_time_str = current_time.strftime('%H:%M')
        
        # Simpan ke DB dengan status 'reservation' (Bukan 'pending')
        # Category = 'reservation'
        try:
            data_insert = {
                'resi': resi,
                'chat_id': chat_id,
                'nama': data_req['nama'],
                'tipe': data_req['tipe'],
                'tgl': data_req['tgl'],
                'jml_kamar': data_req['jml_kamar'],
                'orang': data_req['orang'],
                'harga': str(data_req['total_harga']),
                'qris_status': 'pending',
                'phone': phone,
                'email': email,
                'via': 'web',
                'lat': 0,
                'lng': 0,
                'created_at': current_time.isoformat(),
                'status': 'reserved',
                'extended': 0,
                'category': 'reservation'
            }
            supabase.table('bookings').insert(data_insert).execute()
        except Exception as e:
            return jsonify({"status": "error", "message": f"Database error: {e}"}), 500

        # Email Konfirmasi Reservasi
        try:
            msg = MIMEMultipart()
            msg['From'] = GMAIL_USER
            msg['To'] = email
            msg['Subject'] = f"Permintaan {data_req['tipe']} - {resi} - Mercure Bandung Nexa"
            
            # Detail String based on Type
            detail_str = ""
            if data_req['tipe'] == 'Kamar':
                detail_str = f"Jumlah Kamar: {data_req['jml_kamar']} Unit"
            elif data_req['tipe'] == 'Meeting' or data_req['tipe'] == 'Birthday':
                detail_str = f"Jumlah Pax: {data_req['orang']} Orang"
            elif data_req['tipe'] == 'Wedding':
                detail_str = f"Jumlah Pax: {data_req['orang']} Orang\n            Kebutuhan Kamar: {data_req['jml_kamar']} Unit"

            display_name = format_guest_name(data_req['nama'])
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; text-align: left; color: #333;">
                <h2 style="color: #512D6D;">Permintaan {data_req['tipe']} Diterima</h2>
                <p>Halo <strong>{display_name}</strong>,</p>
                <p>Permintaan {data_req['tipe']} Anda telah kami terima.<br>
                Staff kami akan segera memeriksa ketersediaan dan menghubungi Anda untuk penawaran terbaik.</p>
                
                <h3 style="border-bottom: 1px solid #ddd; padding-bottom: 5px;">Detail Permintaan:</h3>
                <table style="width: 100%; max-width: 600px; border-collapse: collapse; margin-bottom: 20px;">
                    <tr><td style="padding: 5px; font-weight: bold;">No. Resi</td><td style="padding: 5px;">: {resi}</td></tr>
                    <tr><td style="padding: 5px; font-weight: bold;">Tanggal</td><td style="padding: 5px;">: {data_req['tgl']}</td></tr>
                    <tr><td style="padding: 5px; font-weight: bold;">Jenis</td><td style="padding: 5px;">: {data_req['tipe']}</td></tr>
                    <tr><td style="padding: 5px; font-weight: bold;">Detail</td><td style="padding: 5px;">: {detail_str}</td></tr>
                </table>
                
                <p>Mohon tunggu konfirmasi selanjutnya dari staff kami melalui WhatsApp atau Email.</p>
                
                <br>
                <p>Salam Hangat,<br>
                <strong>Mercure Bandung Nexa Supratman</strong></p>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, email, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Failed send reservation email: {e}")

        # Notifikasi Staff FO
        for sid in STAFF_FO_IDS:
            try:
                # Detail for Staff
                detail_staff = ""
                if data_req['tipe'] == 'Kamar':
                    detail_staff = f"🛏 Kamar: {data_req['jml_kamar']} Unit"
                elif data_req['tipe'] == 'Meeting' or data_req['tipe'] == 'Birthday':
                    detail_staff = f"👥 Pax: {data_req['orang']} Orang"
                elif data_req['tipe'] == 'Wedding':
                    detail_staff = f"👥 Pax: {data_req['orang']} Orang\n🛏 Kamar: {data_req['jml_kamar']} Unit"

                msg_staff = (f"📅 PERMINTAAN {data_req['tipe'].upper()} BARU\n━━━━━━━━━━━━━━━━━━━━\n"
                                f"🆔 No. Resi: {resi}\n"
                                f"👤 PIC: {data_req['nama']}\n"
                                f"📞 WA: {phone}\n"
                                f"📧 Email: {email}\n"
                                f"📅 Tanggal: {data_req['tgl']}\n"
                                f"{detail_staff}\n"
                                f"⏰ Jam Request: {booking_time_str}\n"
                                "━━━━━━━━━━━━━━━━━━━━\n"
                                "Segera hubungi tamu untuk konfirmasi & penawaran.")
                
                # Send Message
                # Add Buttons (Chat WA / Email)
                markup = types.InlineKeyboardMarkup()
                
                # Chat Tamu Email
                if email and email != '-':
                    btn_chat_email = types.InlineKeyboardButton("📧 Chat Tamu (Email)", url=f"mailto:{email}")
                    markup.add(btn_chat_email)

                # WA Button (Removed as per request, but keeping logic if needed later or just removing)
                # clean_phone = ''.join(filter(str.isdigit, str(phone)))
                # if clean_phone.startswith('0'):
                #    clean_phone = '62' + clean_phone[1:]
                # 
                # if clean_phone:
                #    btn_wa = types.InlineKeyboardButton("💬 Chat WA", url=f"https://wa.me/{clean_phone}")
                #    markup.add(btn_wa)
                
                bot.send_message(sid, msg_staff, reply_markup=markup)

            except Exception as e:
                 print(f"Failed send staff notif: {e}")

        return jsonify({"status": "success", "resi": resi})

    except Exception as e:
        print(f"Error submit_reservasi: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    try:
        data_req = request.json
        chat_id = str(data_req.get('chat_id', 'unknown'))
        phone = str(data_req.get('phone', '-'))
        resi = f"NEXA-{datetime.now().strftime('%y%m%d%H%M')}"
        
        # New Fields
        via = data_req.get('via', 'web' if chat_id == 'unknown' else 'telegram')
        email = data_req.get('email', '-')
        lat = data_req.get('lat', 0)
        lng = data_req.get('lng', 0)
        
        # Validasi Email jika via Web
        if via == 'web' and (not email or email == '-'):
            return jsonify({"status": "error", "message": "Email wajib diisi untuk booking via Web"}), 400

        try:
            # --- ANTI-DUPLICATE CHECK (10 Menit) ---
            # Cek apakah ada booking dengan Nama & Tanggal & HP yang sama dalam 10 menit terakhir
            res_dup = supabase.table('bookings').select('resi').eq('nama', data_req['nama']).eq('tgl', data_req['tgl']).eq('phone', phone).execute()
            existing = res_dup.data
            
            current_time = datetime.now()
            for row in existing:
                try:
                    # Parse waktu dari Resi: NEXA-YYMMDDHHMM
                    # Ambil bagian angka setelah 'NEXA-'
                    ts_str = row['resi'].split('-')[1]
                    booking_time = datetime.strptime(ts_str, '%y%m%d%H%M')
                    
                    # Jika selisih waktu kurang dari 10 menit (600 detik)
                    if (current_time - booking_time).total_seconds() < 600:
                        print(f"Duplicate booking prevented: {row['resi']}")
                        # Return sukses dengan resi lama (Idempotency)
                        return jsonify({"status": "success", "resi": row['resi']})
                except Exception as e:
                    print(f"Error parsing resi for duplicate check: {e}")
                    # Continue checking others

            # --- INSERT NEW BOOKING ---
            data_insert = {
                'resi': resi,
                'chat_id': chat_id,
                'nama': data_req['nama'],
                'tipe': data_req['tipe'],
                'tgl': data_req['tgl'],
                'jml_kamar': data_req['jml_kamar'],
                'orang': data_req['orang'],
                'harga': str(data_req['total_harga']),
                'qris_status': 'pending',
                'phone': phone,
                'email': email,
                'via': via,
                'lat': lat,
                'lng': lng,
                'created_at': current_time.isoformat(),
                'status': 'pending',
                'extended': 0,
                'category': 'booking'
            }
            supabase.table('bookings').insert(data_insert).execute()
            
        except Exception as e:
            return jsonify({"status": "error", "message": f"Database error: {e}"}), 500


        # Send Email Confirmation if email exists
        if email and email != '-':
            # Run in thread to not block response
            Thread(target=send_booking_email, args=(email, {
                'resi': resi,
                'nama': data_req['nama'],
                'tgl': data_req['tgl'],
                'tipe': data_req['tipe'],
                'jml_kamar': data_req['jml_kamar'],
                'orang': data_req['orang'],
                'total_harga': data_req['total_harga']
            })).start()

        # Calculate Deadline
        deadline_dt = current_time + timedelta(hours=2)
        deadline_str = deadline_dt.strftime('%H:%M')
        booking_time_str = current_time.strftime('%H:%M')

        rincian = (f"🆔 *No. Resi:* `{resi}`\n👤 *Tamu:* {data_req['nama']}\n"
                   f"📧 *Email:* {email}\n"
                   f"📅 *Tanggal Booking:* {data_req['tgl']}\n"
                   f"🛏 *Kamar:* {data_req['tipe']} ({data_req['jml_kamar']} unit)\n"
                   f"🔢 *Orang:* {data_req['orang']} Orang\n💰 *Total:* Rp {data_req['total_harga']}\n"
                   f"⏰ *Jam Booking:* {booking_time_str}\n"
                   f"⏳ *Batas Pembayaran:* Jam {deadline_str} (2 Jam setelah Booking)")
        
        if phone and phone != '-':
             rincian += f"\n📞 *HP:* {phone}"

        # Notifikasi ke Tamu (via Chat Pribadi Bot - hanya jika via Telegram)
        if via == 'telegram' and chat_id != 'unknown':
            try:
                guest_disp = format_guest_name(data_req['nama'])
                greeting = f"Halo {guest_disp},"
                bot.send_message(chat_id, f"{greeting}\n\n✨ *RESERVASI BERHASIL DITERIMA*\n━━━━━━━━━━━━━━━━━━━━\n" + rincian + "\n━━━━━━━━━━━━━━━━━━━━\n⚠️ _Jika dalam 2 jam Anda tidak berada di lokasi hotel (radius 10km) atau belum melakukan pembayaran, booking akan otomatis dibatalkan._", parse_mode='Markdown')
            except:
                print(f"Gagal mengirim pesan ke user {chat_id}")

        # Notifikasi ke Staff FO
        for sid in STAFF_FO_IDS:
            try:
                # Tentukan Sumber Booking
                source_display = "📱 Aplikasi Telegram" if via == 'telegram' else "🌐 Browser / Web"
                
                # Gunakan parse_mode=None agar pesan tetap terkirim meski ada karakter spesial di nama tamu
                msg_staff = (f"🔔 BOOKING BARU MASUK\n━━━━━━━━━━━━━━━━━━━━\n"
                             f"🆔 No. Resi: {resi}\n"
                             f"🔄 Sumber: {source_display}\n"
                             f"👤 Tamu: {data_req['nama']}\n"
                             f"📞 HP/WA: {phone}\n"
                             f"📧 Email: {email}\n"
                             f"📅 Tanggal Booking: {data_req['tgl']}\n"
                             f"🛏 Kamar: {data_req['tipe']} ({data_req['jml_kamar']} unit)\n"
                             f"🔢 Orang: {data_req['orang']}\n"
                             f"💰 Total: Rp {data_req['total_harga']}\n"
                             f"⏰ Jam Booking: {booking_time_str}\n"
                             f"⏳ Batas Pembayaran: Jam {deadline_str} (2 Jam setelah Booking)\n"
                             f"📍 Posisi Tamu: {'✅ Ada' if lat else '❌ Tidak ada'}\n"
                             "━━━━━━━━━━━━━━━━━━━━")
                
                # Siapkan Link WA (Hanya jika ada phone)
                has_phone = phone and phone != '-'
                clean_phone = ''
                if has_phone:
                    clean_phone = ''.join(filter(str.isdigit, phone))
                    if clean_phone.startswith('0'):
                        clean_phone = '62' + clean_phone[1:]
                
                markup = types.InlineKeyboardMarkup()

                if via == 'telegram' and chat_id != 'unknown':
                    # JIKA VIA TELEGRAM: Cukup tampilkan tombol Telegram
                    # Tombol Kirim QRIS (Telegram)
                    btn_qris_tg = types.InlineKeyboardButton("📤 Kirim QRIS (Telegram)", callback_data=f"qris_{resi}_{chat_id}")
                    markup.add(btn_qris_tg)
                    
                    # Chat Telegram
                    btn_chat = types.InlineKeyboardButton("💬 Chat Tamu (Telegram)", url=f"tg://user?id={chat_id}")
                    markup.add(btn_chat)
                    
                    # Kirim pesan langsung dengan markup
                    bot.send_message(sid, msg_staff, reply_markup=markup)

                else:
                    # JIKA VIA BROWSER
                    # Kirim pesan dulu untuk dapat ID (karena butuh message_id untuk redirect)
                    sent_msg = bot.send_message(sid, msg_staff)

                    if has_phone:
                        # Tampilkan Tombol WA dengan REDIRECT URL
                        redirect_url = f"{APP_URL}/wa_redirect?resi={resi}&id={sid}&mid={sent_msg.message_id}"
                        
                        btn_qris_wa = types.InlineKeyboardButton("📤 Kirim QRIS (WhatsApp)", url=redirect_url)
                        markup.add(btn_qris_wa)
                        
                        # Link Chat WA Langsung
                        btn_wa = types.InlineKeyboardButton("💬 Chat Tamu (WhatsApp)", url=f"https://wa.me/{clean_phone}")
                        markup.add(btn_wa)
                    else:
                        # Jika tidak ada no HP (via Email Only)
                        if email and email != '-':
                             btn_qris_email = types.InlineKeyboardButton("📧 Kirim QRIS (Email)", callback_data=f"qris_email_{resi}_{chat_id}")
                             markup.add(btn_qris_email)
                
                    # Update pesan dengan markup
                    bot.edit_message_reply_markup(sid, sent_msg.message_id, reply_markup=markup)
                
                print(f"Sukses kirim notifikasi ke staff {sid}")
            except Exception as e:
                print(f"Gagal kirim ke staff {sid}: {e}")
        
        return jsonify({"status": "success", "resi": resi})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- BOT COMMANDS ---

@bot.message_handler(commands=['start'])
def start(message):
    # Hapus tombol keyboard tambahan (karena sudah ada tombol biru Menu)
    markup = types.ReplyKeyboardRemove()
    
    welcome_text = (
        "Selamat Datang di *Mercure Bandung Nexa Supratman Bot*.\n\n"
        "Silahkan tekan tombol menu biru *Aplikasi Hotel* di pojok kiri bawah untuk mengakses layanan kami."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, "Bantuan: Klik tombol 'BUKA APLIKASI HOTEL' untuk mengakses semua fitur.")

# --- FITUR STAFF FO (CEK BOOKING & QRIS) ---

STAFF_COMMANDS = [
    'dashboard_reservasi', 'dash_reservasi',
    'cek_pembayaran',
    'date_reservasi', 'calendar', 'kalender',
    'cek_booking',
    'cetak_lap_harian', 'cetak_laporan_harian',
    'cetak_laporan_reservasi',
    'sys_check'
]

@bot.message_handler(commands=STAFF_COMMANDS)
def staff_command_dispatcher(message):
    print(f"DEBUG: Dispatcher received {message.text} from {message.chat.id}")
    
    if message.chat.id not in STAFF_FO_IDS:
        bot.send_message(message.chat.id, f"❌ Akses Ditolak. ID Anda: {message.chat.id} tidak terdaftar sebagai Staff FO.")
        return

    # Normalize command
    cmd = message.text.split()[0].lower().replace('/', '').split('@')[0]
    
    if cmd in ['dashboard_reservasi', 'dash_reservasi']:
        logic_dashboard_reservasi(message)
    elif cmd == 'cek_pembayaran':
        logic_cek_pembayaran(message)
    elif cmd in ['date_reservasi', 'calendar', 'kalender']:
        logic_date_reservasi(message)
    elif cmd == 'cek_booking':
        logic_cek_booking(message)
    elif cmd in ['cetak_lap_harian', 'cetak_laporan_harian']:
        logic_cetak_lap_harian(message)
    elif cmd == 'cetak_laporan_reservasi':
        logic_cetak_laporan_reservasi(message)
    elif cmd == 'sys_check':
                bot.send_message(message.chat.id, "✅ System Online\nVersion: 2.4 (Vercel Fix)\nDeployment: ACTIVE\nStatus: Ready")

def logic_dashboard_reservasi(message):
    print(f"DEBUG: /dashboard_reservasi accessed by {message.chat.id}")
    if message.chat.id not in STAFF_FO_IDS:
        bot.send_message(message.chat.id, f"❌ Akses Ditolak. ID Anda: {message.chat.id} tidak terdaftar sebagai Staff FO.")
        return
    
    url = f"{APP_URL}/staff/dashboard_reservasi"
    try:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🗂️ Buka Dashboard Reservasi", url=url)
        markup.add(btn)
        bot.send_message(message.chat.id, "🗂️ *DASHBOARD RESERVASI (INQUIRY)*\nKlik tombol di bawah untuk melihat request reservasi:", parse_mode='Markdown', reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f"URL Dashboard: {url}")

def logic_cek_pembayaran(message):
    print(f"DEBUG: /cek_pembayaran accessed by {message.chat.id}")
    if message.chat.id not in STAFF_FO_IDS:
        bot.send_message(message.chat.id, f"❌ Akses Ditolak. ID Anda: {message.chat.id} tidak terdaftar sebagai Staff FO.")
        return
        
    dashboard_url = f"{APP_URL}/staff/dashboard"
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🖥️ Buka Dashboard Staff", url=dashboard_url)
    markup.add(btn)
    
    bot.send_message(message.chat.id, 
                     "📊 *STAFF DASHBOARD (BOOKING)*\n\n"
                     "Gunakan dashboard ini untuk:\n"
                     "✅ Cek Status Pembayaran (Pending/Paid)\n"
                     "❌ Membatalkan Booking\n"
                     "📝 Melihat Detail Booking Tamu",
                     parse_mode='Markdown', reply_markup=markup)

def logic_date_reservasi(message):
    print(f"DEBUG: /date_reservasi accessed by {message.chat.id}")
    if message.chat.id not in STAFF_FO_IDS:
        bot.send_message(message.chat.id, f"❌ Akses Ditolak. ID Anda: {message.chat.id} tidak terdaftar sebagai Staff FO.")
        return
        
    calendar_url = f"{APP_URL}/date_reservasi"
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📅 Tampilkan Kalender", url=calendar_url)
    markup.add(btn)
    
    bot.send_message(message.chat.id, "🗓 *KALENDER RESERVASI*\nKlik tombol di bawah untuk melihat ketersediaan tanggal.", parse_mode='Markdown', reply_markup=markup)

def logic_cek_booking(message):
    print(f"DEBUG: /cek_booking accessed by {message.chat.id}")
    
    # Validasi: Hanya Staff FO yang boleh akses
    if message.chat.id not in STAFF_FO_IDS:
        print(f"DEBUG: Access denied for {message.chat.id}")
        bot.send_message(message.chat.id, f"❌ Akses Ditolak. ID Anda: {message.chat.id} tidak terdaftar sebagai Staff FO.")
        return

    try:
        response = supabase.table('bookings').select('resi, nama, tipe, harga, chat_id, qris_status, phone').eq('category', 'booking').order('created_at', desc=True).limit(5).execute()
        bookings = response.data
        print(f"DEBUG: Found {len(bookings)} bookings")
    except Exception as e:
        print(f"DEBUG: Database error: {e}")
        bot.send_message(message.chat.id, f"❌ Database Error: {e}")
        return

    if not bookings:
        bot.send_message(message.chat.id, "📭 Belum ada data booking terbaru.")
        return

    bot.send_message(message.chat.id, "📋 *DAFTAR 5 BOOKING TERBARU*\nSilahkan pilih tamu untuk dikirimkan QRIS Pembayaran:", parse_mode='Markdown')

    for b in bookings:
        try:
            resi = b['resi']
            nama = b['nama']
            tipe = b['tipe']
            harga = b['harga']
            guest_chat_id = b['chat_id']
            qris_status = b['qris_status']
            phone = b['phone']

            # Tentukan status icon
            status_icon = "✅ SUDAH DIKIRIM" if qris_status == 'sent' else "❌ BELUM DIKIRIM"
            source = "📱 Telegram" if guest_chat_id != 'unknown' else "🌐 Browser"
            
            text = f"👤 *{nama}*\n🆔 `{resi}`\n🔄 Sumber: {source}\n🛏 {tipe}\n💰 Rp {harga}\n📊 Status QRIS: {status_icon}"
            
            markup = types.InlineKeyboardMarkup()
            
            # Siapkan Link WA
            has_phone = phone and phone != '-'
            clean_phone = ''
            if has_phone:
                clean_phone = ''.join(filter(str.isdigit, str(phone)))
                if clean_phone.startswith('0'):
                    clean_phone = '62' + clean_phone[1:]
            
            # Logic Tombol
            if qris_status != 'sent':
                if guest_chat_id != 'unknown':
                    # Telegram User
                    markup.add(types.InlineKeyboardButton("📤 Kirim QRIS (Telegram)", callback_data=f"qris_{resi}_{guest_chat_id}"))
                    markup.add(types.InlineKeyboardButton("💬 Chat Tamu (Telegram)", url=f"tg://user?id={guest_chat_id}"))
                else:
                    # Web User (WhatsApp)
                    # Redirect ke WA Helper
                    markup.add(types.InlineKeyboardButton("📤 Kirim QRIS (WhatsApp)", url=f"{APP_URL}/wa_redirect?resi={resi}&id={message.chat.id}&mid=0")) 
                    markup.add(types.InlineKeyboardButton("💬 Chat Tamu (WhatsApp)", url=f"https://wa.me/{clean_phone}"))
            else:
                # Already sent
                if guest_chat_id != 'unknown':
                    markup.add(types.InlineKeyboardButton("💬 Chat Tamu (Telegram)", url=f"tg://user?id={guest_chat_id}"))
                else:
                    markup.add(types.InlineKeyboardButton("💬 Chat Tamu (WhatsApp)", url=f"https://wa.me/{clean_phone}"))

            # Send Message AND Markup together
            bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)
            
        except Exception as e:
            print(f"DEBUG: Error sending booking {resi}: {e}")

class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Laporan dibuat oleh Sentra Guest OS | SGO V1.0 - Halaman {self.page_no()}', 0, 0, 'C')

def logic_cetak_lap_harian(message):
    # Validasi: Hanya Staff FO
    if message.chat.id not in STAFF_FO_IDS:
        bot.send_message(message.chat.id, f"❌ Akses Ditolak. ID Anda: {message.chat.id} tidak terdaftar sebagai Staff FO.")
        return

    bot.send_message(message.chat.id, "⏳ Sedang membuat Laporan Booking Harian...")
    
    try:
        # 1. Ambil Data Booking Harian (Berdasarkan Resi Hari Ini)
        today_str = datetime.now().strftime('%y%m%d') # Format YYMMDD sesuai Resi NEXA-YYMMDD...
        date_display = datetime.now().strftime('%d %B %Y')
        
        try:
            response = supabase.table('bookings').select('resi, nama, phone, tgl, tipe, orang, via').like('resi', f'NEXA-{today_str}%').execute()
            bookings = response.data
        except Exception as e:
             bot.send_message(message.chat.id, "❌ Database Error")
             return
        
        if not bookings:
            bot.send_message(message.chat.id, "📭 Belum ada data booking untuk hari ini.")
            return

        # 2. Buat PDF
        pdf = PDF(orientation='L', unit='mm', format='A4') # Landscape
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Judul
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 8, "Laporan Booking Harian", 0, 1, 'C')
        
        # Sub-judul
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, "Mercure Hotel Bandung Nexa Supratman", 0, 1, 'C')
        
        # Tanggal Cetak
        pdf.set_font("Arial", 'I', 9)
        pdf.cell(0, 8, f"Tanggal Cetak: {date_display}", 0, 1, 'C')
        pdf.ln(5)
        
        # Header Tabel
        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(200, 220, 255)
        
        # Kolom: No. Resi, Nama Tamu, Tgl Check-in, Tipe Room, Jml Org, Via
        # Lebar total A4 Landscape ~277mm (dikurangi margin)
        # Center the table: Total width 240mm. Page width 297mm. Margin (297-240)/2 = 28.5mm
        # Set margin left to center table
        pdf.set_left_margin(28)
        
        col_widths = [40, 50, 40, 60, 20, 30] 
        headers = ["No. Resi", "Nama Tamu", "Check-in", "Tipe Room", "Org", "Via"]
        
        for i in range(len(headers)):
            pdf.cell(col_widths[i], 8, headers[i], 1, 0, 'C', 1)
        pdf.ln()
        
        # Isi Tabel
        pdf.set_font("Arial", '', 9)
        pdf.set_fill_color(255, 255, 255)
        
        for b in bookings:
            # Unpack sesuai query (resi, nama, phone, tgl, tipe, orang, via)
            resi = b['resi']
            nama = b['nama']
            phone = b['phone']
            tgl = b['tgl']
            tipe = b['tipe']
            orang = b['orang']
            via = b['via']
            
            # Clean data if necessary
            # Nama (Truncate if too long)
            nama_disp = (nama[:25] + '..') if len(nama) > 25 else nama
            
            # Format Source (Via)
            via_disp = "Telegram" if via == 'telegram' else "Website"
            
            pdf.cell(col_widths[0], 8, str(resi), 1, 0, 'C')
            pdf.cell(col_widths[1], 8, nama_disp, 1)
            pdf.cell(col_widths[2], 8, str(tgl), 1, 0, 'C')
            pdf.cell(col_widths[3], 8, str(tipe), 1)
            pdf.cell(col_widths[4], 8, str(orang), 1, 0, 'C')
            pdf.cell(col_widths[5], 8, via_disp, 1, 0, 'C')
            pdf.ln()
            
        # Simpan File Sementara (Gunakan /tmp/ untuk Vercel)
        filename = f"/tmp/Laporan_Harian_{today_str}.pdf"
        pdf.output(filename)
        
        # 3. Kirim File
        with open(filename, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"📄 Laporan Booking Harian ({date_display})")
            
        # Hapus File Sementara
        try:
            os.remove(filename)
        except:
            pass
            
    except Exception as e:
        print(f"Error cetak laporan: {e}")
        bot.send_message(message.chat.id, f"❌ Gagal membuat laporan: {e}")

def logic_cetak_laporan_reservasi(message):
    if message.chat.id not in STAFF_FO_IDS:
        bot.send_message(message.chat.id, f"❌ Akses Ditolak. ID Anda: {message.chat.id} tidak terdaftar sebagai Staff FO.")
        return
    bot.send_message(message.chat.id, "⏳ Sedang membuat Laporan Reservasi Harian...")
    try:
        today_str = datetime.now().strftime('%y%m%d')
        date_display = datetime.now().strftime('%d %B %Y')
        
        try:
            response = supabase.table('bookings').select('resi, nama, tgl, tipe, jml_kamar, orang, status, phone').eq('category', 'reservation').like('resi', f'RSV-{today_str}%').execute()
            rows = response.data
        except Exception as e:
            bot.send_message(message.chat.id, "❌ Database Error")
            return
        
        if not rows:
            bot.send_message(message.chat.id, "📭 Belum ada data reservasi untuk hari ini.")
            return
        
        pdf = PDF(orientation='L', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_left_margin(28)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 8, "Laporan Reservasi", 0, 1, 'C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, "Mercure Hotel Bandung Nexa Supratman", 0, 1, 'C')
        pdf.set_font("Arial", 'I', 9)
        pdf.cell(0, 8, f"Tanggal Cetak: {date_display}", 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(200, 220, 255)
        col_widths = [30, 50, 30, 35, 40, 30, 25]
        headers = ["No. Resi", "Nama PIC", "Tanggal", "Jenis", "Detail", "No. HP", "Status"]
        for i in range(len(headers)):
            pdf.cell(col_widths[i], 8, headers[i], 1, 0, 'C', 1)
        pdf.ln()
        
        pdf.set_font("Arial", '', 9)
        pdf.set_fill_color(255, 255, 255)
        for r in rows:
            resi = r['resi']
            nama = r['nama']
            tgl = r['tgl']
            tipe = r['tipe']
            jml_kamar = r['jml_kamar']
            orang = r['orang']
            status = r['status']
            phone = r['phone']
            nama_disp = (nama[:25] + '..') if len(nama) > 25 else nama
            detail = ""
            if tipe == 'Kamar':
                detail = f"{jml_kamar} Kamar"
            elif tipe == 'Meeting' or tipe == 'Birthday':
                detail = f"{orang} Pax"
            elif tipe == 'Wedding':
                detail = f"{orang} Pax, {jml_kamar} Kamar"
            else:
                detail = "-"
            
            status_disp = "CONFIRMED" if status == 'confirmed' else ("CANCELLED" if status == 'cancelled' else "RESERVED")
            
            pdf.cell(col_widths[0], 8, str(resi), 1, 0, 'C')
            pdf.cell(col_widths[1], 8, nama_disp, 1, 0, 'L')
            pdf.cell(col_widths[2], 8, str(tgl), 1, 0, 'C')
            pdf.cell(col_widths[3], 8, str(tipe), 1, 0, 'L')
            pdf.cell(col_widths[4], 8, str(detail), 1, 0, 'L')
            pdf.cell(col_widths[5], 8, str(phone or '-'), 1, 0, 'L')
            pdf.cell(col_widths[6], 8, status_disp, 1, 0, 'C')
            pdf.ln()
        
        filename = f"/tmp/Laporan_Reservasi_{today_str}.pdf"
        pdf.output(filename)
        
        with open(filename, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"📄 Laporan Reservasi Harian ({date_display})")
        try:
            os.remove(filename)
        except:
            pass
    except Exception as e:
        print(f"Error cetak laporan reservasi: {e}")
        bot.send_message(message.chat.id, f"❌ Gagal membuat laporan reservasi: {e}")

# (Moved to Staff Features Section)

# Hapus handle_wa_qris lama karena sudah diganti endpoint redirect
# (Sudah dihapus di kode baru ini)

@bot.callback_query_handler(func=lambda call: call.data.startswith('qris_') and not call.data.startswith('qris_email_'))
def handle_qris(call):
    try:
        parts = call.data.split('_')
        if len(parts) < 3:
            return
            
        resi = parts[1]
        guest_chat_id = parts[2]
        
        # Validasi ID Tamu
        if guest_chat_id == 'unknown' or not guest_chat_id:
            bot.answer_callback_query(call.id, "Data tamu tidak valid ❌")
            bot.send_message(call.message.chat.id, f"❌ Tidak dapat mengirim QRIS. Tamu booking melalui browser/bukan Telegram (ID: {guest_chat_id}).")
            return

        guest_name = None
        try:
            response = supabase.table('bookings').select('nama').eq('resi', resi).execute()
            if response.data:
                guest_name = response.data[0]['nama']
        except Exception as _:
            guest_name = None

        # Cek file QRIS
        base_dir = os.path.dirname(os.path.abspath(__file__))
        qris_path = os.path.join(base_dir, 'qris.jpeg')
        
        if not os.path.exists(qris_path):
            bot.answer_callback_query(call.id, "File QRIS hilang! ❌")
            bot.send_message(call.message.chat.id, "❌ File 'qris.jpeg' tidak ditemukan di server.")
            return

        # Kirim ke Tamu
        try:
            with open(qris_path, 'rb') as photo:
                salutation = f"👋 Halo {format_guest_name(guest_name)}," if guest_name else "👋 Halo,"
                caption = (f"{salutation}\n\nTerima kasih telah melakukan reservasi di Mercure Bandung Nexa Supratman.\n"
                           f"🆔 No. Resi: *{resi}*\n\n"
                           "Untuk menyelesaikan pemesanan, mohon lakukan pembayaran melalui Scan QRIS di atas.\n"
                           "Setelah transfer, mohon kirimkan bukti transfer di chat ini.\n\n"
                           "Terima kasih! 🙏")
                bot.send_photo(guest_chat_id, photo, caption=caption, parse_mode='Markdown')
            
            # Konfirmasi ke Staff
            bot.answer_callback_query(call.id, "QRIS Terkirim! ✅")
            bot.send_message(call.message.chat.id, f"✅ QRIS berhasil dikirim ke tamu dengan Resi {resi}.")
            
            # Update status di database
            try:
                supabase.table('bookings').update({'qris_status': 'sent'}).eq('resi', resi).execute()
            except Exception as db_err:
                print(f"Gagal update status QRIS: {db_err}")

            # Update tombol/pesan di chat Staff agar langsung berubah jadi 'Terkirim'
            try:
                # Kita edit tombol di pesan yang diklik tadi
                markup = types.InlineKeyboardMarkup()
                
                # Jika sudah terkirim, sisakan tombol Chat Tamu saja
                if guest_chat_id != 'unknown':
                    btn_chat = types.InlineKeyboardButton("💬 Chat Tamu (Telegram)", url=f"tg://user?id={guest_chat_id}")
                    markup.add(btn_chat)

                # Jika pesan berasal dari /cek_booking (ada teks Status QRIS), kita update teksnya juga
                if "Status QRIS:" in call.message.text:
                    # Reconstruct text dengan status baru
                    lines = call.message.text.split('\n')
                    new_lines = []
                    for line in lines:
                        if "Status QRIS:" in line:
                            new_lines.append("📊 Status QRIS: ✅ SUDAH DIKIRIM")
                        else:
                            new_lines.append(line)
                    new_text = "\n".join(new_lines)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                          text=new_text, reply_markup=markup, parse_mode='Markdown')
                else:
                    # Jika dari notifikasi awal (belum ada teks status), cuma update tombol
                    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            
            except Exception as e:
                print(f"Gagal update UI pesan: {e}")
                
        except telebot.apihelper.ApiTelegramException as e:
            error_msg = str(e)
            if "chat not found" in error_msg:
                bot.send_message(call.message.chat.id, f"❌ Gagal: Tamu belum memulai bot (Start) atau ID salah.\nID: {guest_chat_id}")
            elif "bot was blocked" in error_msg:
                bot.send_message(call.message.chat.id, f"❌ Gagal: Tamu memblokir bot.\nID: {guest_chat_id}")
            else:
                bot.send_message(call.message.chat.id, f"❌ Gagal mengirim QRIS: {e}")
                
    except Exception as e:
        bot.answer_callback_query(call.id, "Gagal mengirim ❌")
        bot.send_message(call.message.chat.id, f"❌ Terjadi kesalahan sistem: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('qris_email_'))
def handle_qris_email(call):
    try:
        # Format: qris_email_{resi}_{guest_chat_id}
        parts = call.data.split('_')
        if len(parts) < 4:
             bot.answer_callback_query(call.id, "Data callback tidak valid ❌")
             return
            
        resi = parts[2]
        guest_chat_id = parts[3]
        
        # Ambil data booking dari DB untuk dapat email
        try:
            response = supabase.table('bookings').select('email, nama, harga, created_at, qris_status').eq('resi', resi).execute()
            if not response.data:
                bot.answer_callback_query(call.id, "Data booking tidak ditemukan ❌")
                return
            row_data = response.data[0]
        except Exception as e:
            bot.answer_callback_query(call.id, "Database Error ❌")
            print(f"DB Error: {e}")
            return
            
        email = row_data['email']
        nama = row_data['nama']
        total_harga = row_data['harga']
        created_at_str = row_data['created_at']
        qris_status = row_data['qris_status']
        
        # Jika sudah terkirim sebelumnya, jangan kirim ulang
        if qris_status == 'sent':
            bot.answer_callback_query(call.id, "QRIS sudah dikirim sebelumnya ✅")
            try:
                # Hapus tombol Kirim QRIS dan sisakan tombol Chat Email
                markup = types.InlineKeyboardMarkup()
                if email and email != '-':
                    btn_chat_email = types.InlineKeyboardButton("📧 Chat Tamu (Email)", url=f"mailto:{email}")
                    markup.add(btn_chat_email)
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            except Exception as ui_err:
                print(f"Error update UI (already sent): {ui_err}")
            return
        
        # Calculate Deadline & Booking Time
        try:
             # created_at might be datetime object or string
             if not created_at_str:
                 booking_dt = datetime.now()
             elif isinstance(created_at_str, datetime):
                 booking_dt = created_at_str
             elif isinstance(created_at_str, str):
                 booking_dt = datetime.strptime(created_at_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
             else:
                 booking_dt = datetime.now() # Fallback
             
             booking_time_str = booking_dt.strftime('%H:%M')
             deadline_dt = booking_dt + timedelta(hours=2)
             deadline_str = deadline_dt.strftime('%H:%M')
        except Exception as e:
             print(f"Error date parsing: {e}")
             booking_time_str = "-"
             deadline_str = "-"
        
        # Cek email valid
        if not email or email == '-' or '@' not in email:
             bot.answer_callback_query(call.id, "Email tamu tidak tersedia/valid ❌")
             conn.close()
             return

        # Kirim Email QRIS (HTML, rata kiri)
        try:
            booking_data = {
                'resi': resi,
                'nama': nama,
                'total_harga': total_harga
            }
            send_qris_email(email, booking_data)
            
            # Update Status di DB
            try:
                supabase.table('bookings').update({'qris_status': 'sent'}).eq('resi', resi).execute()
            except Exception as e:
                print(f"Error updating qris status: {e}")
            
            bot.answer_callback_query(call.id, "Email QRIS Terkirim! ✅")
            bot.send_message(call.message.chat.id, f"✅ Email QRIS berhasil dikirim ke {email} (Resi: {resi}).")
            
            # Update Tombol di Telegram
            try:
                markup = types.InlineKeyboardMarkup()
                btn_chat_email = types.InlineKeyboardButton("📧 Chat Tamu (Email)", url=f"mailto:{email}")
                markup.add(btn_chat_email)
                
                if "Status QRIS:" in call.message.text:
                    lines = call.message.text.split('\n')
                    new_lines = []
                    for line in lines:
                        if "Status QRIS:" in line:
                            new_lines.append("📊 Status QRIS: ✅ SENT VIA EMAIL")
                        else:
                            new_lines.append(line)
                    new_text = "\n".join(new_lines)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                          text=new_text, reply_markup=markup, parse_mode='Markdown')
                else:
                    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            except Exception as ui_err:
                print(f"Error update UI: {ui_err}")
        except Exception as e:
            print(f"Gagal kirim email: {e}")
            bot.answer_callback_query(call.id, "Gagal kirim email ❌")
            bot.send_message(call.message.chat.id, f"❌ Error send email: {e}")
            
    except Exception as e:
        print(f"Error handle_qris_email: {e}")
        bot.answer_callback_query(call.id, "Terjadi kesalahan sistem ❌")

# --- BACKGROUND TASK: AUTO-CANCEL & GEOLOCATION CHECK ---
def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371  # Radius of earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d

def check_expired_bookings():
    print("Background Task Started: Auto-Cancel & Geolocation Check")
    while True:
        try:
            # 1. Cari booking 'pending' yang sudah > 2 jam
            time_threshold = (datetime.now() - timedelta(hours=2)).isoformat()
            
            response = supabase.table('bookings').select('resi, nama, chat_id, lat, lng, created_at, extended').eq('status', 'pending').lt('created_at', time_threshold).execute()
            rows = response.data
            
            for row in rows:
                resi = row['resi']
                nama = row['nama']
                chat_id = row['chat_id']
                lat = row['lat']
                lng = row['lng']
                created_at_str = row['created_at']
                extended = row['extended']
        
                # Parse created_at
                try:
                    if '.' in created_at_str:
                        created_at = datetime.strptime(created_at_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                    else:
                        created_at = datetime.fromisoformat(created_at_str)
                except:
                    created_at = datetime.now() # Fallback

                # Cek Geolocation untuk Extend (Jika belum pernah extended)
                should_extend = False
                
                # Titik Koordinat Hotel Mercure Bandung Nexa Supratman (Hardcoded/From data.py)
                HOTEL_LAT = -6.9088
                HOTEL_LNG = 107.6285
                
                if not extended and lat and lng:
                    # Cek jarak
                    dist = calculate_distance(lat, lng, HOTEL_LAT, HOTEL_LNG)
                    print(f"DEBUG: Booking {resi} expired. Dist: {dist:.2f} km")
                    
                    if dist < 10: # Radius aman 10 km
                        should_extend = True
                
                if should_extend:
                    # EXTEND 30 Menit (Update created_at + 30 menit)
                    new_created_at = created_at + timedelta(minutes=30)
                    supabase.table('bookings').update({'created_at': new_created_at.isoformat(), 'extended': 1}).eq('resi', resi).execute()
                    
                    msg_ext = f"⏳ Booking {resi} ({nama}) diperpanjang 30 menit otomatis karena posisi tamu dekat ({dist:.1f} km)."
                    print(msg_ext)
                    
                    # Notif FO
                    for sid in STAFF_FO_IDS:
                        try:
                            bot.send_message(sid, msg_ext)
                        except: pass
                        
                else:
                    # CANCEL
                    supabase.table('bookings').update({'status': 'cancelled'}).eq('resi', resi).execute()
                    
                    print(f"Booking {resi} ({nama}) dicancel otomatis (Expired > 2 jam).")
                    
                    # Notif Tamu
                    if chat_id != 'unknown':
                        try:
                            bot.send_message(chat_id, f"⚠️ *BOOKING EXPIRED*\nBooking Anda {resi} telah dibatalkan otomatis karena melewati batas waktu hold 2 jam.", parse_mode='Markdown')
                        except: pass
                        
                    # Notif FO
                    for sid in STAFF_FO_IDS:
                        try:
                            bot.send_message(sid, f"❌ Booking {resi} ({nama}) otomatis DIBATALKAN (Expired 2 Jam).")
                        except: pass
            
        except Exception as e:
            print(f"Error background task: {e}")
            
        time.sleep(60) # Cek tiap 1 menit

# --- STAFF DASHBOARD ROUTES ---

@app.route('/staff/dashboard')
def staff_dashboard():
    # Simple protection: Just a secret link or open for now as requested
    # Ideal: Check session/login
    return render_template('staff_dashboard.html', api_endpoint='/staff/api/bookings', dashboard_title='Staff Dashboard - Booking', mode='booking')

import traceback

@app.route('/staff/api/bookings')
def api_bookings():
    print("API Bookings Request Received - NEW VERSION CHECK")
    try:
        response = supabase.table('bookings').select('resi, nama, tipe, tgl, jml_kamar, harga, status, email, via, created_at, orang').eq('category', 'booking').order('created_at', desc=True).limit(50).execute()
        rows = response.data
        
        data = []
        for r in rows:
            # Parse jam booking dari created_at
            jam_booking = '-'
            created_at_val = r.get('created_at')
            try:
                if created_at_val:
                    if '.' in created_at_val:
                         dt = datetime.strptime(created_at_val.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    else:
                         dt = datetime.fromisoformat(created_at_val)
                    jam_booking = dt.strftime('%H:%M')
            except:
                pass

            # Parse Harga safely
            harga_str = "0"
            raw_harga = str(r.get('harga', '0'))
            try:
                import re
                clean_digits = re.sub(r'[^\d]', '', raw_harga)
                if clean_digits:
                    val = float(clean_digits)
                    harga_str = "{:,.0f}".format(val)
                else:
                    harga_str = raw_harga
            except:
                harga_str = raw_harga

            data.append({
                "resi": r['resi'],
                "nama": r['nama'],
                "tipe": r['tipe'],
                "tgl": r['tgl'],
                "jml_kamar": r['jml_kamar'],
                "harga": harga_str,
                "status": r['status'],
                "email": r['email'],
                "via": r['via'],
                "jam_booking": jam_booking,
                "orang": r['orang']
            })
        return jsonify(data)
    except Exception as e:
        print(f"ERROR api_bookings: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/staff/dashboard_reservasi')
def staff_dashboard_reservasi():
    return render_template('staff_dashboard.html', api_endpoint='/staff/api/reservasi', dashboard_title='Staff Dashboard - Reservasi', mode='reservasi')

@app.route('/staff/api/reservasi')
def api_reservasi():
    try:
        response = supabase.table('bookings').select('resi, nama, tipe, tgl, jml_kamar, harga, status, email, via, created_at, orang').eq('category', 'reservation').order('created_at', desc=True).execute()
        rows = response.data
        
        data = []
        for r in rows:
            jam_booking = '-'
            created_at_val = r.get('created_at')
            try:
                if created_at_val:
                    if '.' in created_at_val:
                         dt = datetime.strptime(created_at_val.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    else:
                         dt = datetime.fromisoformat(created_at_val)
                    jam_booking = dt.strftime('%H:%M')
            except:
                pass
            
            harga_str = "0"
            raw_harga = str(r.get('harga', '0'))
            try:
                import re
                clean_digits = re.sub(r'[^\d]', '', raw_harga)
                if clean_digits:
                    val = float(clean_digits)
                    harga_str = "{:,.0f}".format(val)
                else:
                    harga_str = raw_harga
            except:
                harga_str = raw_harga
            
            data.append({
                "resi": r['resi'],
                "nama": r['nama'],
                "tipe": r['tipe'],
                "tgl": r['tgl'],
                "jml_kamar": r['jml_kamar'],
                "harga": harga_str,
                "status": r['status'],
                "email": r['email'],
                "via": r['via'],
                "jam_booking": jam_booking,
                "orang": r['orang']
            })
        return jsonify(data)
    except Exception as e:
        print(f"ERROR api_reservasi: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/date_reservasi')
def date_reservasi():
    response = make_response(render_template('calendar_reservasi.html'))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/api/calendar_events')
def api_calendar_events():
    try:
        month = request.args.get('month')
        year = request.args.get('year')
        
        if not month or not year:
            return jsonify([])
            
        try:
            year_int = int(year)
            month_int = int(month)
            
            # Get last day of month
            last_day = calendar.monthrange(year_int, month_int)[1]
            
            start_date = f"{year_int}-{month_int:02d}-01"
            end_date = f"{year_int}-{month_int:02d}-{last_day}"
            
            # Use Range Filter (gte and lte) instead of Like to prevent Cloudflare/Supabase 500 Error
            response = supabase.table('bookings').select('tgl, tipe, nama').eq('category', 'reservation').gte('tgl', start_date).lte('tgl', end_date).execute()
            rows = response.data
        except Exception as e:
            print(f"Error calendar events db: {e}")
            return jsonify([]), 500
        
        events = []
        for r in rows:
            events.append({
                "tgl": r['tgl'],
                "tipe": r['tipe'],
                "nama": r['nama']
            })
            
        return jsonify(events)
    except Exception as e:
        print(f"Error calendar events: {e}")
        return jsonify([]), 500

@app.route('/staff/api/update_status', methods=['POST'])
def api_update_status():
    try:
        data = request.json
        resi = data.get('resi')
        new_status = data.get('status')
        
        if not resi or not new_status:
            return jsonify({"status": "error", "message": "Missing data"}), 400
            
        try:
            supabase.table('bookings').update({'status': new_status}).eq('resi', resi).execute()
        except Exception as e:
             return jsonify({"status": "error", "message": f"Database error: {e}"}), 500
        
        # Optional: Notify Staff FO on Telegram about status change
        msg = f"📝 Status Booking {resi} diubah menjadi {new_status.upper()} via Dashboard."
        for sid in STAFF_FO_IDS:
            try:
                bot.send_message(sid, msg)
            except: pass
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Invalid payload', 403

@app.route('/init_webhook')
def init_webhook():
    """
    Route khusus untuk inisialisasi Webhook di Vercel.
    Akses URL ini sekali setelah deploy: https://reservasi-hotel-seven.vercel.app/init_webhook
    """
    try:
        bot.remove_webhook()
        time.sleep(0.5)
        
        # Set webhook ke URL Vercel saat ini
        webhook_url = f"{APP_URL}/webhook"
        bot.set_webhook(url=webhook_url)
        
        return f"Webhook successfully set to: {webhook_url}", 200
    except Exception as e:
        return f"Failed to set webhook: {e}", 500

@app.route('/test_db')
def test_db_route():
    try:
        # Test Supabase REST API Connection
        response = supabase.table('bookings').select("count", count='exact').limit(1).execute()
        count = response.count
        return f"Database Connected via REST API! Bookings count: {count}", 200
    except Exception as e:
        return f"Database Connection Failed (REST API): {str(e)}", 500

@app.route('/version')
def version_route():
    return "App Version: 2.4 (Unified Command Handler)", 200

if __name__ == '__main__':
    # init_db() # Disabled for Supabase REST Migration
    print("\n\n=======================================================")
    print(">>> SGO V1.1 LOADED: VERCEL MODE <<<")
    print("=======================================================\n")
    
    # --- SETUP MENU COMMANDS (Optional on startup, better separate) ---
    # ... code setup commands ...

    # Jalankan Flask (Vercel akan menjalankan ini sebagai WSGI app)
    # app.run tidak perlu dipanggil secara eksplisit di Vercel jika menggunakan wsgi handler, 
    # tapi untuk local dev kita tetap butuh.
    
    # Deteksi Environment Vercel
    if os.environ.get('VERCEL'):
         # Di Vercel, kita tidak jalankan infinity_polling
         pass
    else:
         # Local Development
         print(f"Web App running on Local/Dev")
         
         # Jalankan Flask di Thread terpisah
         t = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False))
         t.daemon = True
         t.start()
         
         # Jalankan Polling (HANYA JIKA LOCAL)
         # Jika sudah set webhook ke Vercel, polling lokal mungkin akan konflik atau gagal (conflict error)
         # Jadi idealnya jika migrasi ke Vercel, kita matikan polling lokal dan gunakan ngrok untuk tunnel webhook jika mau debug lokal.
         # Tapi user minta migrasi.
         
         print("Bot is polling (Local Mode)...")
         # Note: Jika webhook sudah diset, polling akan gagal. 
         # Kita akan remove webhook dulu jika running local (opsional), tapi biar aman kita try-except polling
         try:
             bot.remove_webhook()
             time.sleep(1)
             bot.infinity_polling(timeout=10, long_polling_timeout=5)
         except Exception as e:
             print(f"Bot polling error: {e}")

