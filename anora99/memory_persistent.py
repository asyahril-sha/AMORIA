# anora/memory_persistent.py
"""
ANORA Persistent Memory - Simpan semua ingatan Nova ke database
Gak ilang kalo restart. Short-term memory sliding window.
Long-term memory permanen.
DENGAN COMPLETE STATE - Semua aspek disimpan ke database.
DENGAN ROLE TABLES - Semua role (IPAR, Teman Kantor, Pelakor, Istri Orang) juga disimpan.
"""

import time
import json
import aiosqlite
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .brain import (
    get_anora_brain, TimelineEvent, LocationType, LocationDetail,
    Activity, Mood, Clothing, Feelings, Relationship
)

logger = logging.getLogger(__name__)


class PersistentMemory:
    """
    Memory permanen Nova. Disimpan ke database.
    - Timeline: semua kejadian
    - Short-term memory: sliding window 50 kejadian (otomatis di-brain)
    - Long-term memory: kebiasaan, momen, janji
    - State: lokasi, pakaian, perasaan terakhir
    - Conversation: semua percakapan
    - COMPLETE STATE: semua aspek Mas, Nova, dan bersama
    - ROLE TABLES: semua state dan memory untuk role (IPAR, Teman Kantor, dll)
    """
    
    def __init__(self, db_path: Path = Path("data/anora_memory.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = None
    
    async def init(self):
        """Buat semua tabel memory"""
        self._conn = await aiosqlite.connect(str(self.db_path))
        
        # ========== TABEL STATE (UTAMA) ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS anora_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL COMPLETE STATE (BARU!) ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS complete_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                mas_state TEXT NOT NULL,
                nova_state TEXT NOT NULL,
                together_state TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL TIMELINE (SEMUA KEJADIAN) ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS timeline (
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
        
        # ========== TABEL SHORT-TERM MEMORY (SLIDING WINDOW) ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS short_term_memory (
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
        
        # ========== TABEL LONG-TERM MEMORY (PERMANEN) ==========
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
        
        # ========== TABEL STATE SAAT INI ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS current_state (
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
        
        # ========== TABEL PERCAKAPAN ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                state_snapshot TEXT
            )
        ''')
        
        # ========== TABEL KUNJUNGAN LOKASI ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS location_visits (
                id TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                visit_count INTEGER DEFAULT 1,
                last_visit REAL NOT NULL
            )
        ''')
        
        # ========== TABEL ROLE (BARU!) ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS role_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_type TEXT NOT NULL,
                name TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                phase TEXT DEFAULT 'acquaintance',
                clothing TEXT,
                position TEXT,
                location TEXT,
                activity TEXT,
                arousal REAL DEFAULT 0,
                desire REAL DEFAULT 0,
                tension REAL DEFAULT 0,
                stamina_current REAL DEFAULT 100,
                stamina_climax_today INTEGER DEFAULT 0,
                intimacy_active INTEGER DEFAULT 0,
                intimacy_climax_count INTEGER DEFAULT 0,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL ROLE MEMORY (BARU!) ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS role_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                role_msg TEXT,
                mas_msg TEXT
            )
        ''')
        
        # ========== INDEXES ==========
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_timeline_time ON timeline(timestamp)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_short_term_time ON short_term_memory(timestamp)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_long_term_tipe ON long_term_memory(tipe)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_conversation_time ON conversation(timestamp)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_role_states_type ON role_states(role_type)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_role_memory_type ON role_memory(role_type)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_role_memory_time ON role_memory(timestamp)')
        
        await self._conn.commit()
        
        # Inisialisasi state awal jika belum ada
        await self._init_state()
        
        logger.info(f"💾 ANORA Persistent Memory initialized at {self.db_path}")
        
        # Load data ke brain
        await self._load_to_brain()
    
    async def _init_state(self):
        """Inisialisasi state awal"""
        # Cek apakah tabel complete_state sudah ada isinya
        cursor = await self._conn.execute("SELECT COUNT(*) FROM complete_state")
        count = await cursor.fetchone()
        
        if count[0] == 0:
            # Inisialisasi complete_state default
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
            
            await self._conn.execute(
                "INSERT INTO complete_state (id, mas_state, nova_state, together_state, updated_at) VALUES (1, ?, ?, ?, ?)",
                (json.dumps(default_complete['mas']), json.dumps(default_complete['nova']), 
                 json.dumps(default_complete['together']), time.time())
            )
            await self._conn.commit()
            logger.info("📀 Complete state initialized")
        
        # State default untuk anora_state
        defaults = {
            'sayang': '50',
            'rindu': '0',
            'desire': '0',
            'arousal': '0',
            'tension': '0',
            'level': '1',
            'energi': '100',
            'stamina_nova': '100',
            'stamina_mas': '100'
        }
        for key, val in defaults.items():
            await self._conn.execute(
                "INSERT OR IGNORE INTO anora_state (key, value, updated_at) VALUES (?, ?, ?)",
                (key, val, time.time())
            )
        await self._conn.commit()
    
    # =========================================================================
    # COMPLETE STATE METHODS
    # =========================================================================
    
    async def save_complete_state(self, brain):
        """Simpan complete_state ke database"""
        try:
            complete = brain.complete_state
            
            await self._conn.execute(
                """INSERT OR REPLACE INTO complete_state 
                   (id, mas_state, nova_state, together_state, updated_at) 
                   VALUES (1, ?, ?, ?, ?)""",
                (json.dumps(complete['mas']), json.dumps(complete['nova']), 
                 json.dumps(complete['together']), time.time())
            )
            await self._conn.commit()
            logger.debug("💾 Complete state saved to database")
        except Exception as e:
            logger.error(f"Error saving complete state: {e}")
    
    async def load_complete_state(self, brain) -> bool:
        """Load complete_state dari database ke brain"""
        try:
            cursor = await self._conn.execute(
                "SELECT mas_state, nova_state, together_state FROM complete_state WHERE id = 1"
            )
            row = await cursor.fetchone()
            
            if row:
                brain.complete_state['mas'] = json.loads(row[0])
                brain.complete_state['nova'] = json.loads(row[1])
                brain.complete_state['together'] = json.loads(row[2])
                logger.info("📀 Complete state loaded from database")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading complete state: {e}")
            return False
    
    # =========================================================================
    # STATE METHODS
    # =========================================================================
    
    async def get_state(self, key: str) -> Optional[str]:
        """Dapatkan state berdasarkan key"""
        cursor = await self._conn.execute("SELECT value FROM anora_state WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else None
    
    async def set_state(self, key: str, value: str):
        """Simpan state ke database"""
        await self._conn.execute(
            "INSERT OR REPLACE INTO anora_state (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, time.time())
        )
        await self._conn.commit()
        logger.debug(f"💾 State saved: {key}")
    
    async def get_all_states(self) -> Dict[str, str]:
        """Dapatkan semua state dari database"""
        cursor = await self._conn.execute("SELECT key, value FROM anora_state")
        rows = await cursor.fetchall()
        return {row[0]: row[1] for row in rows}
    
    # =========================================================================
    # ROLE STATE METHODS (BARU!)
    # =========================================================================
    
    async def init_role_tables(self) -> bool:
        """Inisialisasi tabel untuk role (dipanggil dari roles.py)"""
        try:
            # Tabel role_states sudah dibuat di init(), tapi pastikan ada
            await self._conn.execute('''
                CREATE TABLE IF NOT EXISTS role_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    phase TEXT DEFAULT 'acquaintance',
                    clothing TEXT,
                    position TEXT,
                    location TEXT,
                    activity TEXT,
                    arousal REAL DEFAULT 0,
                    desire REAL DEFAULT 0,
                    tension REAL DEFAULT 0,
                    stamina_current REAL DEFAULT 100,
                    stamina_climax_today INTEGER DEFAULT 0,
                    intimacy_active INTEGER DEFAULT 0,
                    intimacy_climax_count INTEGER DEFAULT 0,
                    updated_at REAL NOT NULL
                )
            ''')
            
            # Tabel role_memory
            await self._conn.execute('''
                CREATE TABLE IF NOT EXISTS role_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_type TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    role_msg TEXT,
                    mas_msg TEXT
                )
            ''')
            
            # Index untuk performa
            await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_role_states_type ON role_states(role_type)')
            await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_role_memory_type ON role_memory(role_type)')
            await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_role_memory_time ON role_memory(timestamp)')
            
            await self._conn.commit()
            logger.info("📀 Role tables initialized")
            return True
        except Exception as e:
            logger.error(f"Error creating role tables: {e}")
            return False
    
    async def save_role_state(self, role_type: str, role_instance) -> bool:
        """Simpan state role ke database"""
        try:
            # Konversi state ke JSON
            clothing_data = {
                'hijab': role_instance.clothing.hijab,
                'hijab_warna': role_instance.clothing.hijab_warna,
                'top': role_instance.clothing.top,
                'bra': role_instance.clothing.bra,
                'cd': role_instance.clothing.cd
            }
            
            position_data = {
                'state': role_instance.position.state,
                'detail': role_instance.position.detail
            }
            
            location_data = {
                'room': role_instance.location.room,
                'detail': role_instance.location.detail
            }
            
            activity_data = {
                'main': role_instance.activity.main,
                'detail': role_instance.activity.detail
            }
            
            await self._conn.execute('''
                INSERT OR REPLACE INTO role_states (
                    role_type, name, level, phase,
                    clothing, position, location, activity,
                    arousal, desire, tension,
                    stamina_current, stamina_climax_today,
                    intimacy_active, intimacy_climax_count,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                role_type,
                role_instance.name,
                role_instance.level,
                role_instance.phase.value,
                json.dumps(clothing_data),
                json.dumps(position_data),
                json.dumps(location_data),
                json.dumps(activity_data),
                role_instance.arousal.arousal,
                role_instance.arousal.desire,
                role_instance.arousal.tension,
                role_instance.stamina.current,
                role_instance.stamina.climax_today,
                1 if role_instance.intimacy.is_active else 0,
                role_instance.intimacy.climax_count,
                time.time()
            ))
            await self._conn.commit()
            logger.debug(f"💾 Role state saved: {role_type}")
            return True
        except Exception as e:
            logger.error(f"Error saving role state: {e}")
            return False
    
    async def load_role_state(self, role_type: str, role_instance) -> bool:
        """Load state role dari database"""
        try:
            cursor = await self._conn.execute(
                "SELECT * FROM role_states WHERE role_type = ? ORDER BY updated_at DESC LIMIT 1",
                (role_type,)
            )
            row = await cursor.fetchone()
            
            if row:
                # Load level
                role_instance.level = row[3] if len(row) > 3 else 1
                
                # Load phase
                from .role_base import RolePhase
                try:
                    if len(row) > 4 and row[4]:
                        role_instance.phase = RolePhase(row[4])
                except:
                    pass
                
                # Load clothing
                if len(row) > 5 and row[5]:
                    clothing_data = json.loads(row[5])
                    role_instance.clothing.hijab = clothing_data.get('hijab', True)
                    role_instance.clothing.hijab_warna = clothing_data.get('hijab_warna', 'pink muda')
                    role_instance.clothing.top = clothing_data.get('top', 'daster rumah motif bunga')
                    role_instance.clothing.bra = clothing_data.get('bra', True)
                    role_instance.clothing.cd = clothing_data.get('cd', True)
                
                # Load position
                if len(row) > 6 and row[6]:
                    position_data = json.loads(row[6])
                    role_instance.position.state = position_data.get('state')
                    role_instance.position.detail = position_data.get('detail')
                
                # Load location
                if len(row) > 7 and row[7]:
                    location_data = json.loads(row[7])
                    role_instance.location.room = location_data.get('room', 'kamar')
                    role_instance.location.detail = location_data.get('detail')
                
                # Load activity
                if len(row) > 8 and row[8]:
                    activity_data = json.loads(row[8])
                    role_instance.activity.main = activity_data.get('main', 'santai')
                    role_instance.activity.detail = activity_data.get('detail')
                
                # Load arousal
                role_instance.arousal.arousal = row[9] if len(row) > 9 else 0
                role_instance.arousal.desire = row[10] if len(row) > 10 else 0
                role_instance.arousal.tension = row[11] if len(row) > 11 else 0
                
                # Load stamina
                role_instance.stamina.current = row[12] if len(row) > 12 else 100
                role_instance.stamina.climax_today = row[13] if len(row) > 13 else 0
                
                # Load intimacy
                role_instance.intimacy.is_active = bool(row[14]) if len(row) > 14 else False
                role_instance.intimacy.climax_count = row[15] if len(row) > 15 else 0
                
                logger.info(f"📀 Role state loaded: {role_type} (Level {role_instance.level})")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading role state: {e}")
            return False
    
    async def save_role_memory(self, role_type: str, role_instance) -> bool:
        """Simpan memory percakapan role"""
        try:
            # Hapus memory lama untuk role ini
            await self._conn.execute(
                "DELETE FROM role_memory WHERE role_type = ?",
                (role_type,)
            )
            
            # Simpan memory baru (last 30)
            for conv in role_instance.conversations[-30:]:
                await self._conn.execute('''
                    INSERT INTO role_memory (role_type, timestamp, role_msg, mas_msg)
                    VALUES (?, ?, ?, ?)
                ''', (
                    role_type,
                    conv['timestamp'],
                    conv['role'][:1000] if conv['role'] else "",
                    conv['mas'][:1000] if conv['mas'] else ""
                ))
            
            await self._conn.commit()
            logger.debug(f"💾 Role memory saved: {role_type}")
            return True
        except Exception as e:
            logger.error(f"Error saving role memory: {e}")
            return False
    
    async def load_role_memory(self, role_type: str, role_instance) -> bool:
        """Load memory percakapan role"""
        try:
            cursor = await self._conn.execute(
                "SELECT * FROM role_memory WHERE role_type = ? ORDER BY timestamp ASC",
                (role_type,)
            )
            rows = await cursor.fetchall()
            
            role_instance.conversations = []
            for row in rows:
                if len(row) >= 5:
                    role_instance.conversations.append({
                        'timestamp': row[2],
                        'role': row[3] or "",
                        'mas': row[4] or ""
                    })
            
            logger.info(f"📀 Role memory loaded: {role_type} ({len(role_instance.conversations)} conversations)")
            return True
        except Exception as e:
            logger.error(f"Error loading role memory: {e}")
            return False
    
    # =========================================================================
    # LOAD KE BRAIN
    # =========================================================================
    
    async def _load_to_brain(self):
        """Load semua memory ke brain"""
        brain = get_anora_brain()
        
        # Load complete state
        await self.load_complete_state(brain)
        
        # Load state dari anora_state
        states = await self.get_all_states()
        if 'sayang' in states:
            brain.feelings.sayang = float(states['sayang'])
        if 'rindu' in states:
            brain.feelings.rindu = float(states['rindu'])
        if 'desire' in states:
            brain.feelings.desire = float(states['desire'])
        if 'arousal' in states:
            brain.feelings.arousal = float(states['arousal'])
        if 'tension' in states:
            brain.feelings.tension = float(states['tension'])
        if 'level' in states:
            brain.relationship.level = int(states['level'])
        
        # Load timeline (terakhir 100)
        cursor = await self._conn.execute(
            "SELECT * FROM timeline ORDER BY timestamp ASC LIMIT 100"
        )
        rows = await cursor.fetchall()
        for row in rows:
            pakaian_nova = Clothing()
            pakaian_mas = Clothing()
            try:
                pakaian_nova_dict = json.loads(row[8])
                pakaian_mas_dict = json.loads(row[9])
                for key, val in pakaian_nova_dict.items():
                    if hasattr(pakaian_nova, key):
                        setattr(pakaian_nova, key, val)
                for key, val in pakaian_mas_dict.items():
                    if hasattr(pakaian_mas, key):
                        setattr(pakaian_mas, key, val)
            except:
                pass
            
            event = TimelineEvent(
                kejadian=row[2],
                lokasi_type=row[3],
                lokasi_detail=row[4],
                aktivitas_nova=row[5],
                aktivitas_mas=row[6],
                perasaan=row[7],
                pakaian_nova=pakaian_nova,
                pakaian_mas=pakaian_mas,
                pesan_mas=row[10] or "",
                pesan_nova=row[11] or ""
            )
            event.timestamp = row[1]
            brain.timeline.append(event)
        
        # Load short-term memory
        cursor = await self._conn.execute(
            "SELECT * FROM short_term_memory ORDER BY timestamp ASC LIMIT 50"
        )
        rows = await cursor.fetchall()
        for row in rows:
            pakaian_nova = Clothing()
            pakaian_mas = Clothing()
            try:
                pakaian_nova_dict = json.loads(row[8])
                pakaian_mas_dict = json.loads(row[9])
                for key, val in pakaian_nova_dict.items():
                    if hasattr(pakaian_nova, key):
                        setattr(pakaian_nova, key, val)
                for key, val in pakaian_mas_dict.items():
                    if hasattr(pakaian_mas, key):
                        setattr(pakaian_mas, key, val)
            except:
                pass
            
            event = TimelineEvent(
                kejadian=row[2],
                lokasi_type=row[3],
                lokasi_detail=row[4],
                aktivitas_nova=row[5],
                aktivitas_mas=row[6],
                perasaan=row[7],
                pakaian_nova=pakaian_nova,
                pakaian_mas=pakaian_mas,
                pesan_mas=row[10] or "",
                pesan_nova=row[11] or ""
            )
            event.timestamp = row[1]
            brain.short_term.append(event)
        
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
        
        # Load current state
        cursor = await self._conn.execute(
            "SELECT * FROM current_state ORDER BY updated_at DESC LIMIT 1"
        )
        row = await cursor.fetchone()
        if row:
            brain.location_type = LocationType(row[1])
            brain.location_detail = LocationDetail(row[2])
            brain.activity_nova = Activity(row[3]) if row[3] else Activity.SANTAl
            brain.activity_mas = row[4]
            
            try:
                pakaian_dict = json.loads(row[5])
                for key, val in pakaian_dict.items():
                    if hasattr(brain.clothing, key):
                        setattr(brain.clothing, key, val)
            except:
                pass
            
            brain.mood_nova = Mood(row[7]) if row[7] else Mood.NETRAL
            
            # Load feelings
            try:
                feelings_dict = json.loads(row[9])
                brain.feelings.sayang = feelings_dict.get('sayang', 50)
                brain.feelings.rindu = feelings_dict.get('rindu', 0)
                brain.feelings.desire = feelings_dict.get('desire', 0)
                brain.feelings.arousal = feelings_dict.get('arousal', 0)
                brain.feelings.tension = feelings_dict.get('tension', 0)
            except:
                pass
            
            # Load relationship
            try:
                rel_dict = json.loads(row[10])
                brain.relationship.level = rel_dict.get('level', 1)
                brain.relationship.first_kiss = rel_dict.get('first_kiss', False)
                brain.relationship.first_touch = rel_dict.get('first_touch', False)
                brain.relationship.first_hug = rel_dict.get('first_hug', False)
                brain.relationship.first_intim = rel_dict.get('first_intim', False)
            except:
                pass
            
            # Load complete state dari row (jika ada)
            if len(row) > 12 and row[12]:
                try:
                    complete_dict = json.loads(row[12])
                    if complete_dict:
                        brain.complete_state = complete_dict
                        logger.info("📀 Complete state loaded from current_state")
                except:
                    pass
        
        logger.info(f"📀 Loaded to brain: {len(brain.timeline)} timeline, {len(brain.short_term)} short-term")
    
    # =========================================================================
    # SAVE FUNCTIONS
    # =========================================================================
    
    async def save_timeline_event(self, event: TimelineEvent):
        """Simpan kejadian ke timeline"""
        await self._conn.execute('''
            INSERT INTO timeline (
                timestamp, kejadian, lokasi_type, lokasi_detail,
                aktivitas_nova, aktivitas_mas, perasaan,
                pakaian_nova, pakaian_mas, pesan_mas, pesan_nova
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp,
            event.kejadian,
            event.lokasi_type,
            event.lokasi_detail,
            event.aktivitas_nova,
            event.aktivitas_mas,
            event.perasaan,
            json.dumps(event.pakaian_nova.to_dict()),
            json.dumps(event.pakaian_mas.to_dict()),
            event.pesan_mas[:1000] if event.pesan_mas else "",
            event.pesan_nova[:1000] if event.pesan_nova else ""
        ))
        await self._conn.commit()
    
    async def save_short_term(self, event: TimelineEvent):
        """Simpan ke short-term memory (sliding window)"""
        cursor = await self._conn.execute("SELECT COUNT(*) FROM short_term_memory")
        count = (await cursor.fetchone())[0]
        
        if count >= 50:
            await self._conn.execute(
                "DELETE FROM short_term_memory WHERE id IN (SELECT id FROM short_term_memory ORDER BY timestamp ASC LIMIT 1)"
            )
        
        await self._conn.execute('''
            INSERT INTO short_term_memory (
                timestamp, kejadian, lokasi_type, lokasi_detail,
                aktivitas_nova, aktivitas_mas, perasaan,
                pakaian_nova, pakaian_mas, pesan_mas, pesan_nova
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp,
            event.kejadian,
            event.lokasi_type,
            event.lokasi_detail,
            event.aktivitas_nova,
            event.aktivitas_mas,
            event.perasaan,
            json.dumps(event.pakaian_nova.to_dict()),
            json.dumps(event.pakaian_mas.to_dict()),
            event.pesan_mas[:1000] if event.pesan_mas else "",
            event.pesan_nova[:1000] if event.pesan_nova else ""
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
        """Simpan state saat ini (termasuk complete state)"""
        # Simpan complete state terlebih dahulu
        await self.save_complete_state(brain)
        
        await self._conn.execute('''
            INSERT OR REPLACE INTO current_state (
                id, lokasi_type, lokasi_detail, aktivitas_nova, aktivitas_mas,
                pakaian_nova, pakaian_mas, mood_nova, mood_mas,
                feelings, relationship, complete_state, updated_at
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            brain.location_type.value,
            brain.location_detail.value,
            brain.activity_nova.value if hasattr(brain.activity_nova, 'value') else str(brain.activity_nova),
            brain.activity_mas,
            json.dumps(brain.clothing.to_dict()),
            json.dumps(brain.clothing.to_dict()),
            brain.mood_nova.value if hasattr(brain.mood_nova, 'value') else str(brain.mood_nova),
            brain.mood_mas.value if hasattr(brain.mood_mas, 'value') else str(brain.mood_mas),
            json.dumps(brain.feelings.to_dict()),
            json.dumps(brain.relationship.to_dict()),
            json.dumps(brain.complete_state),
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
            message[:2000],
            json.dumps(state_snapshot) if state_snapshot else None
        ))
        await self._conn.commit()
    
    async def save_location_visit(self, location_id: str, nama: str):
        """Simpan kunjungan lokasi"""
        now = time.time()
        await self._conn.execute('''
            INSERT INTO location_visits (id, nama, visit_count, last_visit)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(id) DO UPDATE SET
                visit_count = visit_count + 1,
                last_visit = ?
        ''', (location_id, nama, now, now))
        await self._conn.commit()
    
    # =========================================================================
    # GET FUNCTIONS
    # =========================================================================
    
    async def get_recent_conversations(self, limit: int = 20) -> List[Dict]:
        cursor = await self._conn.execute(
            "SELECT * FROM conversation ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows][::-1]
    
    async def get_timeline(self, limit: int = 100) -> List[Dict]:
        cursor = await self._conn.execute(
            "SELECT * FROM timeline ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows][::-1]
    
    async def get_short_term(self) -> List[Dict]:
        cursor = await self._conn.execute(
            "SELECT * FROM short_term_memory ORDER BY timestamp ASC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_long_term_memories(self, tipe: str = None) -> List[Dict]:
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
    
    async def get_stats(self) -> Dict:
        stats = {}
        tables = ['timeline', 'short_term_memory', 'long_term_memory', 'conversation', 'location_visits', 'complete_state', 'role_states', 'role_memory']
        for table in tables:
            cursor = await self._conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = (await cursor.fetchone())[0]
            stats[f"{table}_count"] = count
        if self.db_path.exists():
            stats['db_size_mb'] = round(self.db_path.stat().st_size / (1024 * 1024), 2)
        return stats
    
    # =========================================================================
    # CLEANUP & UTILITY
    # =========================================================================
    
    async def cleanup_old_short_term(self, keep: int = 50):
        cursor = await self._conn.execute("SELECT COUNT(*) FROM short_term_memory")
        count = (await cursor.fetchone())[0]
        if count > keep:
            to_delete = count - keep
            await self._conn.execute(
                "DELETE FROM short_term_memory WHERE id IN (SELECT id FROM short_term_memory ORDER BY timestamp ASC LIMIT ?)",
                (to_delete,)
            )
            await self._conn.commit()
    
    async def vacuum(self):
        await self._conn.execute("VACUUM")
    
    async def close(self):
        if self._conn:
            await self._conn.close()


# =============================================================================
# SINGLETON
# =============================================================================

_anora_persistent: Optional[PersistentMemory] = None


async def get_anora_persistent() -> PersistentMemory:
    global _anora_persistent
    if _anora_persistent is None:
        _anora_persistent = PersistentMemory()
        await _anora_persistent.init()
    return _anora_persistent


anora_persistent = get_anora_persistent()
