# fix_time_data.py
import sqlite3
import os
from pathlib import Path

# Buat direktori data
Path("data").mkdir(parents=True, exist_ok=True)

# Path database
db_path = Path("data/amoria.db")

print(f"Database path: {db_path.absolute()}")

# Cek apakah database ada
if not db_path.exists():
    print("Database belum ada, membuat database kosong...")
    # Buat database kosong
    conn = sqlite3.connect(str(db_path))
    conn.close()
    print("Database created")

try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Cek tabel state_tracker
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='state_tracker'")
    if not cursor.fetchone():
        print("Tabel state_tracker belum ada, membuat...")
        cursor.execute('''
            CREATE TABLE state_tracker (
                registration_id TEXT PRIMARY KEY,
                time_data TEXT
            )
        ''')
        conn.commit()
        print("Tabel state_tracker dibuat")
    
    # Cek kolom yang ada
    cursor.execute("PRAGMA table_info(state_tracker)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Existing columns: {columns}")
    
    # Tambah kolom time_data
    if 'time_data' not in columns:
        print("Adding time_data column...")
        cursor.execute("ALTER TABLE state_tracker ADD COLUMN time_data TEXT")
        conn.commit()
        print("✅ time_data column added")
    else:
        print("✅ time_data already exists")
    
    # Verifikasi
    cursor.execute("PRAGMA table_info(state_tracker)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Final columns: {columns}")
    
    conn.close()
    
    print("\n✅ FIX COMPLETE! Restart bot now.")
    
except Exception as e:
    print(f"Error: {e}")
