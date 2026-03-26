#!/usr/bin/env python3
"""
Fix Database ANORA 9.9 - Hapus database lama dan buat baru
Jalankan di Railway shell
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

# Tambah path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🔧 FIX DATABASE ANORA 9.9")
print("=" * 70)

# Path database
DB_PATH = Path("data/anora.db")
BACKUP_DIR = Path("backups_anora99")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def backup_and_delete():
    """Backup dan hapus database lama"""
    if DB_PATH.exists():
        # Backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"anora99_old_{timestamp}.db"
        
        print(f"\n📦 Backup database lama ke: {backup_path.name}")
        shutil.copy(DB_PATH, backup_path)
        
        size = DB_PATH.stat().st_size / 1024
        print(f"   Size: {size:.2f} KB")
        print(f"   ✅ Backup berhasil")
        
        # Hapus
        print(f"\n🗑️  Menghapus database lama...")
        DB_PATH.unlink()
        print(f"   ✅ Database dihapus")
        
        return True
    else:
        print(f"\n📦 Database tidak ditemukan: {DB_PATH}")
        return False


def create_database():
    """Buat database baru dengan struktur yang benar"""
    print(f"\n🔄 Membuat database baru...")
    
    try:
        # Buat folder data jika belum ada
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Buat koneksi
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # ========== TABEL UTAMA ==========
        
        # anora99_state
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anora99_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # complete_state_99
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complete_state_99 (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                mas_state TEXT NOT NULL,
                nova_state TEXT NOT NULL,
                together_state TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # emotional_state_99
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotional_state_99 (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                sayang REAL NOT NULL,
                rindu REAL NOT NULL,
                trust REAL NOT NULL,
                mood REAL NOT NULL,
                desire REAL NOT NULL,
                arousal REAL NOT NULL,
                tension REAL NOT NULL,
                cemburu REAL NOT NULL,
                kecewa REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # relationship_state_99
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationship_state_99 (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                phase TEXT NOT NULL,
                level INTEGER NOT NULL,
                interaction_count INTEGER NOT NULL,
                milestones TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # conflict_state_99
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conflict_state_99 (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                cemburu REAL NOT NULL,
                kecewa REAL NOT NULL,
                marah REAL NOT NULL,
                sakit_hati REAL NOT NULL,
                is_cold_war INTEGER NOT NULL,
                is_waiting_for_apology INTEGER NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # timeline_99
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timeline_99 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                kejadian TEXT NOT NULL,
                lokasi_type TEXT NOT NULL,
                lokasi_detail TEXT NOT NULL,
                aktivitas_nova TEXT NOT NULL,
                aktivitas_mas TEXT NOT NULL,
                perasaan TEXT NOT NULL,
                pakaian_nova TEXT NOT NULL,
                pakaian_mas TEXT NOT NULL,
                pesan_mas TEXT,
                pesan_nova TEXT
            )
        ''')
        
        # short_term_memory_99
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS short_term_memory_99 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                kejadian TEXT NOT NULL,
                lokasi_type TEXT NOT NULL,
                lokasi_detail TEXT NOT NULL,
                aktivitas_nova TEXT NOT NULL,
                aktivitas_mas TEXT NOT NULL,
                perasaan TEXT NOT NULL,
                pakaian_nova TEXT NOT NULL,
                pakaian_mas TEXT NOT NULL,
                pesan_mas TEXT,
                pesan_nova TEXT
            )
        ''')
        
        # long_term_memory_99
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory_99 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipe TEXT NOT NULL,
                judul TEXT NOT NULL,
                konten TEXT NOT NULL,
                perasaan TEXT,
                timestamp REAL NOT NULL
            )
        ''')
        
        # current_state_99
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS current_state_99 (
                id INTEGER PRIMARY KEY,
                lokasi_type TEXT NOT NULL,
                lokasi_detail TEXT NOT NULL,
                aktivitas_nova TEXT NOT NULL,
                aktivitas_mas TEXT NOT NULL,
                pakaian_nova TEXT NOT NULL,
                pakaian_mas TEXT NOT NULL,
                mood_nova TEXT NOT NULL,
                mood_mas TEXT NOT NULL,
                feelings TEXT NOT NULL,
                relationship TEXT NOT NULL,
                complete_state TEXT,
                updated_at REAL NOT NULL
            )
        ''')
        
        # conversation_99
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_99 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                state_snapshot TEXT
            )
        ''')
        
        # location_visits_99
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS location_visits_99 (
                id TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                visit_count INTEGER DEFAULT 1,
                last_visit REAL NOT NULL
            )
        ''')
        
        # ========== INDEXES ==========
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timeline_99_time ON timeline_99(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_short_term_99_time ON short_term_memory_99(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_long_term_99_tipe ON long_term_memory_99(tipe)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_99_time ON conversation_99(timestamp)')
        
        # ========== DATA AWAL ==========
        
        # Complete state awal
        import json
        import time
        
        default_complete = {
            'mas': {
                'clothing': {'top': 'kaos', 'bottom': 'celana pendek', 'boxer': True, 'last_update': time.time()},
                'position': {'state': None, 'detail': None, 'last_update': 0},
                'activity': {'main': 'santai', 'detail': None, 'last_update': 0},
                'location': {'room': 'kamar', 'detail': None, 'last_update': 0},
                'holding': {'object': None, 'detail': None, 'last_update': 0},
                'status': {'mood': 'netral', 'need': None, 'last_update': 0}
            },
            'nova': {
                'clothing': {'hijab': True, 'top': 'daster rumah motif bunga', 'bra': True, 'cd': True, 'last_update': time.time()},
                'position': {'state': None, 'detail': None, 'last_update': 0},
                'activity': {'main': 'santai', 'detail': None, 'last_update': 0},
                'location': {'room': 'kamar', 'detail': None, 'last_update': 0},
                'holding': {'object': None, 'detail': None, 'last_update': 0},
                'status': {'mood': 'malu-malu', 'need': None, 'last_update': 0}
            },
            'together': {
                'location': 'kamar',
                'distance': None,
                'atmosphere': 'santai',
                'last_action': None,
                'pending_action': None,
                'confirmed_topics': [],
                'asked_count': 0,
                'last_question': '',
                'last_update': time.time()
            }
        }
        
        cursor.execute(
            "INSERT OR REPLACE INTO complete_state_99 (id, mas_state, nova_state, together_state, updated_at) VALUES (1, ?, ?, ?, ?)",
            (json.dumps(default_complete['mas']), json.dumps(default_complete['nova']), 
             json.dumps(default_complete['together']), time.time())
        )
        
        # Emotional state awal
        cursor.execute(
            "INSERT OR REPLACE INTO emotional_state_99 (id, sayang, rindu, trust, mood, desire, arousal, tension, cemburu, kecewa, updated_at) "
            "VALUES (1, 50, 0, 50, 0, 0, 0, 0, 0, 0, ?)",
            (time.time(),)
        )
        
        # Relationship state awal
        cursor.execute(
            "INSERT OR REPLACE INTO relationship_state_99 (id, phase, level, interaction_count, milestones, updated_at) "
            "VALUES (1, 'stranger', 1, 0, '{}', ?)",
            (time.time(),)
        )
        
        # Conflict state awal
        cursor.execute(
            "INSERT OR REPLACE INTO conflict_state_99 (id, cemburu, kecewa, marah, sakit_hati, is_cold_war, is_waiting_for_apology, updated_at) "
            "VALUES (1, 0, 0, 0, 0, 0, 0, ?)",
            (time.time(),)
        )
        
        conn.commit()
        conn.close()
        
        # Cek hasil
        size = DB_PATH.stat().st_size / 1024
        print(f"   ✅ Database baru berhasil dibuat!")
        print(f"   📁 Path: {DB_PATH}")
        print(f"   📊 Size: {size:.2f} KB")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 70)
    print("🔧 FIX DATABASE ANORA 9.9")
    print("=" * 70)
    
    # Step 1: Backup & Hapus
    backup_and_delete()
    
    # Step 2: Buat baru
    success = create_database()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ DATABASE FIX BERHASIL!")
        print("=" * 70)
        print("\n📌 Langkah selanjutnya:")
        print("   1. Restart bot: railway up")
        print("   2. Kirim /nova untuk mulai ngobrol")
        print("   3. Error Milestone akan hilang")
    else:
        print("❌ DATABASE FIX GAGAL!")
        print("=" * 70)
        print("\n📌 Coba jalankan manual:")
        print("   rm -f data/anora.db")
        print("   railway up")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
