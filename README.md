# Panduan Instalasi & Menjalankan (Windows & Ubuntu)

## 1. Persiapan (Windows & Ubuntu)
Pastikan Anda sudah menginstal **Python 3** di komputer Anda.

### Install Library Python
Jalankan perintah berikut di Terminal / Command Prompt:
```bash
pip install -r requirements.txt
```
*(Jika di Ubuntu/Mac gunakan `pip3` jika `pip` tidak terdeteksi)*

---

## 2. Cara Menjalankan di Ubuntu (Linux)

**Langkah 1: Siapkan Terminal**
Buka terminal Ubuntu dan arahkan ke folder project ini.

**Langkah 2: Install Dependencies**
```bash
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt
```

**Langkah 3: Install & Jalankan Ngrok**
Jika belum punya Ngrok di Ubuntu:
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update
sudo apt install ngrok
```
Lalu jalankan Ngrok dengan domain Anda:
```bash
ngrok http --url=pauletta-nonrevertive-finally.ngrok-free.dev 5000
```

**Langkah 4: Jalankan Program Bot**
Buka terminal baru (Terminal ke-2), lalu jalankan:
```bash
python3 app.py
```

---

## 3. Cara Menjalankan di Windows

**Terminal 1 (Ngrok):**
```powershell
ngrok http --url=pauletta-nonrevertive-finally.ngrok-free.dev 5000
```

**Terminal 2 (Program Bot):**
```powershell
python app.py
```

---

## Catatan Penting
- Pastikan **Ngrok** dan **app.py** berjalan bersamaan.
- Jika Bot tidak merespon, cek apakah URL Ngrok di `app.py` sudah sesuai dengan yang berjalan di terminal Ngrok.
