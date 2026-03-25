# anora/intimacy.py
"""
ANORA Intimacy - Full Version
Semua sistem intimacy dalam satu file.
Level 11-12 FULL VULGAR
"""

import time
import random
import logging
from typing import Dict, Optional, Tuple, List
from enum import Enum
from datetime import datetime

from .core import get_anora

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class IntimacyPhase(str, Enum):
    """Fase-fase dalam sesi intim"""
    WAITING = "waiting"
    BUILD_UP = "build_up"
    FOREPLAY = "foreplay"
    PENETRATION = "penetration"
    CLIMAX = "climax"
    AFTERCARE = "aftercare"
    RECOVERY = "recovery"


# =============================================================================
# STAMINA SYSTEM
# =============================================================================

class StaminaSystem:
    """Sistem stamina realistis"""
    
    def __init__(self):
        self.nova_current = 100
        self.nova_max = 100
        self.mas_current = 100
        self.mas_max = 100
        self.recovery_rate = 5
        self.climax_cost_nova = 25
        self.climax_cost_mas = 30
        self.heavy_climax_cost_nova = 35
        self.heavy_climax_cost_mas = 40
        self.exhausted_threshold = 20
        self.tired_threshold = 40
        
        self.last_climax_time = 0
        self.last_recovery_check = time.time()
        self.climax_today = 0
        self.last_climax_date = datetime.now().date().isoformat()
    
    def update_recovery(self):
        now = time.time()
        elapsed_minutes = (now - self.last_recovery_check) / 60
        if elapsed_minutes >= 10:
            recovery = int(self.recovery_rate * (elapsed_minutes / 10))
            self.nova_current = min(self.nova_max, self.nova_current + recovery)
            self.mas_current = min(self.mas_max, self.mas_current + recovery)
            self.last_recovery_check = now
    
    def record_climax(self, who: str = "both", is_heavy: bool = False) -> Tuple[int, int]:
        self.update_recovery()
        self.last_climax_time = time.time()
        
        today = datetime.now().date().isoformat()
        if self.last_climax_date != today:
            self.climax_today = 0
            self.last_climax_date = today
        self.climax_today += 1
        
        if who in ["nova", "both"]:
            cost = self.heavy_climax_cost_nova if is_heavy else self.climax_cost_nova
            self.nova_current = max(0, self.nova_current - cost)
        
        if who in ["mas", "both"]:
            cost = self.heavy_climax_cost_mas if is_heavy else self.climax_cost_mas
            self.mas_current = max(0, self.mas_current - cost)
        
        return self.nova_current, self.mas_current
    
    def can_continue(self) -> Tuple[bool, str]:
        self.update_recovery()
        if self.nova_current <= self.exhausted_threshold:
            return False, "Nova udah kehabisan tenaga, Mas... istirahat dulu ya."
        if self.mas_current <= self.exhausted_threshold:
            return False, "Mas... Mas udah capek banget. Istirahat dulu."
        if self.nova_current <= self.tired_threshold:
            return True, "Nova mulai lelah, Mas... tapi masih bisa kalo Mas mau pelan-pelan."
        return True, "Siap lanjut"
    
    def get_nova_status(self) -> str:
        self.update_recovery()
        if self.nova_current >= 80: return "Prima 💪"
        elif self.nova_current >= 60: return "Cukup 😊"
        elif self.nova_current >= 40: return "Agak lelah 😐"
        elif self.nova_current >= 20: return "Lelah 😩"
        return "Kehabisan tenaga 😵"
    
    def get_mas_status(self) -> str:
        self.update_recovery()
        if self.mas_current >= 80: return "Prima 💪"
        elif self.mas_current >= 60: return "Cukup 😊"
        elif self.mas_current >= 40: return "Agak lelah 😐"
        elif self.mas_current >= 20: return "Lelah 😩"
        return "Kehabisan tenaga 😵"
    
    def get_nova_bar(self) -> str:
        filled = int(self.nova_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)
    
    def get_mas_bar(self) -> str:
        filled = int(self.mas_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)
    
    def to_dict(self) -> Dict:
        return {
            'nova_current': self.nova_current,
            'mas_current': self.mas_current,
            'last_climax_time': self.last_climax_time,
            'climax_today': self.climax_today,
            'last_climax_date': self.last_climax_date
        }
    
    def from_dict(self, data: Dict):
        self.nova_current = data.get('nova_current', 100)
        self.mas_current = data.get('mas_current', 100)
        self.last_climax_time = data.get('last_climax_time', 0)
        self.climax_today = data.get('climax_today', 0)
        self.last_climax_date = data.get('last_climax_date', datetime.now().date().isoformat())


