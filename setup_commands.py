import telebot
from telebot import types

# Token Bot Anda
API_TOKEN = '8556104756:AAGVZJyvrxV4P-yN486BH7K5SR_f8jRZDLw'

# URL Vercel Baru
WEB_APP_URL = 'https://reservasi-hotel-seven.vercel.app' 

bot = telebot.TeleBot(API_TOKEN)
STAFF_FO_IDS = [784633296]

print("--- MEMULAI UPDATE MENU BOT ---")

try:
    # 1. Hapus command lama
    print("1. Menghapus command lama...")
    bot.delete_my_commands(scope=types.BotCommandScopeDefault())
    
    # 2. Set Command Dasar (User Biasa)
    print("2. Setting command dasar...")
    guest_commands = [
        types.BotCommand("start", "Mulai Aplikasi"),
        types.BotCommand("help", "Bantuan Aplikasi")
    ]
    bot.set_my_commands(guest_commands, scope=types.BotCommandScopeDefault())

    # 3. SET MENU BUTTON (Bagian Paling Penting)
    # Ini akan mengubah tombol "Menu" di pojok kiri bawah menjadi membuka Web App Vercel
    print(f"3. Mengarahkan Menu Button ke: {WEB_APP_URL}")
    
    web_app_info = types.WebAppInfo(url=WEB_APP_URL)
    
    # Menggunakan set_chat_menu_button untuk mengubah tombol default
    # Fix: Coba pass 'web_app' sebagai argument type
    bot.set_chat_menu_button(
        menu_button=types.MenuButtonWebApp('web_app', text="Aplikasi Hotel", web_app=web_app_info)
    )

    # 4. Set Command Khusus Staff
    print("4. Setting command khusus staff...")
    staff_commands = [
        types.BotCommand("cek_booking", "📋 Cek Data Booking Tamu"),
        types.BotCommand("cek_pembayaran", "📊 Dashboard Staff FO"),
        types.BotCommand("cetak_lap_harian", "📄 Cetak Laporan Harian (PDF)"),
        types.BotCommand("dashboard_reservasi", "🗂️ Dashboard Reservasi (Inquiry)"),
        types.BotCommand("cetak_laporan_reservasi", "📄 Cetak Laporan Reservasi (PDF)"),
        types.BotCommand("date_reservasi", "📅 Calender Reservasi")
    ]
    
    for staff_id in STAFF_FO_IDS:
        try:
            bot.set_my_commands(staff_commands, scope=types.BotCommandScopeChat(staff_id))
            print(f"   - Command staff diset untuk ID: {staff_id}")
        except Exception as e:
            print(f"   - Gagal set staff {staff_id}: {e}")

    print("\n✅ SELESAI! Konfigurasi bot telah diperbarui.")
    print("------------------------------------------------")
    print("PENTING: Tutup dan buka kembali aplikasi Telegram Anda")
    print("untuk melihat perubahan pada tombol Menu.")
    print("------------------------------------------------")

except Exception as e:
    print(f"\n❌ TERJADI ERROR: {e}")
