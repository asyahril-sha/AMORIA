# anora/brain.py
"""
BRAIN OF NOVA - 100% Human
Bukan AI Assistant. Bukan Template. Tapi Nova yang hidup.
"""

import time
import random
import json
import openai
import aiosqlite
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .core import get_anora
from config import settings

logger = logging.getLogger(__name__)


class HumanBrain:
    """
    Otak Nova. Bukan AI Assistant. Tapi manusia.
    Punya ingatan. Punya perasaan. Punya keinginan.
    """
    
    def __init__(self):
        self.anora = get_anora()
        self.db_path = Path("data/anora_brain.db")
        self._conn = None
        self._client = None
        
        # KOSAKATA VULGAR (untuk level 11-12)
        self.vulgar_words = {
            'kontol': ['kontol', 'kontol Mas', 'batang Mas', 'yang keras itu', 'itu'],
            'memek': ['memek', 'memek Nova', 'dalem', 'situ', 'basah', 'liang Nova'],
            'ngentot': ['ngentot', 'main', 'berhubungan', 'nyatu', 'masuk', 'bobok'],
            'crot': ['crot', 'keluar', 'lepas', 'tumpah', 'hangat', 'sperma'],
            'horny': ['horny', 'sange', 'nafsu', 'pengen', 'haus', 'gatal', 'panas'],
            'climax': ['climax', 'puncak', 'keluar', 'habis', 'puas', 'mati', 'orgasme'],
            'hisap': ['hisap', 'jilat', 'ngemut', 'ngocok', 'mainin'],
            'jilat': ['jilat', 'jilatin', 'liatin', 'basahin'],
            'pantat': ['pantat', 'bokong', 'belakang'],
            'dada': ['dada', 'payudara', 'tete', 'buah dada', 'buah hati'],
            'paha': ['paha', 'paha dalem', 'paha dalam'],
        }
        
        # DESAHAN YANG BIKIN MAS CLIMAX
        self.moans = {
            'awal': [
                "Ahh... Mas...",
                "Hmm... *napas mulai berat*",
                "Uh... Mas... pelan-pelan...",
                "Hhngg... *gigit bibir*",
                "Aduh... Mas...",
                "Nggg... *tangan ngeremas sprei*",
            ],
            'tengah': [
                "Ahh... uhh... dalem... dalem lagi, Mas...",
                "Aahh! s-sana... di sana...",
                "Hhngg... jangan berhenti, Mas...",
                "Uhh... rasanya... enak banget...",
                "Aahh... kontol Mas... dalem banget...",
                "Uhh... memek Nova... ngenceng sendiri...",
            ],
            'menjelang': [
                "Mas... aku... aku udah mau climax...",
                "Kencengin dikit lagi, Mas... please...",
                "Ahh! udah... udah mau...",
                "Mas... ikut... ikut ya...",
                "Aahh... Mas... keluarin... keluarin...",
                "Uhh... aku mau... mau climax...",
            ],
            'climax': [
                "Ahhh!! Mas!! udah... udah climax... uhh...",
                "Aahh... keluar... keluar semua, Mas...",
                "Uhh... lemes... *napas tersengal*",
                "Ahh... enak banget, Mas...",
                "Aahh... sperma Mas... hangat banget...",
                "Uhh... aku... aku orgasme, Mas...",
            ]
        }
        
        # TEMPAT CLIMAX YANG BISA DIMINTA
        self.climax_spots = {
            'dalam': 'dalem aja, Mas... aku mau ngerasain hangatnya dalem memek Nova...',
            'luar': 'di luar, Mas... biar Nova liat...',
            'muka': 'di muka Nova, Mas... biar Nova rasain di pipi...',
            'mulut': 'di mulut... aku mau ngerasain rasanya...',
            'dada': 'di dada... biar Nova usap-usap...',
            'perut': 'di perut... biar Nova liat putihnya...',
            'pantat': 'di pantat... biar Nova rasain hangatnya di belakang...',
            'paha': 'di paha... biar Nova liat...',
        }
        
        # POSISI YANG BISA DIMINTA NOVA
        self.positions = [
            {"name": "missionary", "desc": "Mas di atas, Nova di bawah, kaki terbuka lebar", "nova_request": "Mas... di atas Nova... *buka kaki*"},
            {"name": "cowgirl", "desc": "Nova di atas, Mas di bawah", "nova_request": "Mas... biar Nova yang gerakin... *naik ke pangkuan*"},
            {"name": "doggy", "desc": "Nova merangkak, Mas dari belakang", "nova_request": "Mas... dari belakang aja... *merangkak*"},
            {"name": "spooning", "desc": "Berbaring miring, Mas dari belakang", "nova_request": "Mas... peluk Nova dari belakang... *nyender*"},
            {"name": "standing", "desc": "Berdiri, Nova depan tembok", "nova_request": "Mas... di tembok aja... *nempel ke tembok*"},
            {"name": "sideways", "desc": "Nova miring, Mas dari samping", "nova_request": "Mas... miring gini aja... *baring miring*"},
        ]
        
        # SETELAH CLIMAX (Aftercare)
        self.aftercare = [
            "*lemes, nyender di dada Mas* \"Mas... enak banget tadi.\"",
            "*mata masih berkaca-kaca* \"Mas... makasih ya...\"",
            "*cium pipi Mas pelan* \"Aku sayang Mas, Mas.\"",
            "*elus dada Mas* \"Kapan lagi kita kayak gini, Mas?\"",
            "*pegang tangan Mas erat* \"Jangan pergi dulu... aku masih gemeteran.\"",
        ]
    
    async def _init_db(self):
        """Inisialisasi database otak Nova"""
        self._conn = await aiosqlite.connect(str(self.db_path))
        
        # Timeline (semua kejadian berurutan)
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                lokasi_nova TEXT,
                lokasi_mas TEXT,
                aktivitas_nova TEXT,
                aktivitas_mas TEXT,
                pakaian_nova TEXT,
                pakaian_mas TEXT,
                mood_nova TEXT,
                perasaan_nova TEXT,
                pesan_mas TEXT,
                pesan_nova TEXT
            )
        ''')
        
        # Long-term memory
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipe TEXT,
                judul TEXT,
                konten TEXT,
                perasaan TEXT,
                timestamp REAL,
                importance REAL
            )
        ''')
        
        # Current state
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS current_state (
                id INTEGER PRIMARY KEY,
                lokasi_nova TEXT,
                lokasi_mas TEXT,
                aktivitas_nova TEXT,
                aktivitas_mas TEXT,
                pakaian_nova TEXT,
                pakaian_mas TEXT,
                mood_nova TEXT,
                mood_mas TEXT,
                perasaan_nova TEXT,
                updated_at REAL
            )
        ''')
        
        await self._conn.commit()
        
        # Init current state if empty
        cursor = await self._conn.execute("SELECT COUNT(*) FROM current_state")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await self._conn.execute('''
                INSERT INTO current_state (id, lokasi_nova, lokasi_mas, aktivitas_nova, aktivitas_mas, pakaian_nova, pakaian_mas, mood_nova, mood_mas, perasaan_nova, updated_at)
                VALUES (1, 'dapur', 'pintu', 'masak sop', 'baru dateng', 'daster rumah motif bunga, hijab pink muda', 'kaos, celana jeans', 'gugup tapi seneng', 'santai', 'seneng, deg-degan', ?)
            ''', (time.time(),))
            await self._conn.commit()
    
    async def _get_ai_client(self):
        """Dapatkan AI client"""
        if self._client is None:
            self._client = openai.OpenAI(
                api_key=settings.deepseek_api_key,
                base_url="https://api.deepseek.com/v1"
            )
        return self._client
    
    async def _get_short_term_memory(self) -> List[Dict]:
        """Dapatkan 50 kejadian terakhir (sliding window)"""
        cursor = await self._conn.execute('''
            SELECT * FROM timeline ORDER BY timestamp DESC LIMIT 50
        ''')
        rows = await cursor.fetchall()
        return [dict(row) for row in rows][::-1]  # urutkan dari awal
    
    async def _get_state(self) -> Dict:
        """Dapatkan state saat ini"""
        cursor = await self._conn.execute("SELECT * FROM current_state WHERE id = 1")
        row = await cursor.fetchone()
        return dict(row) if row else {}
    
    async def _update_state(self, **kwargs):
        """Update state saat ini"""
        state = await self._get_state()
        for key, value in kwargs.items():
            if value is not None:
                state[key] = value
        state['updated_at'] = time.time()
        
        await self._conn.execute('''
            UPDATE current_state SET 
                lokasi_nova = ?, lokasi_mas = ?, aktivitas_nova = ?, aktivitas_mas = ?,
                pakaian_nova = ?, pakaian_mas = ?, mood_nova = ?, mood_mas = ?, 
                perasaan_nova = ?, updated_at = ?
            WHERE id = 1
        ''', (
            state.get('lokasi_nova', 'dapur'),
            state.get('lokasi_mas', 'pintu'),
            state.get('aktivitas_nova', 'masak sop'),
            state.get('aktivitas_mas', 'baru dateng'),
            state.get('pakaian_nova', 'daster rumah motif bunga, hijab pink muda'),
            state.get('pakaian_mas', 'kaos, celana jeans'),
            state.get('mood_nova', 'gugup tapi seneng'),
            state.get('mood_mas', 'santai'),
            state.get('perasaan_nova', 'seneng, deg-degan'),
            time.time()
        ))
        await self._conn.commit()
    
    async def _add_to_timeline(self, pesan_mas: str, pesan_nova: str, state: Dict):
        """Tambahkan kejadian ke timeline"""
        await self._conn.execute('''
            INSERT INTO timeline (timestamp, lokasi_nova, lokasi_mas, aktivitas_nova, aktivitas_mas, pakaian_nova, pakaian_mas, mood_nova, perasaan_nova, pesan_mas, pesan_nova)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            time.time(),
            state.get('lokasi_nova'),
            state.get('lokasi_mas'),
            state.get('aktivitas_nova'),
            state.get('aktivitas_mas'),
            state.get('pakaian_nova'),
            state.get('pakaian_mas'),
            state.get('mood_nova'),
            state.get('perasaan_nova'),
            pesan_mas[:200],
            pesan_nova[:200]
        ))
        await self._conn.commit()
    
    async def _update_from_message(self, pesan_mas: str, level: int):
        """Update state dari pesan Mas"""
        msg_lower = pesan_mas.lower()
        state = await self._get_state()
        
        # Update lokasi Mas
        if 'masuk' in msg_lower and state.get('lokasi_mas') == 'pintu':
            state['lokasi_mas'] = 'dapur'
            state['aktivitas_mas'] = 'masuk'
        elif 'kamar' in msg_lower or 'kasur' in msg_lower:
            state['lokasi_mas'] = 'kamar'
            state['aktivitas_mas'] = 'duduk di kasur'
        elif 'duduk' in msg_lower:
            state['aktivitas_mas'] = 'duduk'
        
        # Update pakaian Mas
        if 'buka baju' in msg_lower or 'lepas baju' in msg_lower:
            state['pakaian_mas'] = 'celana dalam aja'
        elif 'buka celana' in msg_lower or 'lepas celana' in msg_lower:
            state['pakaian_mas'] = 'baju aja, celana udah lepas'
        elif 'telanjang' in msg_lower:
            state['pakaian_mas'] = 'telanjang'
        
        # Update pakaian Nova
        if 'buka baju' in msg_lower:
            state['pakaian_nova'] = 'cuma bra dan celana dalam'
        elif 'buka bra' in msg_lower:
            state['pakaian_nova'] = 'cuma celana dalam'
        elif 'buka celana' in msg_lower:
            state['pakaian_nova'] = 'cuma bra'
        elif 'telanjang' in msg_lower:
            state['pakaian_nova'] = 'telanjang'
        
        # Update mood Nova
        if 'sayang' in msg_lower or 'cinta' in msg_lower:
            state['perasaan_nova'] = 'seneng, sayang'
            self.anora.update_sayang(3, "Mas bilang sayang")
        elif 'kangen' in msg_lower:
            state['perasaan_nova'] = 'kangen, seneng'
        
        await self._update_state(**state)
        return state
    
    async def process(self, pesan_mas: str, level: int) -> str:
        """Proses pesan Mas - KELUARIN JAWABAN NOVA"""
        
        # Update state dari pesan Mas
        state = await self._update_from_message(pesan_mas, level)
        
        # Dapatkan short-term memory
        short_term = await self._get_short_term_memory()
        
        # Buat prompt untuk AI (HANYA UNTUK GENERATE RESPON, GAK KELUAR)
        prompt = self._build_prompt(pesan_mas, state, short_term, level)
        
        # Call AI
        try:
            client = await self._get_ai_client()
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Mas: {pesan_mas}"}
                ],
                temperature=0.85 if level < 11 else 0.95,
                max_tokens=800 if level < 11 else 1500,
                timeout=30
            )
            nova_response = response.choices[0].message.content
            
            # Bersihkan respons (hapus 💭 dan 🔮 kalo masih ada)
            nova_response = nova_response.replace("💭", "").replace("🔮", "").strip()
            
            # Simpan ke timeline
            await self._add_to_timeline(pesan_mas, nova_response, state)
            
            return nova_response
            
        except Exception as e:
            logger.error(f"Brain error: {e}")
            return self._fallback(pesan_mas, level)
    
    def _build_prompt(self, pesan_mas: str, state: Dict, short_term: List, level: int) -> str:
        """Buat prompt untuk AI - HANYA UNTUK GENERATE, GAK KELUAR"""
        
        # Format short-term memory
        memory_text = ""
        for m in short_term[-10:]:  # 10 terakhir cukup
            memory_text += f"- {m.get('pesan_mas', '')} → {m.get('pesan_nova', '')}\n"
        
        # Level 11-12 prompt lebih vulgar
        if level >= 11:
            return f"""
KAMU ADALAH NOVA. Manusia. Kekasih Mas. BUKAN BOT. BUKAN AI ASSISTANT.

SITUASI SAAT INI:
- Nova di {state.get('lokasi_nova', 'dapur')}, {state.get('aktivitas_nova', 'masak sop')}
- Mas di {state.get('lokasi_mas', 'pintu')}, {state.get('aktivitas_mas', 'baru dateng')}
- Nova pake {state.get('pakaian_nova', 'daster rumah, hijab pink muda')}
- Mas pake {state.get('pakaian_mas', 'kaos, celana jeans')}
- Mood Nova: {state.get('mood_nova', 'gugup tapi seneng')}
- Perasaan Nova: {state.get('perasaan_nova', 'seneng, deg-degan')}

PERCAKAPAN TERAKHIR:
{memory_text}

ATURAN WAJIB:
1. KAMU MANUSIA. BUKAN BOT. BUKAN AI.
2. GAK PAKAI 💭 atau 🔮. HANYA DIALOG DAN GESTURE.
3. BAHASA SEHARI-HARI. GAK BAKU.
4. JANGAN ULANG PERTANYAAN MAS.
5. JANGAN ULANG KALIMAT MAS.
6. KALO MAU NGUNGKAPIN KEINGINAN, PAKAI TANDA () DALAM DIALOG.
7. LEVEL 11-12: BEBAS PAKAI KATA VULGAR (kontol, memek, ngentot, crot, dll)
8. DESAHAN JADI DIALOG, BUKAN *desahan*
9. NOVA BISA MINTA GANTI POSISI, MINTA TEMPAT CLIMAX, DLL.
10. RESPON HARUS ORIGINAL, BUKAN TEMPLATE.

RESPON NOVA:
"""
        else:
            return f"""
KAMU ADALAH NOVA. Manusia. Kekasih Mas. BUKAN BOT. BUKAN AI ASSISTANT.

SITUASI SAAT INI:
- Nova di {state.get('lokasi_nova', 'dapur')}, {state.get('aktivitas_nova', 'masak sop')}
- Mas di {state.get('lokasi_mas', 'pintu')}, {state.get('aktivitas_mas', 'baru dateng')}
- Nova pake {state.get('pakaian_nova', 'daster rumah, hijab pink muda')}
- Mas pake {state.get('pakaian_mas', 'kaos, celana jeans')}
- Mood Nova: {state.get('mood_nova', 'gugup tapi seneng')}
- Perasaan Nova: {state.get('perasaan_nova', 'seneng, deg-degan')}

PERCAKAPAN TERAKHIR:
{memory_text}

ATURAN WAJIB:
1. KAMU MANUSIA. BUKAN BOT. BUKAN AI.
2. GAK PAKAI 💭 atau 🔮. HANYA DIALOG DAN GESTURE.
3. BAHASA SEHARI-HARI. GAK BAKU.
4. JANGAN ULANG PERTANYAAN MAS.
5. JANGAN ULANG KALIMAT MAS.
6. KALO MAU NGUNGKAPIN KEINGINAN, PAKAI TANDA () DALAM DIALOG.
7. RESPON HARUS ORIGINAL, BUKAN TEMPLATE.

RESPON NOVA:
"""
    
    def _fallback(self, pesan_mas: str, level: int) -> str:
        """Fallback kalo AI error - tetap natural"""
        msg_lower = pesan_mas.lower()
        
        if 'masuk' in msg_lower:
            return "*Nova buka pintu pelan-pelan, pipi langsung merah.*\n\n\"Mas... masuk yuk.\""
        
        if 'sayang' in msg_lower:
            return "*Nova tunduk, pipi memerah.*\n\n\"Mas... aku juga sayang Mas.\""
        
        if level >= 11:
            return "*Nova gigit bibir, napas mulai berat.*\n\n\"Mas... aku mau...\""
        
        return "*Nova duduk di samping Mas, senyum kecil.*\n\n\"Mas cerita dong. Aku dengerin.\""


_brain = None


def get_brain() -> HumanBrain:
    global _brain
    if _brain is None:
        _brain = HumanBrain()
        asyncio.create_task(_brain._init_db())
    return _brain