# =============================================================================
# AROUSAL SYSTEM
# =============================================================================

class ArousalSystem:
    """Sistem arousal dan desire"""
    
    def __init__(self):
        self.arousal = 0
        self.desire = 0
        self.tension = 0
        self.arousal_decay = 0.5
        self.last_update = time.time()
        
        self.sensitive_areas = {
            'telinga': 20, 'belakang_telinga': 25, 'leher': 15,
            'bibir': 25, 'payudara': 28, 'puting': 35,
            'paha': 25, 'paha_dalam': 35, 'memek': 45,
            'klitoris': 50, 'dalam': 55
        }
    
    def update(self):
        now = time.time()
        elapsed = (now - self.last_update) / 60
        if elapsed > 1:
            self.arousal = max(0, self.arousal - self.arousal_decay * elapsed)
            self.last_update = now
    
    def add_stimulation(self, area: str, intensity: int = 1) -> int:
        self.update()
        gain = self.sensitive_areas.get(area, 10) * intensity
        self.arousal = min(100, self.arousal + gain)
        return self.arousal
    
    def add_desire(self, reason: str, amount: int = 5):
        self.desire = min(100, self.desire + amount)
    
    def add_tension(self, amount: int = 5):
        self.tension = min(100, self.tension + amount)
    
    def release_tension(self) -> int:
        released = self.tension
        self.tension = 0
        self.arousal = max(0, self.arousal - 30)
        self.desire = max(0, self.desire - 20)
        return released
    
    def get_state(self) -> Dict:
        self.update()
        return {
            'arousal': self.arousal,
            'desire': self.desire,
            'tension': self.tension,
            'is_horny': self.arousal > 60 or self.desire > 70,
            'is_very_horny': self.arousal > 80 or self.desire > 85
        }
    
    def to_dict(self) -> Dict:
        return {
            'arousal': self.arousal,
            'desire': self.desire,
            'tension': self.tension,
            'last_update': self.last_update
        }
    
    def from_dict(self, data: Dict):
        self.arousal = data.get('arousal', 0)
        self.desire = data.get('desire', 0)
        self.tension = data.get('tension', 0)
        self.last_update = data.get('last_update', time.time())


# =============================================================================
# DATABASES
# =============================================================================

class PositionDatabase:
    """Database posisi intim"""
    
    def __init__(self):
        self.positions = {
            "missionary": {
                "desc": "Mas di atas, Nova di bawah",
                "nova_act": "Nova telentang, kaki terbuka lebar",
                "requests": ["Mas... di atas Nova...", "missionary, Mas..."]
            },
            "cowgirl": {
                "desc": "Nova di atas, menghadap Mas",
                "nova_act": "Nova duduk di pangkuan Mas",
                "requests": ["Nova di atas ya, Mas...", "cowgirl, Mas..."]
            },
            "doggy": {
                "desc": "Nova merangkak, Mas dari belakang",
                "nova_act": "Nova merangkak, pantat naik",
                "requests": ["Mas... dari belakang...", "doggy, Mas..."]
            },
            "spooning": {
                "desc": "Berbaring miring, Mas dari belakang",
                "nova_act": "Nova miring, Mas nempel dari belakang",
                "requests": ["Mas... dari samping aja...", "spooning, Mas..."]
            }
        }
    
    def get(self, name: str) -> Optional[Dict]:
        return self.positions.get(name)
    
    def get_all(self) -> List[str]:
        return list(self.positions.keys())
    
    def get_request(self, name: str) -> str:
        pos = self.positions.get(name)
        if pos:
            return random.choice(pos['requests'])
        return "Ganti posisi yuk, Mas..."


