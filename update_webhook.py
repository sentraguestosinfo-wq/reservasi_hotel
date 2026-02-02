import telebot
import time

API_TOKEN = '8556104756:AAGVZJyvrxV4P-yN486BH7K5SR_f8jRZDLw'
bot = telebot.TeleBot(API_TOKEN)

# URL Vercel baru + Route Webhook yang baru saja kita buat di app.py
VERCEL_WEBHOOK_URL = 'https://reservasi-hotel-seven.vercel.app/webhook'

print("--- CEK & UPDATE WEBHOOK ---")

try:
    # 1. Cek Info Saat Ini
    info = bot.get_webhook_info()
    print(f"Current Webhook URL: {info.url}")
    print(f"Pending Updates: {info.pending_update_count}")
    
    # 2. Update ke Vercel
    if info.url != VERCEL_WEBHOOK_URL:
        print(f"\nUpdating Webhook to: {VERCEL_WEBHOOK_URL}")
        
        # Hapus dulu biar bersih
        bot.remove_webhook()
        time.sleep(1)
        
        # Set baru
        success = bot.set_webhook(url=VERCEL_WEBHOOK_URL)
        if success:
            print("✅ Webhook BERHASIL di-update ke Vercel!")
        else:
            print("❌ Gagal set webhook.")
    else:
        print("\n✅ Webhook sudah mengarah ke Vercel yang benar.")

except Exception as e:
    print(f"❌ Error: {e}")
