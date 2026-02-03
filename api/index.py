import os
import sys

# Tambahkan direktori parent ke system path agar bisa import app.py dari root
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import Flask app dari app.py di root
from app import app

# Vercel serverless function entry point
# Flask app object is implicitly handled by Vercel when exposed as 'app'
