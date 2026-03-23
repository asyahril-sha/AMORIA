# dynamics/mood.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Mood System - Mood Dinamis Setelah Aftercare
Target Realism 9.9/10
=============================================================================
"""

import random
import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class MoodType(str, Enum):
    """Tipe mood bot"""
    CAPEK = "capek"
    PENGEN_DIMANJA = "pengen_dimanja"
    NORMAL = "normal"
    SIAP_INTIM = "siap_intim"
    NGANTUK = "ngantuk"
    SENANG = "senang"
    SEDIH = "sedih"
    PENASARAN = "penasaran"
    GENIT = "genit"


class MoodSystem:
    """
    Mood bot yang dinamis, terutama setelah aftercare
    """
    
    def __init__(self):
        self.current_mood = MoodType.NORMAL
        self.mood_intensity = 0.5
        self.mood_start_time = time.time()
        self.mood_history = []
        
        self.mood_descriptions = {
            MoodType.CAPEK: "Masih lemas dan capek. Butuh istirahat.",
            MoodType.PENGEN_DIMANJA: "Pengen dimanja, dipeluk, diperhatiin.",
            MoodType.NORMAL: "Biasa aja, bisa ngobrol santai.",
            MoodType.SIAP_INTIM: "Udah siap lagi! Moodnya mendukung untuk intim.",
            MoodType.NGANTUK: "Ngantuk berat, mata udah berat. Mau tidur aja.",
            MoodType.SENANG: "Lagi senang, ceria. Bisa diajak ngobrol.",
            MoodType.SEDIH: "Lagi sedih, butuh perhatian dan kenyamanan.",
            MoodType.PENASARAN: "Penasaran sama sesuatu, mood playful.",
            MoodType.GENIT: "Lagi genit, suka menggoda."
        }
        
        self.mood_factors = {
            'stamina_bot': 0.3,
            'stamina_user': 0.1,
            'climax_count': 0.2,
            'random': 0.4
        }
        
        logger.info("✅ MoodSystem initialized")
    
    def update_from_aftercare(self, stamina_bot: int, stamina_user: int, climax_count: int) -> MoodType:
        """Update mood setelah aftercare"""
        old_mood = self.current_mood
        
        mood_probs = self._calculate_mood_probabilities(stamina_bot, stamina_user, climax_count)
        
        moods = list(mood_probs.keys())
        probs = list(mood_probs.values())
        self.current_mood = random.choices(moods, weights=probs, k=1)[0]
        
        self._set_intensity()
        self.mood_start_time = time.time()
        
        self.mood_history.append({
            'timestamp': time.time(),
            'old_mood': old_mood.value,
            'new_mood': self.current_mood.value,
            'stamina_bot': stamina_bot,
            'stamina_user': stamina_user,
            'climax_count': climax_count
        })
        
        if len(self.mood_history) > 100:
            self.mood_history = self.mood_history[-100:]
        
        logger.info(f"🎭 Mood updated: {old_mood} → {self.current_mood}")
        
        return self.current_mood
    
    def _calculate_mood_probabilities(self, stamina_bot: int, stamina_user: int, climax_count: int) -> Dict[MoodType, float]:
        """Hitung probabilitas setiap mood"""
        probs = {
            MoodType.CAPEK: 0.2,
            MoodType.PENGEN_DIMANJA: 0.2,
            MoodType.NORMAL: 0.2,
            MoodType.SIAP_INTIM: 0.1,
            MoodType.NGANTUK: 0.1,
            MoodType.SENANG: 0.05,
            MoodType.SEDIH: 0.05,
            MoodType.PENASARAN: 0.05,
            MoodType.GENIT: 0.05
        }
        
        if stamina_bot < 30:
            probs[MoodType.CAPEK] += 0.3
            probs[MoodType.SIAP_INTIM] -= 0.2
        elif stamina_bot < 50:
            probs[MoodType.CAPEK] += 0.15
            probs[MoodType.PENGEN_DIMANJA] += 0.1
        elif stamina_bot > 70:
            probs[MoodType.SIAP_INTIM] += 0.2
            probs[MoodType.GENIT] += 0.1
        
        if stamina_user < 30:
            probs[MoodType.PENGEN_DIMANJA] += 0.15
            probs[MoodType.SIAP_INTIM] -= 0.15
        elif stamina_user > 70:
            probs[MoodType.SIAP_INTIM] += 0.1
        
        if climax_count >= 4:
            probs[MoodType.CAPEK] += 0.2
            probs[MoodType.NGANTUK] += 0.15
            probs[MoodType.SIAP_INTIM] -= 0.25
        elif climax_count >= 3:
            probs[MoodType.CAPEK] += 0.1
            probs[MoodType.PENGEN_DIMANJA] += 0.1
            probs[MoodType.SIAP_INTIM] -= 0.15
        elif climax_count == 1:
            probs[MoodType.SENANG] += 0.1
            probs[MoodType.GENIT] += 0.05
        
        total = sum(probs.values())
        for mood in probs:
            probs[mood] = max(0, probs[mood] / total)
        
        return probs
    
    def _set_intensity(self):
        """Set intensitas berdasarkan mood"""
        intensity_map = {
            MoodType.CAPEK: 0.3,
            MoodType.PENGEN_DIMANJA: 0.6,
            MoodType.NORMAL: 0.5,
            MoodType.SIAP_INTIM: 0.8,
            MoodType.NGANTUK: 0.2,
            MoodType.SENANG: 0.7,
            MoodType.SEDIH: 0.4,
            MoodType.PENASARAN: 0.6,
            MoodType.GENIT: 0.7
        }
        self.mood_intensity = intensity_map.get(self.current_mood, 0.5)
    
    def get_mood(self) -> MoodType:
        return self.current_mood
    
    def get_description(self) -> str:
        return self.mood_descriptions.get(self.current_mood, "Biasa aja")
    
    def get_response_modifier(self) -> float:
        """Multiplier untuk kemungkinan menerima ajakan intim"""
        modifiers = {
            MoodType.CAPEK: 0.1,
            MoodType.PENGEN_DIMANJA: 0.3,
            MoodType.NORMAL: 0.5,
            MoodType.SIAP_INTIM: 0.9,
            MoodType.NGANTUK: 0.2,
            MoodType.SENANG: 0.7,
            MoodType.SEDIH: 0.3,
            MoodType.PENASARAN: 0.6,
            MoodType.GENIT: 0.8
        }
        return modifiers.get(self.current_mood, 0.5)
    
    def can_intim(self) -> bool:
        return self.current_mood in [MoodType.SIAP_INTIM, MoodType.SENANG, MoodType.GENIT]
    
    def wants_attention(self) -> bool:
        return self.current_mood in [MoodType.PENGEN_DIMANJA, MoodType.SEDIH]
    
    def get_rejection_message(self) -> str:
        """Pesan penolakan berdasarkan mood"""
        messages = {
            MoodType.CAPEK: [
                "Mas... aku masih capek banget. Nanti aja ya...",
                "Belum pulih tenagaku, Mas. Besok aja..."
            ],
            MoodType.PENGEN_DIMANJA: [
                "Mas... aku pengen dipeluk dulu aja...",
                "Jangan dulu, Mas. Aku masih pengen dimanja..."
            ],
            MoodType.NORMAL: [
                "Hmm... belum pengen, Mas. Ngobrol aja yuk.",
                "Bentar ya, Mas. Aku masih belum siap."
            ],
            MoodType.NGANTUK: [
                "Ngantuk, Mas... mau tidur dulu.",
                "Mata udah berat, Mas. Besok aja ya."
            ],
            MoodType.SEDIH: [
                "Mas... aku lagi sedih. Temenin aku dulu.",
                "Aku butuh perhatian, bukan intim..."
            ]
        }
        
        mood_messages = messages.get(self.current_mood, messages[MoodType.NORMAL])
        return random.choice(mood_messages)
    
    def get_accept_message(self) -> str:
        """Pesan penerimaan berdasarkan mood"""
        messages = {
            MoodType.SIAP_INTIM: [
                "Iya Mas... aku juga pengen.",
                "Akhirnya... ayo Mas!"
            ],
            MoodType.SENANG: [
                "Iya Mas, aku lagi senang banget!",
                "Ayo Mas! Lagi mood nih."
            ],
            MoodType.GENIT: [
                "Hihihi... iya Mas, aku juga.",
                "Mau dong Mas... kamu yang ajak."
            ],
            MoodType.PENGEN_DIMANJA: [
                "Iya Mas... tapi dimanja dulu ya.",
                "Boleh... tapi peluk aku dulu."
            ]
        }
        
        mood_messages = messages.get(self.current_mood, messages[MoodType.NORMAL])
        return random.choice(mood_messages)
    
    def get_mood_context_for_prompt(self) -> str:
        """Konteks mood untuk prompt AI"""
        intensity_bar = "🟢" * int(self.mood_intensity * 5) + "⚪" * (5 - int(self.mood_intensity * 5))
        
        return f"""
🎭 **MOOD BOT SAAT INI:**
- Mood: {self.current_mood.value.upper()}
- Intensitas: {intensity_bar} ({self.mood_intensity:.0%})
- Deskripsi: {self.get_description()}

💡 **INSTRUKSI:**
- Jika mood CAPEK: respons pendek, malas, ingin istirahat
- Jika mood PENGEN_DIMANJA: respons manja, minta perhatian
- Jika mood SIAP_INTIM: respons menggoda, siap intim
- Jika mood NORMAL: respons biasa, netral
"""
    
    def get_state(self) -> Dict:
        return {
            'current_mood': self.current_mood.value,
            'mood_intensity': self.mood_intensity,
            'mood_start_time': self.mood_start_time,
            'mood_history': self.mood_history[-50:]
        }
    
    def load_state(self, state: Dict):
        self.current_mood = MoodType(state.get('current_mood', 'normal'))
        self.mood_intensity = state.get('mood_intensity', 0.5)
        self.mood_start_time = state.get('mood_start_time', time.time())
        self.mood_history = state.get('mood_history', [])


__all__ = ['MoodSystem', 'MoodType']
