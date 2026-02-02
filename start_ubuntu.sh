#!/bin/bash

# Script Otomatis untuk Menjalankan Nexa Hotel Bot di Ubuntu/Linux
# Mengatasi masalah "externally-managed-environment" dan dependencies

echo "=========================================="
echo "   NEXA HOTEL BANDUNG - UBUNTU LAUNCHER   "
echo "=========================================="

# 1. Cek apakah Python3 terinstall
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 tidak ditemukan!"
    echo "   Silahkan install dengan: sudo apt update && sudo apt install python3 python3-venv python3-pip -y"
    exit 1
fi

# 2. Reset Virtual Environment (Agar bersih dari error sebelumnya)
if [ -d "venv" ]; then
    echo "🧹 Membersihkan environment lama..."
    rm -rf venv
fi

# 3. Buat Virtual Environment Baru
echo "📦 Membuat Virtual Environment (venv)..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Gagal membuat venv. Pastikan python3-venv terinstall."
    echo "   Run: sudo apt install python3-venv"
    exit 1
fi

# 4. Install Dependencies
echo "⬇️  Menginstall library (Flask, Telebot, FPDF, dll)..."
./venv/bin/pip install --upgrade pip -v
if [ -f "requirements.txt" ]; then
    ./venv/bin/pip install -r requirements.txt -v
    if [ $? -ne 0 ]; then
        echo "❌ Gagal menginstall library!"
        exit 1
    fi
else
    echo "❌ File requirements.txt tidak ditemukan!"
    exit 1
fi

# 5. Jalankan Aplikasi
echo "------------------------------------------"
echo "🚀 MENJALANKAN APLIKASI..."
echo "   Tekan Ctrl+C untuk berhenti."
echo "------------------------------------------"
./venv/bin/python app.py
