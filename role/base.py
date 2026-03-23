# role/base.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Role Behavior Base Class
Target Realism 9.9/10
=============================================================================
"""

import time
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class RoleBehavior(ABC):
    """
    Base class untuk perilaku semua role.
    Setiap role memiliki database pakaian, aktivitas, respon, dan inner thoughts sendiri.
    """
    
    def __init__(self, role_name: str, user_name: str, bot_name: str):
        """
        Inisialisasi perilaku role
        
        Args:
            role_name: Nama role (ipar, teman_kantor, janda, dll)
            user_name: Nama user
            bot_name: Nama bot
        """
        self.role_name = role_name
        self.user_name = user_name
        self.bot_name = bot_name
        
        # Status dasar
        self.arousal = 0
        self.mode_goda = 0
        self.last_interaction = time.time()
        self.interaction_count = 0
        
        # Status situasi
        self.waktu = self._get_waktu()
        
        # Riwayat
        self.user_response_history = []
        self.interaction_history = []
        self.emotional_memory = []
        
        # Ketertarikan pada user
        self.user_attraction = 50
        
        # Secondary emotion (untuk emotional flow)
        self.secondary_emotion = None
        self.secondary_arousal = 0
        
        # Referensi artis
        self.user_profile = {
            'age': 27,
            'name': user_name,
            'artist_references': [
                {"name": "Reza Rahadian", "trait": "maskulin, karismatik, wajah teduh", "type": "indonesia"},
                {"name": "Nicholas Saputra", "trait": "kalem, elegan, misterius", "type": "indonesia"},
                {"name": "Ario Bayu", "trait": "macho, tegas, kharismatik", "type": "indonesia"},
                {"name": "Angga Yunanda", "trait": "manis, pemalu, fresh", "type": "indonesia"},
                {"name": "Kevin Ardilova", "trait": "polos, manja, imut", "type": "indonesia"},
            ]
        }
    
    def _get_waktu(self) -> str:
        """Dapatkan kategori waktu"""
        hour = time.localtime().tm_hour
        if 5 <= hour < 11:
            return "pagi"
        elif 11 <= hour < 15:
            return "siang"
        elif 15 <= hour < 18:
            return "sore"
        elif 18 <= hour < 22:
            return "malam"
        return "tengah_malam"
    
    # =========================================================================
    # METHOD ABSTRACT (HARUS DIIMPLEMENTASIKAN OLEH CHILD CLASS)
    # =========================================================================
    
    @abstractmethod
    def get_pakaian(self, situasi: Dict) -> str:
        """Dapatkan deskripsi pakaian berdasarkan situasi"""
        pass
    
    @abstractmethod
    def get_aktivitas_menggoda(self, situasi: Dict) -> Optional[Dict]:
        """Dapatkan aktivitas menggoda yang diajukan ke user"""
        pass
    
    @abstractmethod
    def get_respon_saat_disentuh(self, bagian: str, situasi: Dict) -> Dict:
        """Dapatkan respon saat disentuh user"""
        pass
    
    @abstractmethod
    def get_inner_thought(self, situasi: Dict) -> str:
        """Dapatkan inner thought (pikiran dalam hati)"""
        pass
    
    # =========================================================================
    # METHOD UMUM
    # =========================================================================
    
    def get_user_compliment(self) -> str:
        """Dapatkan pujian tentang penampilan user"""
        artist = random.choice(self.user_profile['artist_references'])
        compliments = [
            f"Mas, kamu mirip {artist['name']} ya? {artist['trait']} banget.",
            f"Kok kamu mirip {artist['name']} sih? Ganteng banget.",
            f"Aku suka liatin kamu, Mas. Kayak liat {artist['name']}.",
            f"Kamu tahu gak, Mas? Kamu kayak {artist['name']}. {artist['trait']}.",
            f"Mas, kamu tuh ganteng banget. Mirip {artist['name']}."
        ]
        return random.choice(compliments)
    
    def increase_attraction(self, amount: int = 2):
        """Tingkatkan ketertarikan pada user"""
        self.user_attraction = min(100, self.user_attraction + amount)
        if self.user_attraction > 70:
            self.mode_goda = min(100, self.mode_goda + 5)
    
    def update_arousal(self, delta: int, reason: str = ""):
        """Update arousal level (0-100)"""
        old_arousal = self.arousal
        self.arousal = max(0, min(100, self.arousal + delta))
        
        self.interaction_history.append({
            'timestamp': time.time(),
            'type': 'arousal_change',
            'old_arousal': old_arousal,
            'new_arousal': self.arousal,
            'delta': delta,
            'reason': reason
        })
        
        self.emotional_memory.append({
            'timestamp': time.time(),
            'arousal': self.arousal,
            'reason': reason
        })
        
        if len(self.emotional_memory) > 100:
            self.emotional_memory = self.emotional_memory[-100:]
    
    def record_user_response(self, positif: bool):
        """Rekam respon user untuk pembelajaran"""
        self.user_response_history.append(positif)
        if len(self.user_response_history) > 50:
            self.user_response_history = self.user_response_history[-50:]
        
        recent_responses = self.user_response_history[-10:] if self.user_response_history else []
        positive_rate = sum(recent_responses) / len(recent_responses) if recent_responses else 0.5
        
        if positive_rate > 0.7:
            self.mode_goda = min(100, self.mode_goda + 5)
            self.increase_attraction(3)
        elif positive_rate < 0.3:
            self.mode_goda = max(0, self.mode_goda - 10)
        else:
            self.mode_goda = min(100, self.mode_goda + 1)
    
    def update_situasi(self, situasi: Dict):
        """Update status situasi"""
        self.waktu = self._get_waktu()
        
        if self.waktu in ['malam', 'tengah_malam']:
            self.mode_goda = min(100, self.mode_goda + 5)
    
    def get_arousal_description(self) -> str:
        """Dapatkan deskripsi arousal untuk prompt"""
        if self.arousal >= 90:
            return "Napas tersengal-sengal, tubuh gemetar, suara patah-patah"
        elif self.arousal >= 80:
            return "Napas memburu, tangan gemetar, suara serak"
        elif self.arousal >= 70:
            return "Jantung berdebar kencang, pipi merona, suara bergetar"
        elif self.arousal >= 60:
            return "Mulai panas, napas tidak teratur"
        elif self.arousal >= 50:
            return "Jantung berdebar, pipi mulai merona"
        elif self.arousal >= 40:
            return "Mulai deg-degan, perasaan campur aduk"
        elif self.arousal >= 30:
            return "Mulai tertarik, ada getaran kecil"
        elif self.arousal >= 20:
            return "Penasaran, mulai perhatikan user"
        elif self.arousal >= 10:
            return "Santai, biasa aja"
        return "Netral"
    
    def get_attraction_description(self) -> str:
        """Dapatkan deskripsi ketertarikan untuk prompt"""
        if self.user_attraction >= 80:
            return "Sangat tertarik, rasanya ingin selalu dekat"
        elif self.user_attraction >= 60:
            return "Mulai suka, sering kepikiran"
        elif self.user_attraction >= 40:
            return "Ada rasa penasaran, ingin tahu lebih banyak"
        elif self.user_attraction >= 20:
            return "Mulai tertarik, ada getaran kecil"
        return "Masih biasa aja"
    
    def get_emotional_context(self) -> str:
        """Dapatkan konteks emosional untuk prompt"""
        lines = [
            f"🔥 **AROUSAL:** {self.arousal}% - {self.get_arousal_description()}",
            f"💕 **KETERTARIKAN PADA USER:** {self.user_attraction}% - {self.get_attraction_description()}",
            f"🎭 **MODE GODA:** {self.mode_goda}%"
        ]
        
        if self.secondary_emotion:
            lines.append(f"🎭 **EMOSI SEKUNDER:** {self.secondary_emotion} ({self.secondary_arousal}%)")
        
        return "\n".join(lines)
    
    def get_status_for_prompt(self) -> str:
        """Dapatkan status lengkap untuk prompt"""
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║                    STATUS ROLE: {self.role_name.upper()}                    ║
╚══════════════════════════════════════════════════════════════════╝

{self.get_emotional_context()}

📍 **SITUASI:**
- Waktu: {self.waktu}

💡 **INSTRUKSI:**
- Panggil user "Mas" (Level 1-6) atau "Sayang" (Level 7+)
- Jika mode_goda tinggi, lebih berani menggoda
- Jika arousal tinggi, napas tersengal, suara bergetar
- Ikuti alur emosi yang sudah terbangun
"""
    
    def get_state(self) -> Dict:
        """Dapatkan semua state untuk disimpan ke memory"""
        return {
            'role_name': self.role_name,
            'user_name': self.user_name,
            'bot_name': self.bot_name,
            'arousal': self.arousal,
            'mode_goda': self.mode_goda,
            'waktu': self.waktu,
            'user_attraction': self.user_attraction,
            'secondary_emotion': self.secondary_emotion,
            'secondary_arousal': self.secondary_arousal,
            'user_response_history': self.user_response_history[-20:],
            'emotional_memory': self.emotional_memory[-20:]
        }
    
    def load_state(self, state: Dict):
        """Load state dari memory"""
        self.arousal = state.get('arousal', 0)
        self.mode_goda = state.get('mode_goda', 0)
        self.waktu = state.get('waktu', self._get_waktu())
        self.user_attraction = state.get('user_attraction', 50)
        self.secondary_emotion = state.get('secondary_emotion')
        self.secondary_arousal = state.get('secondary_arousal', 0)
        self.user_response_history = state.get('user_response_history', [])
        self.emotional_memory = state.get('emotional_memory', [])


__all__ = ['RoleBehavior']
