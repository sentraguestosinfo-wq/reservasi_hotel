# Cara Menjalankan di Terminal Ubuntu

Program ini sudah dirancang untuk kompatibel sepenuhnya dengan Ubuntu/Linux.
Kami telah menyediakan script otomatis `start_ubuntu.sh` untuk memudahkan instalasi dan eksekusi.

## 1. Cara Paling Mudah (Rekomendasi)
Cukup jalankan script launcher yang sudah disediakan. Script ini akan otomatis membuat environment, install library, dan menjalankan aplikasi.

1. Buka Terminal di folder project.
2. Beri izin eksekusi pada script:
   ```bash
   chmod +x start_ubuntu.sh
   ```
3. Jalankan script:
   ```bash
   ./start_ubuntu.sh
   ```

Script ini otomatis menangani masalah "externally-managed-environment" yang sering terjadi di Ubuntu versi baru.

---

## 2. Cara Manual (Alternatif)
Jika Anda ingin menjalankannya langkah demi langkah:

### a. Persiapan Sistem
Pastikan Python 3, Venv, dan PIP sudah terinstall:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

### b. Buat & Aktifkan Virtual Environment
Wajib dilakukan untuk menghindari error permission/system package.
```bash
python3 -m venv venv
source venv/bin/activate
```

### c. Instalasi Dependensi
Install library yang dibutuhkan (Flask, Telebot, FPDF, dll) ke dalam venv:
```bash
pip install -r requirements.txt
```

### d. Menjalankan Aplikasi
Jalankan program:
```bash
python app.py
```

---

## 3. Konfigurasi Ngrok (Penting!)
Karena program berjalan di Ubuntu, Anda perlu memastikan Ngrok juga berjalan di Ubuntu tersebut agar bisa diakses publik.

1. Download Ngrok untuk Linux (via apt/snap/zip).
2. Jalankan Ngrok di terminal **terpisah** (tab baru):
   ```bash
   ngrok http --domain=pauletta-nonrevertive-finally.ngrok-free.dev 5000
   ```
   *(Pastikan domain sesuai dengan yang ada di app.py)*

## Troubleshooting Umum
- **Error `ModuleNotFoundError`**: Artinya Anda belum mengaktifkan venv atau belum `pip install`. Gunakan cara no 1 saja biar aman.
- **Error `Address already in use`**: Port 5000 sedang dipakai. Matikan proses python lama dengan `pkill python` atau cari PID-nya.
- **Error `Permission denied`**: Jangan lupa `chmod +x start_ubuntu.sh`.
