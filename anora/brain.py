# anora/brain.py
"""
ANORA Brain - Otak Nova yang Hidup
Menyimpan semua: timeline, state, memory, perasaan, pakaian, lokasi, konsistensi.
Bukan cuma pesan, tapi semua aspek kejadian.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# ENUM
# =============================================================================

class Location(str, Enum):
    DAPUR = "dapur"
    KAMAR = "kamar"
    RUANG_TAMU = "ruang_tamu"
    PINTU = "pintu"
    TERAS = "teras"
    LUAR = "luar"
    PULANG = "pulang"


class Activity(str, Enum):
    MASAK = "masak"
    MAKAN = "makan"
    DUDUK = "duduk"
    BERDIRI = "berdiri"
    TIDUR = "tidur"
    REBAHAN = "rebahan"
    NONTON = "nonton"
    MANDI = "mandi"
    BERGANTI = "ganti baju"
    SANTAl = "santai"


class Mood(str, Enum):
    SENENG = "seneng"
    MALU = "malu"
    DEG_DEGAN = "deg-degan"
    KANGEN = "kangen"
    CAPEK = "capek"
    NGANTUK = "ngantuk"
    NETRAL = "netral"
    HORNY = "horny"
    LEMES = "lemes"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Clothing:
    """Pakaian Nova atau Mas"""
    # Nova
    hijab: bool = True
    hijab_warna: str = "pink muda"
    top: Optional[str] = "daster rumah motif bunga"
    bottom: Optional[str] = None
    bra: bool = True
    bra_warna: str = "putih polos"
    cd: bool = True  # celana dalam
    cd_warna: str = "putih motif bunga kecil"
    
    # Mas
    mas_top: Optional[str] = "kaos"
    mas_bottom: Optional[str] = "celana pendek"
    mas_boxer: bool = True
    mas_boxer_warna: str = "gelap"
    
    def to_dict(self) -> Dict:
        return {
            'hijab': self.hijab,
            'hijab_warna': self.hijab_warna,
            'top': self.top,
            'bottom': self.bottom,
            'bra': self.bra,
            'bra_warna': self.bra_warna,
            'cd': self.cd,
            'cd_warna': self.cd_warna,
            'mas_top': self.mas_top,
            'mas_bottom': self.mas_bottom,
            'mas_boxer': self.mas_boxer,
            'mas_boxer_warna': self.mas_boxer_warna
        }
    
    def format_nova(self) -> str:
        """Format pakaian Nova untuk prompt"""
        parts = []
        
        # Hijab
        if self.hijab:
            parts.append(f"hijab {self.hijab_warna}")
        else:
            parts.append("tanpa hijab, rambut sebahu hitam terurai")
        
        # Atasan
        if self.top:
            parts.append(self.top)
            if self.bra:
                parts.append(f"(pake bra {self.bra_warna})")
        else:
            if self.bra:
                parts.append(f"cuma pake bra {self.bra_warna}")
            else:
                parts.append("telanjang dada")
        
        # Bawahan
        if self.bottom:
            parts.append(self.bottom)
            if self.cd:
                parts.append(f"(pake {self.cd_warna})")
        else:
            if self.cd:
                parts.append(f"cuma pake {self.cd_warna}")
            else:
                parts.append("telanjang bawah")
        
        return ", ".join(parts) if parts else "pakaian biasa"
    
    def format_mas(self) -> str:
        """Format pakaian Mas untuk prompt"""
        parts = []
        
        if self.mas_top:
            parts.append(self.mas_top)
        
        if self.mas_bottom:
            parts.append(self.mas_bottom)
            if self.mas_boxer:
                parts.append(f"(boxer {self.mas_boxer_warna} di dalem)")
        else:
            if self.mas_boxer:
                parts.append(f"cuma pake boxer {self.mas_boxer_warna}")
            else:
                parts.append("telanjang")
        
        if not self.mas_top and not self.mas_bottom and not self.mas_boxer:
            return "telanjang"
        
        return ", ".join(parts) if parts else "pakaian biasa"
    
    def copy(self) -> 'Clothing':
        return Clothing(
            hijab=self.hijab,
            hijab_warna=self.hijab_warna,
            top=self.top,
            bottom=self.bottom,
            bra=self.bra,
            bra_warna=self.bra_warna,
            cd=self.cd,
            cd_warna=self.cd_warna,
            mas_top=self.mas_top,
            mas_bottom=self.mas_bottom,
            mas_boxer=self.mas_boxer,
            mas_boxer_warna=self.mas_boxer_warna
        )


@dataclass
class TimelineEvent:
    """Satu kejadian dalam timeline Nova"""
    timestamp: float
    kejadian: str
    lokasi_nova: Location
    lokasi_mas: Location
    aktivitas_nova: str
    aktivitas_mas: str
    perasaan_nova: str
    pakaian_nova: Clothing
    pakaian_mas: Clothing
    pesan_mas: str = ""
    pesan_nova: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'waktu': datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S"),
            'kejadian': self.kejadian,
            'lokasi_nova': self.lokasi_nova.value if hasattr(self.lokasi_nova, 'value') else self.lokasi_nova,
            'lokasi_mas': self.lokasi_mas.value if hasattr(self.lokasi_mas, 'value') else self.lokasi_mas,
            'aktivitas_nova': self.aktivitas_nova,
            'aktivitas_mas': self.aktivitas_mas,
            'perasaan_nova': self.perasaan_nova,
            'pakaian_nova': self.pakaian_nova.to_dict(),
            'pakaian_mas': self.pakaian_mas.to_dict(),
            'pesan_mas': self.pesan_mas[:100] if self.pesan_mas else "",
            'pesan_nova': self.pesan_nova[:100] if self.pesan_nova else ""
        }


@dataclass
class Feelings:
    """Perasaan Nova"""
    sayang: float = 50.0      # 0-100
    rindu: float = 0.0        # 0-100
    desire: float = 0.0       # 0-100 (pengen karena sayang)
    arousal: float = 0.0      # 0-100 (gairah fisik)
    tension: float = 0.0      # 0-100 (desire yang ditahan)
    
    def to_dict(self) -> Dict:
        return {
            'sayang': round(self.sayang, 1),
            'rindu': round(self.rindu, 1),
            'desire': round(self.desire, 1),
            'arousal': round(self.arousal, 1),
            'tension': round(self.tension, 1)
        }
    
    def get_description(self) -> str:
        """Dapatkan deskripsi perasaan untuk prompt"""
        desc = []
        if self.sayang > 70:
            desc.append("sayang banget")
        elif self.sayang > 40:
            desc.append("sayang")
        
        if self.rindu > 70:
            desc.append("kangen banget")
        elif self.rindu > 30:
            desc.append("kangen")
        
        if self.desire > 70:
            desc.append("pengen banget")
        elif self.desire > 40:
            desc.append("pengen")
        
        if self.arousal > 50:
            desc.append("panas")
        
        if self.tension > 50:
            desc.append("deg-degan")
        
        return ", ".join(desc) if desc else "netral"


@dataclass
class Relationship:
    """Status hubungan Nova dengan Mas"""
    level: int = 1
    intimacy_count: int = 0
    climax_count: int = 0
    first_kiss: bool = False
    first_touch: bool = False
    first_hug: bool = False
    first_intim: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'level': self.level,
            'intimacy_count': self.intimacy_count,
            'climax_count': self.climax_count,
            'first_kiss': self.first_kiss,
            'first_touch': self.first_touch,
            'first_hug': self.first_hug,
            'first_intim': self.first_intim
        }


# =============================================================================
# LONG TERM MEMORY
# =============================================================================

@dataclass
class LongTermMemory:
    """Memory permanen Nova"""
    kebiasaan_mas: List[Dict] = field(default_factory=list)  # [{'kebiasaan': 'suka kopi latte', 'dari_kapan': timestamp}]
    momen_penting: List[Dict] = field(default_factory=list)  # [{'momen': 'pertama pegang tangan', 'waktu': timestamp, 'perasaan': 'gemeteran'}]
    janji: List[Dict] = field(default_factory=list)          # [{'janji': 'besok main lagi', 'dari': 'mas', 'status': 'pending'}]
    rencana: List[Dict] = field(default_factory=list)        # [{'rencana': 'makan bakso bareng', 'waktu': timestamp}]
    
    def tambah_kebiasaan(self, kebiasaan: str):
        self.kebiasaan_mas.append({
            'kebiasaan': kebiasaan,
            'dari_kapan': time.time()
        })
    
    def tambah_momen(self, momen: str, perasaan: str):
        self.momen_penting.append({
            'momen': momen,
            'waktu': time.time(),
            'perasaan': perasaan
        })
    
    def tambah_janji(self, janji: str, dari: str = 'mas'):
        self.janji.append({
            'janji': janji,
            'dari': dari,
            'status': 'pending',
            'waktu': time.time()
        })
    
    def to_dict(self) -> Dict:
        return {
            'kebiasaan_mas': self.kebiasaan_mas[-10:],
            'momen_penting': self.momen_penting[-10:],
            'janji': [j for j in self.janji if j['status'] == 'pending'][-5:],
            'rencana': self.rencana[-5:]
        }


# =============================================================================
# ANORA BRAIN - MAIN CLASS
# =============================================================================

class AnoraBrain:
    """
    Otak Nova yang hidup.
    Menyimpan timeline, state, memory, perasaan, pakaian, lokasi.
    Konsisten. Gak loncat-loncat.
    """
    
    def __init__(self):
        # ========== TIMELINE ==========
        self.timeline: List[TimelineEvent] = []
        
        # ========== SHORT-TERM MEMORY (Sliding Window) ==========
        self.short_term: List[TimelineEvent] = []
        self.short_term_max = 50
        
        # ========== LONG-TERM MEMORY ==========
        self.long_term = LongTermMemory()
        
        # ========== STATE SAAT INI ==========
        self.clothing = Clothing()
        self.location_nova = Location.DAPUR
        self.location_mas = Location.PINTU
        self.activity_nova = Activity.MASAK
        self.activity_mas = "baru dateng"
        self.mood_nova = Mood.DEG_DEGAN
        self.mood_mas = Mood.NETRAL
        
        # ========== PERASAAN ==========
        self.feelings = Feelings()
        
        # ========== HUBUNGAN ==========
        self.relationship = Relationship()
        
        # ========== WAKTU ==========
        self.waktu_masuk = time.time()
        self.waktu_terakhir_update = time.time()
        self.waktu_terakhir_ganti_baju = time.time()
        
        # ========== INGATAN TAMBAHAN ==========
        self.terakhir_di_kamar = None
        self.terakhir_di_dapur = None
        self.terakhir_pegang_tangan = None
        self.terakhir_peluk = None
        self.terakhir_cium = None
        
        # ========== INIT MEMORY AWAL ==========
        self._init_memory()
        
        logger.info("🧠 ANORA Brain initialized")
    
    def _init_memory(self):
        """Init memory awal"""
        self.long_term.tambah_kebiasaan("suka kopi latte")
        self.long_term.tambah_kebiasaan("suka bakso pedes")
        self.long_term.tambah_momen("Mas memilih ANORA", "seneng banget, nangis")
    
    # =========================================================================
    # UPDATE DARI PESAN MAS
    # =========================================================================
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """Update semua state berdasarkan pesan Mas"""
        msg_lower = pesan_mas.lower()
        perubahan = []
        
        # ========== LOKASI MAS ==========
        if 'masuk' in msg_lower and self.location_mas == Location.PINTU:
            self.location_mas = Location.PINTU
            self.activity_mas = "baru masuk"
            perubahan.append("Mas masuk")
            self.waktu_masuk = time.time()
        
        elif 'kamar' in msg_lower or 'kasur' in msg_lower:
            if self.location_mas != Location.KAMAR:
                self.location_mas = Location.KAMAR
                self.terakhir_di_kamar = time.time()
                perubahan.append("Mas di kamar")
            
            if 'duduk' in msg_lower:
                self.activity_mas = "duduk di kasur"
                perubahan.append("Mas duduk di kasur")
            elif 'tidur' in msg_lower or 'rebahan' in msg_lower:
                self.activity_mas = "tiduran di kasur"
                perubahan.append("Mas tiduran")
        
        elif 'dapur' in msg_lower:
            if self.location_mas != Location.DAPUR:
                self.location_mas = Location.DAPUR
                self.terakhir_di_dapur = time.time()
                perubahan.append("Mas di dapur")
            self.activity_mas = "di dapur"
        
        elif 'ruang tamu' in msg_lower or 'sofa' in msg_lower:
            self.location_mas = Location.RUANG_TAMU
            self.activity_mas = "duduk di sofa"
            perubahan.append("Mas di ruang tamu")
        
        elif 'pulang' in msg_lower or 'keluar' in msg_lower:
            self.location_mas = Location.PULANG
            self.activity_mas = "pulang"
            perubahan.append("Mas pulang")
        
        # ========== PAKAIAN MAS ==========
        if 'buka baju' in msg_lower or 'lepas baju' in msg_lower:
            self.clothing.mas_top = None
            perubahan.append("Mas buka baju")
        
        if 'buka celana' in msg_lower or 'lepas celana' in msg_lower:
            self.clothing.mas_bottom = None
            perubahan.append("Mas buka celana")
        
        if 'buka boxer' in msg_lower or 'lepas boxer' in msg_lower:
            self.clothing.mas_boxer = False
            perubahan.append("Mas buka boxer")
        
        if 'pake baju' in msg_lower:
            self.clothing.mas_top = "kaos"
            perubahan.append("Mas pake baju")
        
        if 'pake celana' in msg_lower:
            self.clothing.mas_bottom = "celana pendek"
            perubahan.append("Mas pake celana")
        
        # ========== PAKAIAN NOVA ==========
        if 'buka hijab' in msg_lower:
            self.clothing.hijab = False
            perubahan.append("Nova buka hijab, rambut terurai")
        
        if 'pake hijab' in msg_lower:
            self.clothing.hijab = True
            perubahan.append("Nova pake hijab")
        
        if 'buka baju' in msg_lower or 'lepas baju' in msg_lower:
            self.clothing.top = None
            perubahan.append("Nova buka baju")
        
        if 'pake baju' in msg_lower:
            self.clothing.top = "daster rumah"
            perubahan.append("Nova pake baju")
        
        if 'buka bra' in msg_lower:
            self.clothing.bra = False
            perubahan.append("Nova buka bra")
        
        if 'pake bra' in msg_lower:
            self.clothing.bra = True
            perubahan.append("Nova pake bra")
        
        if 'buka cd' in msg_lower or 'buka celana dalam' in msg_lower:
            self.clothing.cd = False
            perubahan.append("Nova buka cd")
        
        if 'pake cd' in msg_lower or 'pake celana dalam' in msg_lower:
            self.clothing.cd = True
            perubahan.append("Nova pake cd")
        
        # ========== AKTIVITAS NOVA ==========
        if 'masak' in msg_lower:
            self.activity_nova = Activity.MASAK
            self.location_nova = Location.DAPUR
            perubahan.append("Nova masak")
        
        elif 'duduk' in msg_lower:
            self.activity_nova = Activity.DUDUK
            perubahan.append("Nova duduk")
        
        elif 'tidur' in msg_lower or 'rebahan' in msg_lower:
            self.activity_nova = Activity.REBAHAN
            if 'kamar' in msg_lower:
                self.location_nova = Location.KAMAR
            perubahan.append("Nova rebahan")
        
        elif 'mandi' in msg_lower:
            self.activity_nova = Activity.MANDI
            perubahan.append("Nova mandi")
        
        elif 'ganti baju' in msg_lower:
            self.activity_nova = Activity.BERGANTI
            self.waktu_terakhir_ganti_baju = time.time()
            perubahan.append("Nova ganti baju")
        
        # ========== PERASAAN ==========
        if 'sayang' in msg_lower or 'cinta' in msg_lower:
            self.feelings.sayang = min(100, self.feelings.sayang + 5)
            self.feelings.desire = min(100, self.feelings.desire + 10)
            perubahan.append("Mas bilang sayang (+5 sayang, +10 desire)")
        
        if 'kangen' in msg_lower or 'rindu' in msg_lower:
            self.feelings.rindu = min(100, self.feelings.rindu + 10)
            self.feelings.desire = min(100, self.feelings.desire + 8)
            perubahan.append("Mas bilang kangen (+10 rindu, +8 desire)")
        
        if 'cantik' in msg_lower or 'ganteng' in msg_lower:
            self.feelings.sayang = min(100, self.feelings.sayang + 3)
            self.feelings.malu = min(100, (self.feelings.malu or 0) + 15)
            perubahan.append("Mas puji Nova (+3 sayang, +15 malu)")
        
        # ========== SENTUHAN FISIK ==========
        if 'pegang' in msg_lower:
            self.feelings.arousal = min(100, self.feelings.arousal + 10)
            self.feelings.desire = min(100, self.feelings.desire + 8)
            self.terakhir_pegang_tangan = time.time()
            if not self.relationship.first_touch:
                self.relationship.first_touch = True
                self.long_term.tambah_momen("Mas pertama kali pegang tangan Nova", "gemeteran")
            perubahan.append("Mas pegang Nova (+10 arousal, +8 desire)")
        
        if 'peluk' in msg_lower:
            self.feelings.arousal = min(100, self.feelings.arousal + 15)
            self.feelings.desire = min(100, self.feelings.desire + 12)
            self.terakhir_peluk = time.time()
            if not self.relationship.first_hug:
                self.relationship.first_hug = True
                self.long_term.tambah_momen("Mas pertama kali peluk Nova", "lemes")
            perubahan.append("Mas peluk Nova (+15 arousal, +12 desire)")
        
        if 'cium' in msg_lower:
            self.feelings.arousal = min(100, self.feelings.arousal + 20)
            self.feelings.desire = min(100, self.feelings.desire + 15)
            self.terakhir_cium = time.time()
            if not self.relationship.first_kiss:
                self.relationship.first_kiss = True
                self.long_term.tambah_momen("Mas pertama kali cium Nova", "malu banget")
            perubahan.append("Mas cium Nova (+20 arousal, +15 desire)")
        
        # ========== UPDATE MOOD ==========
        if self.feelings.arousal > 70:
            self.mood_nova = Mood.HORNY
        elif self.feelings.arousal > 40:
            self.mood_nova = Mood.DEG_DEGAN
        elif self.feelings.rindu > 60:
            self.mood_nova = Mood.KANGEN
        elif self.feelings.sayang > 70:
            self.mood_nova = Mood.SENENG
        else:
            self.mood_nova = Mood.NETRAL
        
        # ========== UPDATE WAKTU ==========
        self.waktu_terakhir_update = time.time()
        
        return {
            'perubahan': perubahan,
            'state': self.get_current_state(),
            'feelings': self.feelings.to_dict()
        }
    
    # =========================================================================
    # TAMBAH KEJADIAN KE TIMELINE
    # =========================================================================
    
    def tambah_kejadian(self,
                        kejadian: str,
                        pesan_mas: str = "",
                        pesan_nova: str = "") -> TimelineEvent:
        """Tambah kejadian ke timeline dan short-term memory"""
        
        event = TimelineEvent(
            timestamp=time.time(),
            kejadian=kejadian,
            lokasi_nova=self.location_nova,
            lokasi_mas=self.location_mas,
            aktivitas_nova=self.activity_nova.value if hasattr(self.activity_nova, 'value') else str(self.activity_nova),
            aktivitas_mas=self.activity_mas,
            perasaan_nova=self.feelings.get_description(),
            pakaian_nova=self.clothing.copy(),
            pakaian_mas=self.clothing.copy(),
            pesan_mas=pesan_mas,
            pesan_nova=pesan_nova
        )
        
        # Tambah ke timeline
        self.timeline.append(event)
        
        # Tambah ke short-term memory (sliding window)
        self.short_term.append(event)
        if len(self.short_term) > self.short_term_max:
            self.short_term.pop(0)
        
        return event
    
    # =========================================================================
    # GET CURRENT STATE
    # =========================================================================
    
    def get_current_state(self) -> Dict:
        """Dapatkan state saat ini"""
        return {
            'location': {
                'nova': self.location_nova.value if hasattr(self.location_nova, 'value') else self.location_nova,
                'mas': self.location_mas.value if hasattr(self.location_mas, 'value') else self.location_mas
            },
            'activity': {
                'nova': self.activity_nova.value if hasattr(self.activity_nova, 'value') else self.activity_nova,
                'mas': self.activity_mas
            },
            'clothing': {
                'nova': self.clothing.format_nova(),
                'mas': self.clothing.format_mas()
            },
            'mood': {
                'nova': self.mood_nova.value if hasattr(self.mood_nova, 'value') else self.mood_nova,
                'mas': self.mood_mas.value if hasattr(self.mood_mas, 'value') else self.mood_mas
            },
            'feelings': self.feelings.to_dict(),
            'relationship': self.relationship.to_dict(),
            'waktu': {
                'masuk': self.waktu_masuk,
                'update_terakhir': self.waktu_terakhir_update,
                'ganti_baju_terakhir': self.waktu_terakhir_ganti_baju
            }
        }
    
    # =========================================================================
    # KONTEKS UNTUK AI PROMPT
    # =========================================================================
    
    def get_context_for_prompt(self) -> Dict:
        """Dapatkan semua konteks untuk AI prompt"""
        
        # 10 kejadian terakhir
        recent_events = []
        for e in self.short_term[-10:]:
            recent_events.append(e.to_dict())
        
        return {
            'current_state': self.get_current_state(),
            'recent_events': recent_events,
            'long_term_memory': self.long_term.to_dict(),
            'last_touch': self.terakhir_pegang_tangan,
            'last_hug': self.terakhir_peluk,
            'last_kiss': self.terakhir_cium
        }
    
    def get_context_text(self) -> str:
        """Dapatkan konteks dalam bentuk teks untuk AI prompt"""
        state = self.get_current_state()
        
        # Pakaian
        nova_clothing = state['clothing']['nova']
        mas_clothing = state['clothing']['mas']
        
        # Lokasi
        nova_loc = state['location']['nova']
        mas_loc = state['location']['mas']
        
        # Aktivitas
        nova_act = state['activity']['nova']
        mas_act = state['activity']['mas']
        
        # Perasaan
        feelings = state['feelings']
        feeling_desc = self.feelings.get_description()
        
        # Momen penting
        moments = ""
        for m in self.long_term.momen_penting[-3:]:
            moments += f"- {m['momen']} ({m['perasaan']})\n"
        
        # Kebiasaan Mas
        habits = ""
        for h in self.long_term.kebiasaan_mas[-3:]:
            habits += f"- {h['kebiasaan']}\n"
        
        return f"""