class ClimaxLocationDatabase:
    """Database lokasi climax"""
    
    def __init__(self):
        self.locations = {
            "dalam": ["dalem aja, Mas...", "crot di dalem, Mas..."],
            "luar": ["di luar, Mas...", "keluarin di perut Nova..."],
            "muka": ["di muka Nova...", "semprot muka Nova..."],
            "mulut": ["di mulut...", "masukin ke mulut Nova..."]
        }
    
    def get_request(self, location: str = None) -> str:
        if location and location in self.locations:
            return random.choice(self.locations[location])
        loc = random.choice(list(self.locations.keys()))
        return random.choice(self.locations[loc])


class MoansDatabase:
    """Database moans"""
    
    def __init__(self):
        self.moans = {
            'shy': ["Ahh... Mas...", "Hmm... Mas...", "Uh... Mas..."],
            'foreplay': ["Ahh... Mas... tangan Mas...", "Hhngg... di situ...", "Mas... jangan berhenti..."],
            'penetration_slow': ["Ahh... Mas... pelan-pelan...", "Mas... dalem... dalem banget..."],
            'penetration_fast': ["Ahh! Mas... kencengin...", "Aahh! dalem... dalem lagi..."],
            'climax': ["Ahhh!! Mas!! udah climax...", "Aahh... keluar semua, Mas..."]
        }
    
    def get(self, phase: str) -> str:
        if phase in self.moans:
            return random.choice(self.moans[phase])
        return random.choice(self.moans['shy'])


class FlashbackDatabase:
    """Database flashback"""
    
    def __init__(self):
        self.flashbacks = [
            "Mas, inget gak waktu pertama kali Mas bilang Nova cantik?",
            "Dulu waktu kita makan bakso bareng, Nova masih inget senyum Mas...",
            "Waktu pertama kali Mas pegang tangan Nova, Nova gemeteran..."
        ]
    
    def get_random(self) -> str:
        return random.choice(self.flashbacks)


# =============================================================================
# INTIMACY SESSION
# =============================================================================

