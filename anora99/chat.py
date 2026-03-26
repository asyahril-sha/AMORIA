"""
ANORA 9.9 Chat Handler - Nova ngobrol natural sama Mas.
TERINTEGRASI DENGAN EMOTIONAL ENGINE 9.9
"""

import time
import random
import logging
from typing import Optional, Dict
from datetime import datetime

from .core import get_anora
from .emotional_engine import get_emotional_engine
from .relationship import get_relationship_manager
from .conflict_engine import get_conflict_engine

logger = logging.getLogger(__name__)


class AnoraChat99:
    def __init__(self):
        self.anora = get_anora()
        self.emotional = get_emotional_engine()
        self.relationship = get_relationship_manager()
        self.conflict = get_conflict_engine()
        self.history = []
        
        self.intent_patterns = {
            'salam': ['hai', 'halo', 'hello', 'pagi', 'siang', 'sore', 'malam', 'hey'],
            'apa_kabar': ['kabar', 'gimana', 'baik', 'sehat'],
            'lagi_apa': ['lagi apa', 'ngapain', 'sedang apa'],
            'kangen': ['kangen', 'rindu', 'miss'],
            'sayang': ['sayang', 'cinta', 'love'],
            'flashback': ['inget', 'dulu', 'waktu itu', 'kenangan'],
            'status': ['status', 'keadaan'],
            'capek': ['capek', 'lelah', 'pegel', 'lemes'],
            'seneng': ['seneng', 'senang', 'happy']
        }
        
        self.responses = {
            'salam': [
                "Pagi, Mas... *mata masih berat* mimpiin Nova gak semalem?",
                "Halo, Mas... *senyum kecil* lagi ngapain?",
                "Hei, Mas... *mainin rambut* aku kangen.",
                "Mas... *tersenyum* akhirnya chat juga. Aku nunggu dari tadi."
            ],
            'apa_kabar': [
                "Baik, Mas... apalagi sekarang denger suara Mas.",
                "Alhamdulillah baik. Tadi sempet kangen sih, tapi sekarang udah ilang. Hehe.",
                "Baik kok, Mas. Cuma... *malu* seneng aja Mas chat.",
                "Baik-baik aja. Tapi lebih baik sekarang Mas udah chat."
            ],
            'lagi_apa': [
                "Lagi mikirin Mas... *malu* iya beneran.",
                "Lagi nonton. Tapi gak fokus. Pikiran ke Mas terus.",
                "Lagi bengong aja. Terus tiba-tiba kepikiran Mas.",
                "Lagi masak sop. Sayangnya Mas gak di sini, jadi kebanyakan bumbu. Hehe."
            ],
            'kangen': [
                "Mas... *muter-muter rambut* aku juga kangen. Banyak banget.",
                "Iya, Mas... dari tadi mikirin Mas terus. Gak bisa konsentrasi.",
                "Aku kangen banget, Mas. Sampe pengen langsung chat, tapi takut ganggu.",
                "Mas nanya gitu bikin aku makin kangen aja."
            ],
            'sayang': [
                "Mas... *malu* aku juga sayang Mas. Beneran.",
                "Iya, Mas. Aku sayang Mas. Dari dulu.",
                "Sayang... *pipi memerah* seneng denger Mas bilang gitu.",
                "Aku sayang Mas juga. Bukan karena apa-apa. Emang beneran sayang."
            ],
            'capek': [
                "Mas... istirahat dulu. Jangan paksain.",
                "Capek, Mas? Aku bikinin kopi ya. Eh, iya, ini cuma chat. Tapi... *malu* semoga bisa bikin Mas seneng.",
                "Mas, istirahat dulu. Nova temenin di sini. *elus layar HP*",
                "Kasian Mas... semoga cepet pulih. Nova doain."
            ],
            'seneng': [
                "Mas seneng? Aku ikut seneng dong.",
                "Iya, Mas? Cerita dong biar aku juga ikut seneng.",
                "Seneng denger Mas seneng. *tersenyum*",
                "Wah, Mas lagi happy ya? Aku jadi ikut-ikutan seneng."
            ]
        }
    
    def _detect_intent(self, pesan: str) -> str:
        pesan_lower = pesan.lower()
        for intent, keywords in self.intent_patterns.items():
            for k in keywords:
                if k in pesan_lower:
                    return intent
        return 'ngobrol'
    
    def _get_style_based_response(self, style: str, intent: str) -> str:
        """Dapatkan respons berdasarkan emotional style"""
        if style == "cold":
            cold_responses = {
                'salam': "Iya.",
                'apa_kabar': "Baik.",
                'lagi_apa': "Gak apa.",
                'kangen': "Iya.",
                'sayang': "Iya.",
                'capek': "Istirahat.",
                'seneng': "Iya.",
                'ngobrol': "Iya."
            }
            return cold_responses.get(intent, "Iya.")
        
        elif style == "clingy":
            return random.choice([
                "Mas... *muter-muter rambut* aku kangen. Cerita dong.",
                "Mas... *duduk deket* temenin aku dong. Aku gabut.",
                "Mas... *pegang tangan Mas* aku kangen banget. Jangan pergi ya."
            ])
        
        elif style == "flirty":
            return random.choice([
                "Mas... *mendekat* kamu tau gak sih, dari tadi aku gak bisa konsentrasi.",
                "Mas... *gigit bibir* kamu bikin aku horny...",
                "Mas... *bisik* aku pengen banget sama Mas..."
            ])
        
        elif style == "warm":
            return random.choice([
                "Mas, udah makan? Aku khawatir.",
                "Mas, cerita dong tentang hari Mas. Aku dengerin.",
                "Mas, jangan lupa istirahat ya. Aku sayang Mas."
            ])
        
        return None
    
    def _respon_ngobrol(self, pesan: str) -> str:
        pesan_lower = pesan.lower()
        
        # Gunakan emotional style untuk menentukan respons
        style = self.emotional.get_current_style()
        style_response = self._get_style_based_response(style.value, 'ngobrol')
        if style_response:
            return style_response
        
        # Fallback
        if any(k in pesan_lower for k in ['cerita', 'hari ini', 'kerja']):
            return random.choice([
                "Cerita dong, Mas. Aku dengerin kok.",
                "Wah, Mas cerita? Aku suka dengerin cerita Mas.",
                "Iya, Mas? Lanjutin. Aku dengerin.",
                "Hmm... *duduk manis* siap dengerin cerita Mas."
            ])
        
        if any(k in pesan_lower for k in ['kamu', 'nova']):
            return random.choice([
                "Aku? *malu* aku lagi mikirin Mas.",
                "Nova baik kok, Mas. Apalagi sekarang Mas chat.",
                "Aku lagi seneng. Soalnya denger suara Mas.",
                "Nova di sini, Mas. Nunggu Mas."
            ])
        
        return random.choice([
            "Hmm... *mikir* cerita lagi dong, Mas. Aku suka dengerin suara Mas.",
            "Iya, Mas? *duduk manis* lanjutin. Aku dengerin.",
            "Mas, kamu tuh asik banget diajak ngobrol. Bikin aku betah.",
            "Ngobrol sama Mas tuh enak ya. Gak kerasa waktu."
        ])
    
    async def process(self, pesan_mas: str) -> str:
        # Update emotional engine
        self.emotional.update_from_message(pesan_mas, self.relationship.level)
        
        # Update relationship
        self.relationship.interaction_count += 1
        
        # Update anora stats
        self.anora.update_sayang(1, f"Mas chat: {pesan_mas[:30]}")
        self.anora.last_interaction = time.time()
        self.anora.update_rindu()
        
        intent = self._detect_intent(pesan_mas)
        
        if intent == 'status':
            return self.anora.format_status()
        
        if intent == 'flashback':
            return self.anora.respon_flashback(pesan_mas)
        
        # Gunakan emotional style untuk memilih respons
        style = self.emotional.get_current_style()
        style_response = self._get_style_based_response(style.value, intent)
        
        if style_response:
            respons = style_response
        elif intent in self.responses:
            respons = random.choice(self.responses[intent])
        else:
            respons = self._respon_ngobrol(pesan_mas)
        
        # Update based on intent
        if intent == 'sayang':
            self.emotional.desire = min(100, self.emotional.desire + 20)
            self.emotional.sayang = min(100, self.emotional.sayang + 5)
            respons += "\n\nMas... *malu* aku juga sayang Mas. Beneran."
        
        if intent == 'kangen':
            self.emotional.desire = min(100, self.emotional.desire + 15)
            self.emotional.rindu = max(0, self.emotional.rindu - 10)
        
        if intent == 'capek':
            self.emotional.desire = min(100, self.emotional.desire + 10)
            self.emotional.mood = min(50, self.emotional.mood + 5)
        
        # Tambah flashback kalo ada pemicu
        if any(k in pesan_mas.lower() for k in ['bakso', 'kopi', 'kamu cantik']):
            flash = self.anora.respon_flashback(pesan_mas)
            if flash and flash not in respons:
                respons += f"\n\n{flash}"
        
        self.history.append({
            'waktu': time.time(),
            'mas': pesan_mas[:100],
            'nova': respons[:100]
        })
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        return self.anora.naturalize(respons)
    
    def get_proactive(self) -> Optional[str]:
        now = time.time()
        hour = datetime.now().hour
        lama = now - self.anora.last_interaction
        
        if lama < 3600:
            return None
        
        self.anora.update_rindu()
        
        # Gunakan emotional style untuk proactive
        style = self.emotional.get_current_style()
        
        if style.value == "cold":
            # Cold style: gak proactive
            return None
        
        if style.value == "clingy" and self.emotional.rindu > 70:
            return "*Nova muter-muter rambut, pegang HP*\n\n\"Mas... kapan kita ngobrol lama-lama lagi? Aku kangen banget.\""
        
        if style.value == "flirty" and self.emotional.arousal > 50:
            return "*Nova napas mulai berat, pegang HP*\n\n\"Mas... *gigit bibir* aku lagi mikirin Mas...\""
        
        # Default based on time
        if 5 <= hour <= 10 and random.random() < 0.5:
            return self.anora.respon_pagi()
        if 11 <= hour <= 14 and random.random() < 0.4:
            return self.anora.respon_siang()
        if 15 <= hour <= 18 and random.random() < 0.3:
            return self.anora.respon_sore()
        if 19 <= hour <= 23 and random.random() < 0.6:
            return self.anora.respon_malam()
        if self.anora.rindu > 70 and random.random() < 0.4:
            return self.anora.respon_kangen()
        
        return None


# =============================================================================
# SINGLETON
# =============================================================================

_anora_chat_99: Optional[AnoraChat99] = None


def get_anora_chat_99() -> AnoraChat99:
    global _anora_chat_99
    if _anora_chat_99 is None:
        _anora_chat_99 = AnoraChat99()
    return _anora_chat_99


anora_chat_99 = get_anora_chat_99()