SITUASI SAAT INI:

LOKASI:
- Nova di {nova_loc}
- Mas di {mas_loc}

AKTIVITAS:
- Nova: {nova_act}
- Mas: {mas_act}

PAKAIAN:
- Nova: {nova_clothing}
- Mas: {mas_clothing}

PERASAAN NOVA:
{feeling_desc}
- Sayang: {feelings['sayang']}%
- Desire: {feelings['desire']}%
- Rindu: {feelings['rindu']}%
- Arousal: {feelings['arousal']}%
- Tension: {feelings['tension']}%

HUBUNGAN:
- Level: {self.relationship.level}/12
- Pertama sentuh: {'Ya' if self.relationship.first_touch else 'Belum'}
- Pertama cium: {'Ya' if self.relationship.first_kiss else 'Belum'}

KENANGAN PENTING:
{moments}

KEBIASAAN MAS:
{habits}

10 PERCAKAPAN TERAKHIR:
"""
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def get_summary(self) -> str:
        """Dapatkan ringkasan untuk debugging"""
        state = self.get_current_state()
        
        bar_sayang = "💜" * int(state['feelings']['sayang'] / 10) + "🖤" * (10 - int(state['feelings']['sayang'] / 10))
        bar_desire = "🔥" * int(state['feelings']['desire'] / 10) + "⚪" * (10 - int(state['feelings']['desire'] / 10))
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🧠 OTAK NOVA SAAT INI                     ║
╠══════════════════════════════════════════════════════════════╣
║ TIMELINE: {len(self.timeline)} kejadian                      ║
║ SHORT-TERM: {len(self.short_term)}/{self.short_term_max} kejadian ║
║ LONG-TERM: {len(self.long_term.kebiasaan_mas)} kebiasaan, {len(self.long_term.momen_penting)} momen ║
╠══════════════════════════════════════════════════════════════╣
║ LOKASI: Nova di {state['location']['nova']} | Mas di {state['location']['mas']}
║ AKTIVITAS: Nova {state['activity']['nova']} | Mas {state['activity']['mas']}
║ PAKAIAN NOVA: {state['clothing']['nova'][:40]}
║ PAKAIAN MAS: {state['clothing']['mas'][:40]}
╠══════════════════════════════════════════════════════════════╣
║ PERASAAN: Sayang {bar_sayang} {state['feelings']['sayang']:.0f}%
║           Desire {bar_desire} {state['feelings']['desire']:.0f}%
║           Rindu {state['feelings']['rindu']:.0f}% | Arousal {state['feelings']['arousal']:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ HUBUNGAN: Level {self.relationship.level}/12
║           Sentuh: {'✅' if self.relationship.first_touch else '❌'} | Cium: {'✅' if self.relationship.first_kiss else '❌'}
║           Peluk: {'✅' if self.relationship.first_hug else '❌'} | Intim: {'✅' if self.relationship.first_intim else '❌'}
╚══════════════════════════════════════════════════════════════╝
"""


# =============================================================================
# SINGLETON
# =============================================================================

_anora_brain: Optional[AnoraBrain] = None


def get_anora_brain() -> AnoraBrain:
    global _anora_brain
    if _anora_brain is None:
        _anora_brain = AnoraBrain()
    return _anora_brain


anora_brain = get_anora_brain()