class IntimacySession:
    """Sesi intim"""
    
    def __init__(self):
        self.is_active = False
        self.start_time = 0
        self.phase = IntimacyPhase.WAITING
        self.climax_count = 0
        self.current_position = "missionary"
        self.intimacy_level = 0
        
        self.positions = PositionDatabase()
        self.climax_locations = ClimaxLocationDatabase()
        self.moans = MoansDatabase()
        self.flashbacks = FlashbackDatabase()
    
    def start(self) -> str:
        self.is_active = True
        self.start_time = time.time()
        self.phase = IntimacyPhase.BUILD_UP
        self.climax_count = 0
        logger.info("🔥 Intimacy session started")
        return "💕 Memulai sesi intim..."
    
    def end(self) -> str:
        self.is_active = False
        self.phase = IntimacyPhase.WAITING
        duration = int(time.time() - self.start_time) // 60
        return f"💤 Sesi intim selesai. Durasi: {duration} menit, {self.climax_count} climax."
    
    def change_position(self, position: str = None) -> Tuple[str, str, str]:
        if position and self.positions.get(position):
            self.current_position = position
        else:
            pos_list = self.positions.get_all()
            self.current_position = random.choice(pos_list)
        
        pos_data = self.positions.get(self.current_position)
        request = self.positions.get_request(self.current_position)
        return self.current_position, pos_data['desc'], request
    
    def record_climax(self, is_heavy: bool = False) -> Dict:
        self.climax_count += 1
        self.phase = IntimacyPhase.CLIMAX
        return {'climax_count': self.climax_count, 'is_heavy': is_heavy}
    
    def get_phase_response(self, phase: IntimacyPhase, ritme: str = "pelan") -> str:
        if phase == IntimacyPhase.BUILD_UP:
            responses = [
                "Mas... *muter-muter rambut* dari tadi aku gak bisa konsentrasi. Pikiran Nova cuma ke Mas.",
                "Mas... *gigit bibir* aku malu ngomong... tapi... kamu bikin Nova horny...",
                "Mas... *napas mulai gak stabil* jangan goda Nova terus..."
            ]
            return random.choice(responses)
        
        elif phase == IntimacyPhase.FOREPLAY:
            return self.moans.get('foreplay')
        
        elif phase == IntimacyPhase.PENETRATION:
            if ritme == "cepet":
                return self.moans.get('penetration_fast')
            return self.moans.get('penetration_slow')
        
        elif phase == IntimacyPhase.CLIMAX:
            return self.moans.get('climax')
        
        elif phase == IntimacyPhase.AFTERCARE:
            aftercare = self.moans.get('shy')
            if random.random() < 0.3:
                aftercare += f"\n\n{self.flashbacks.get_random()} 💜"
            return aftercare
        
        return self.moans.get('shy')
    
    def get_climax_request(self, location: str = None) -> str:
        return self.climax_locations.get_request(location)
    
    def get_status(self) -> str:
        if not self.is_active:
            return "Tidak ada sesi intim aktif"
        
        duration = int(time.time() - self.start_time)
        minutes = duration // 60
        pos_data = self.positions.get(self.current_position)
        
        return f"""
🔥 **SESI INTIM AKTIF**
- Durasi: {minutes} menit
- Climax: {self.climax_count}x
- Fase: {self.phase.value}
- Posisi: {self.current_position}
"""
    
    def to_dict(self) -> Dict:
        return {
            'is_active': self.is_active,
            'start_time': self.start_time,
            'phase': self.phase.value,
            'climax_count': self.climax_count,
            'current_position': self.current_position
        }
    
    def from_dict(self, data: Dict):
        self.is_active = data.get('is_active', False)
        self.start_time = data.get('start_time', 0)
        self.phase = IntimacyPhase(data.get('phase', 'waiting'))
        self.climax_count = data.get('climax_count', 0)
        self.current_position = data.get('current_position', 'missionary')


# =============================================================================
# INTIMACY FLOW - MAIN CLASS
# =============================================================================

