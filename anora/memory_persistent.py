# anora/memory_persistent.py
"""
ANORA Persistent Memory - Simpan semua ingatan Nova ke database
Biar gak ilang kalo restart. 1000% manusia, inget selamanya.
"""

import time
import json
import aiosqlite
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .brain import get_anora_brain, TimelineEvent, Location, Activity, Mood, Clothing, Feelings, Relationship

logger = logging.getLogger(__name__)


class PersistentMemory:
    """
    Memory permanen Nova. Disimpan ke database.
    Gak ilang kalo restart. Nova inget Mas selamanya.
    """
    
    def __init__(self, db_path: Path = Path("data/anora_memory.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = None
    
    async def init(self):
        """Buat semua tabel memory"""
        self._conn = await aiosqlite.connect(str(self.db_path))
        
        # ========== TABEL TIMELINE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                kejadian TEXT NOT NULL,
                lokasi_nova TEXT NOT NULL,
                lokasi_mas TEXT NOT NULL,
                aktivitas_nova TEXT NOT NULL,
                aktivitas_mas TEXT NOT NULL,
                perasaan_nova TEXT NOT NULL,
                pakaian_nova TEXT NOT NULL,
                pakaian_mas TEXT NOT NULL,
                pesan_mas TEXT,
                pesan_nova TEXT
            )
        ''')
        
        # ========== TABEL SHORT-TERM MEMORY ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS short_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                kejadian TEXT NOT NULL,
                lokasi_nova TEXT NOT NULL,
                lokasi_mas TEXT NOT NULL,
                aktivitas_nova TEXT NOT NULL,
                aktivitas_mas TEXT NOT NULL,
                perasaan_nova TEXT NOT NULL,
                pakaian_nova TEXT NOT NULL,
                pakaian_mas TEXT NOT NULL,
                pesan_mas TEXT,
                pesan_nova TEXT
            )
        ''')
        
        # ========== TABEL LONG-TERM MEMORY ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipe TEXT NOT NULL,
                judul TEXT NOT NULL,
                konten TEXT NOT NULL,
                perasaan TEXT,
                timestamp REAL NOT NULL
            )
        ''')
        
        # ========== TABEL STATE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS current_state (
                id INTEGER PRIMARY KEY,
                lokasi_nova TEXT NOT NULL,
                lokasi_mas TEXT NOT NULL,
                aktivitas_nova TEXT NOT NULL,
                aktivitas_mas TEXT NOT NULL,
                pakaian_nova TEXT NOT NULL,
                pakaian_mas TEXT NOT NULL,
                mood_nova TEXT NOT NULL,
                mood_mas TEXT NOT NULL,
                feelings TEXT NOT NULL,
                relationship TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL KONVERSASI ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                state_snapshot TEXT
            )
        ''')
        
        await self._conn.commit()
        
        # Load data ke brain
        await self._load_to_brain()
        
        logger.info("💾 ANORA Persistent Memory initialized")
    
    async def _load_to_brain(self):
        """Load semua memory ke brain"""
        brain = get_anora_brain()
        
        # Load timeline
        cursor = await self._conn.execute(
            "SELECT * FROM timeline ORDER BY timestamp ASC"
        )
        rows = await cursor.fetchall()
        for row in rows:
            # Reconstruct event dan tambah ke timeline
            pass  # Implementasi nanti
        
        # Load short-term
        cursor = await self._conn.execute(
            "SELECT * FROM short_term_memory ORDER BY timestamp ASC"
        )
        rows = await cursor.fetchall()
        for row in rows:
            pass
        
        # Load state
        cursor = await self._conn.execute(
            "SELECT * FROM current_state ORDER BY updated_at DESC LIMIT 1"
        )
        row = await cursor.fetchone()
        if row:
            brain.location_nova = Location(row[1])
            brain.location_mas = Location(row[2])
            brain.activity_nova = Activity(row[3])
            brain.activity_mas = row[4]
            
            # Load pakaian
            clothing_data = json.loads(row[5])
            brain.clothing = Clothing(**clothing_data)
            
            brain.mood_nova = Mood(row[7])
            brain.mood_mas = Mood(row[8]) if row[8] else Mood.NETRAL
            
            feelings_data = json.loads(row[9])
            brain.feelings = Feelings(**feelings_data)
            
            relationship_data = json.loads(row[10])
            brain.relationship = Relationship(**relationship_data)
            
            logger.info("📀 State loaded from database")
        
        # Load long-term memory
        cursor = await self._conn.execute(
            "SELECT * FROM long_term_memory ORDER BY timestamp DESC"
        )
        rows = await cursor.fetchall()
        for row in rows:
            tipe = row[1]
            judul = row[2]
            konten = row[3]
            perasaan = row[4]
            if tipe == 'kebiasaan':
                brain.long_term.tambah_kebiasaan(judul)
            elif tipe == 'momen':
                brain.long_term.tambah_momen(judul, perasaan)
            elif tipe == 'janji':
                brain.long_term.tambah_janji(judul)
        
        logger.info(f"📚 Loaded {len(rows)} long-term memories")
    
    # ========== SAVE FUNCTIONS ==========
    
    async def save_timeline_event(self, event: TimelineEvent):
        """Simpan kejadian ke timeline"""
        await self._conn.execute('''
            INSERT INTO timeline (timestamp, kejadian, lokasi_nova, lokasi_mas, 
                                 aktivitas_nova, aktivitas_mas, perasaan_nova,
                                 pakaian_nova, pakaian_mas, pesan_mas, pesan_nova)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp,
            event.kejadian,
            event.lokasi_nova.value if hasattr(event.lokasi_nova, 'value') else event.lokasi_nova,
            event.lokasi_mas.value if hasattr(event.lokasi_mas, 'value') else event.lokasi_mas,
            event.aktivitas_nova,
            event.aktivitas_mas,
            event.perasaan_nova,
            json.dumps(event.pakaian_nova.to_dict()),
            json.dumps(event.pakaian_mas.to_dict()),
            event.pesan_mas[:500] if event.pesan_mas else "",
            event.pesan_nova[:500] if event.pesan_nova else ""
        ))
        await self._conn.commit()
    
    async def save_short_term(self, event: TimelineEvent):
        """Simpan ke short-term memory (sliding window di database juga)"""
        # Hapus yang lama kalo udah lebih dari 50
        cursor = await self._conn.execute(
            "SELECT COUNT(*) FROM short_term_memory"
        )
        count = (await cursor.fetchone())[0]
        
        if count >= 50:
            await self._conn.execute(
                "DELETE FROM short_term_memory WHERE id IN (SELECT id FROM short_term_memory ORDER BY timestamp ASC LIMIT 1)"
            )
        
        await self._conn.execute('''
            INSERT INTO short_term_memory (timestamp, kejadian, lokasi_nova, lokasi_mas,
                                          aktivitas_nova, aktivitas_mas, perasaan_nova,
                                          pakaian_nova, pakaian_mas, pesan_mas, pesan_nova)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp,
            event.kejadian,
            event.lokasi_nova.value if hasattr(event.lokasi_nova, 'value') else event.lokasi_nova,
            event.lokasi_mas.value if hasattr(event.lokasi_mas, 'value') else event.lokasi_mas,
            event.aktivitas_nova,
            event.aktivitas_mas,
            event.perasaan_nova,
            json.dumps(event.pakaian_nova.to_dict()),
            json.dumps(event.pakaian_mas.to_dict()),
            event.pesan_mas[:500] if event.pesan_mas else "",
            event.pesan_nova[:500] if event.pesan_nova else ""
        ))
        await self._conn.commit()
    
    async def save_long_term_memory(self, tipe: str, judul: str, konten: str = "", perasaan: str = ""):
        """Simpan long-term memory"""
        await self._conn.execute('''
            INSERT INTO long_term_memory (tipe, judul, konten, perasaan, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (tipe, judul, konten[:500], perasaan, time.time()))
        await self._conn.commit()
        logger.info(f"📝 Long-term memory saved: {tipe} - {judul}")
    
    async def save_current_state(self, brain):
        """Simpan state saat ini"""
        await self._conn.execute('''
            INSERT OR REPLACE INTO current_state 
            (id, lokasi_nova, lokasi_mas, aktivitas_nova, aktivitas_mas,
             pakaian_nova, pakaian_mas, mood_nova, mood_mas, feelings, relationship, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            brain.location_nova.value if hasattr(brain.location_nova, 'value') else brain.location_nova,
            brain.location_mas.value if hasattr(brain.location_mas, 'value') else brain.location_mas,
            brain.activity_nova.value if hasattr(brain.activity_nova, 'value') else brain.activity_nova,
            brain.activity_mas,
            json.dumps(brain.clothing.to_dict()),
            json.dumps(brain.clothing.to_dict()),  # pakaian mas juga dari clothing
            brain.mood_nova.value if hasattr(brain.mood_nova, 'value') else brain.mood_nova,
            brain.mood_mas.value if hasattr(brain.mood_mas, 'value') else brain.mood_mas,
            json.dumps(brain.feelings.to_dict()),
            json.dumps(brain.relationship.to_dict()),
            time.time()
        ))
        await self._conn.commit()
    
    async def save_conversation(self, role: str, message: str, state_snapshot: Dict = None):
        """Simpan percakapan"""
        await self._conn.execute('''
            INSERT INTO conversation (timestamp, role, message, state_snapshot)
            VALUES (?, ?, ?, ?)
        ''', (
            time.time(),
            role,
            message[:1000],
            json.dumps(state_snapshot) if state_snapshot else None
        ))
        await self._conn.commit()
    
    # ========== GET FUNCTIONS ==========
    
    async def get_recent_conversations(self, limit: int = 20) -> List[Dict]:
        """Dapatkan percakapan terakhir"""
        cursor = await self._conn.execute(
            "SELECT * FROM conversation ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows][::-1]
    
    async def get_timeline(self, limit: int = 100) -> List[Dict]:
        """Dapatkan timeline"""
        cursor = await self._conn.execute(
            "SELECT * FROM timeline ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows][::-1]
    
    async def get_long_term_memories(self, tipe: str = None) -> List[Dict]:
        """Dapatkan long-term memory"""
        if tipe:
            cursor = await self._conn.execute(
                "SELECT * FROM long_term_memory WHERE tipe = ? ORDER BY timestamp DESC",
                (tipe,)
            )
        else:
            cursor = await self._conn.execute(
                "SELECT * FROM long_term_memory ORDER BY timestamp DESC"
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def close(self):
        if self._conn:
            await self._conn.close()


_anora_persistent: Optional[PersistentMemory] = None


async def get_anora_persistent() -> PersistentMemory:
    global _anora_persistent
    if _anora_persistent is None:
        _anora_persistent = PersistentMemory()
        await _anora_persistent.init()
    return _anora_persistent


anora_persistent = get_anora_persistent()
