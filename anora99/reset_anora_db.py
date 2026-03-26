#!/usr/bin/env python3
"""
Reset Database ANORA 9.9
Hapus database lama - biarkan bot membuat baru saat restart
"""

import os
import sys
import shutil
from pathlib import Path

# =============================================================================
# KONFIGURASI
# =============================================================================

# Path database
DB_PATH = Path("data/anora.db")
BACKUP_DIR = Path("backups_anora99")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("🗄️  RESET DATABASE ANORA 9.9")
print("=" * 60)


def reset_database():
    """Reset database - hapus file, backup dulu"""
    
    print(f"\n📁 Database path: {DB_PATH}")
    
    if not DB_PATH.exists():
        print("\n❌ Database tidak ditemukan!")
        print("   (Sudah tidak ada atau belum pernah dibuat)")
        return False
    
    # ========== 1. BACKUP ==========
    import time
    timestamp = int(time.time())
    backup_path = BACKUP_DIR / f"anora99_old_{timestamp}.db"
    
    print(f"\n📦 Backup database lama ke: {backup_path.name}")
    shutil.copy(DB_PATH, backup_path)
    
    size_kb = DB_PATH.stat().st_size / 1024
    print(f"   Size: {size_kb:.2f} KB")
    print(f"   ✅ Backup berhasil")
    
    # ========== 2. HAPUS ==========
    print(f"\n🗑️  Menghapus database lama...")
    DB_PATH.unlink()
    print(f"   ✅ Database dihapus")
    
    return True


def main():
    print("=" * 60)
    print("🗄️  RESET DATABASE ANORA 9.9")
    print("=" * 60)
    print()
    print("⚠️  PERINGATAN!")
    print("   Database akan dihapus.")
    print("   Backup akan dibuat terlebih dahulu.")
    print()
    print("   Tekan ENTER untuk melanjutkan...")
    
    try:
        input()
    except:
        print("\n   (Auto proceed in 5 seconds...)")
        import time
        time.sleep(5)
    
    success = reset_database()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ RESET DATABASE BERHASIL!")
        print("=" * 60)
        print("\n📌 LANGKAH SELANJUTNYA:")
        print("   1. Restart bot di Railway")
        print("   2. Bot akan membuat database baru")
        print("   3. Error Milestone akan hilang")
        print()
        print("   Cara restart:")
        print("   - Railway Dashboard -> Deploy -> Restart")
        print("   - Atau: railway up")
    else:
        print("⚠️  DATABASE TIDAK DITEMUKAN")
        print("=" * 60)
        print("\n📌 Tidak perlu reset.")
        print("   Database mungkin belum pernah dibuat.")
        print("   Restart bot saja untuk membuat database baru.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Dibatalkan.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