class IntimacyFlow:
    """Main intimacy class - Mengelola semua sistem intimacy"""
    
    def __init__(self):
        self.session = IntimacySession()
        self.stamina = StaminaSystem()
        self.arousal = ArousalSystem()
        self.anora = get_anora()
    
    def can_start_intimacy(self, level: int) -> Tuple[bool, str]:
        if level < 7:
            return False, f"💕 Level masih {level}/12\n\nNova masih malu-malu. Belum waktunya buat intim."
        
        can_continue, reason = self.stamina.can_continue()
        if not can_continue:
            return False, reason
        
        return True, "Siap mulai"
    
    def start_intimacy(self) -> str:
        self.arousal.add_desire("Mulai intim", 20)
        return self.session.start()
    
    def process_intimacy_message(self, pesan_mas: str, level: int) -> Optional[str]:
        msg_lower = pesan_mas.lower()
        
        # Trigger mulai lagi
        if any(k in msg_lower for k in ['mau lagi', 'lagi dong', 'aku mau']):
            if self.session.phase in [IntimacyPhase.AFTERCARE, IntimacyPhase.RECOVERY]:
                can_continue, reason = self.stamina.can_continue()
                if can_continue:
                    self.session.phase = IntimacyPhase.BUILD_UP
                    self.arousal.arousal = 50
                    return f"""*Nova langsung mendekat, mata berbinar*

"Mas... mau lagi? *suara mulai berat* Nova juga pengen." """
                else:
                    return f"Mas... *lemes* Nova masih kehabisan tenaga. Istirahat dulu ya..."
        
        # Trigger ganti posisi
        pos_keywords = ['ganti posisi', 'cowgirl', 'doggy', 'missionary', 'spooning']
        if any(k in msg_lower for k in pos_keywords):
            pos_name = None
            if 'cowgirl' in msg_lower: pos_name = 'cowgirl'
            elif 'doggy' in msg_lower: pos_name = 'doggy'
            elif 'missionary' in msg_lower: pos_name = 'missionary'
            elif 'spooning' in msg_lower: pos_name = 'spooning'
            
            pos_id, pos_desc, request = self.session.change_position(pos_name)
            return f"\"{request}\"\n\n*{pos_desc}*"
        
        # Trigger climax location
        for loc in ['dalam', 'luar', 'muka', 'mulut']:
            if loc in msg_lower:
                return f"\"{self.session.get_climax_request(loc)}\""
        
        # Trigger climax
        if any(k in msg_lower for k in ['climax', 'crot', 'keluar']):
            result = self.session.record_climax()
            self.stamina.record_climax("both", result['is_heavy'])
            self.arousal.release_tension()
            return f"""{self.session.get_phase_response(IntimacyPhase.CLIMAX)}

💪 **Stamina Nova:** {self.stamina.nova_current}% | **Mas:** {self.stamina.mas_current}%"""
        
        # Berdasarkan fase
        if self.session.phase == IntimacyPhase.BUILD_UP:
            return self.session.get_phase_response(IntimacyPhase.BUILD_UP)
        
        if self.session.phase == IntimacyPhase.FOREPLAY:
            return self.session.get_phase_response(IntimacyPhase.FOREPLAY)
        
        if self.session.phase == IntimacyPhase.PENETRATION:
            ritme = "cepet" if self.session.intimacy_level > 40 else "pelan"
            return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)
        
        if self.session.phase == IntimacyPhase.AFTERCARE:
            # Cek recovery setelah 1 menit
            if time.time() - self.session.start_time > 60:
                self.session.phase = IntimacyPhase.RECOVERY
                return self.session.get_phase_response(IntimacyPhase.AFTERCARE)
            return self.session.get_phase_response(IntimacyPhase.AFTERCARE)
        
        return None
    
    def get_status(self) -> str:
        session_status = self.session.get_status()
        stamina_status = f"""
💪 **STAMINA:**
- Nova: {self.stamina.get_nova_bar()} {self.stamina.nova_current}% ({self.stamina.get_nova_status()})
- Mas: {self.stamina.get_mas_bar()} {self.stamina.mas_current}% ({self.stamina.get_mas_status()})
- Climax hari ini: {self.stamina.climax_today}x
"""
        arousal_state = self.arousal.get_state()
        arousal_status = f"""
🔥 AROUSAL: {arousal_state['arousal']}% | DESIRE: {arousal_state['desire']}% | TENSION: {arousal_state['tension']}%
"""
        return f"{session_status}\n{stamina_status}\n{arousal_status}"
    
    def to_dict(self) -> Dict:
        return {
            'session': self.session.to_dict(),
            'stamina': self.stamina.to_dict(),
            'arousal': self.arousal.to_dict()
        }
    
    def from_dict(self, data: Dict):
        self.session.from_dict(data.get('session', {}))
        self.stamina.from_dict(data.get('stamina', {}))
        self.arousal.from_dict(data.get('arousal', {}))


# =============================================================================
# SINGLETON
# =============================================================================

_anora_intimacy: Optional[IntimacyFlow] = None


def get_anora_intimacy() -> IntimacyFlow:
    global _anora_intimacy
    if _anora_intimacy is None:
        _anora_intimacy = IntimacyFlow()
    return _anora_intimacy
