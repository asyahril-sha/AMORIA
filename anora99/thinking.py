"""
ANORA 9.9 Thinking Engine - Cara Nova Berpikir.
Bukan copy dari AMORIA. Nova punya proses berpikir sendiri.
TERINTEGRASI DENGAN EMOTIONAL ENGINE 9.9
Target Realism 9.9 - Manusia.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .core import get_anora
from .emotional_engine import get_emotional_engine
from .relationship import get_relationship_manager
from .conflict_engine import get_conflict_engine

logger = logging.getLogger(__name__)


class AnoraThought:
    """
    Proses berpikir Nova. Bukan sekadar memilih respons.
    Nova mikir dulu: "Aku lagi ngerasa apa?", "Mas lagi ngomong apa?", "Aku mau jawab gimana?"
    TERINTEGRASI DENGAN EMOTIONAL ENGINE
    """
    
    def __init__(self):
        self.emotional = get_emotional_engine()
        self.relationship = get_relationship_manager()
        self.conflict = get_conflict_engine()
        self.last_thought = None
        self.thinking_history = []
    
    def process(self, pesan_mas: str, anora, context: Dict) -> Dict:
        """
        Proses berpikir Nova sebelum merespon.
        Seperti manusia: denger → mikir → ngerasa → putuskan → jawab.
        """
        
        # STEP 1: DENGER - Nova tangkap pesan Mas
        pesan_lower = pesan_mas.lower()
        
        # STEP 2: ANALISIS - Nova mikirin maksud Mas
        analysis = self._analyze_message(pesan_lower, anora)
        
        # STEP 3: RASA - Nova ngerasain sesuatu (dari emotional engine)
        feelings = self._feel(analysis, anora, context)
        
        # STEP 4: PUTUSKAN - Nova mutusin mau jawab gimana
        decision = self._decide(feelings, analysis, anora, context)
        
        # STEP 5: CATAT - Nova inget proses berpikirnya
        thought_record = {
            'timestamp': time.time(),
            'pesan_mas': pesan_mas[:100],
            'analysis': analysis,
            'feelings': feelings,
            'decision': decision,
            'emotional_style': self.emotional.get_current_style().value,
            'relationship_phase': self.relationship.phase.value,
            'conflict_active': self.conflict.is_in_conflict
        }
        self.thinking_history.append(thought_record)
        if len(self.thinking_history) > 50:
            self.thinking_history = self.thinking_history[-50:]
        
        self.last_thought = thought_record
        
        return {
            'analysis': analysis,
            'feelings': feelings,
            'decision': decision,
            'emotional_style': self.emotional.get_current_style().value,
            'relationship_phase': self.relationship.phase.value,
            'conflict_active': self.conflict.is_in_conflict
        }
    
    def _analyze_message(self, pesan: str, anora) -> Dict:
        """Nova analisis pesan Mas"""
        
        # Deteksi intent
        intent = 'ngobrol'
        if any(k in pesan for k in ['hai', 'halo', 'pagi', 'siang', 'sore', 'malam']):
            intent = 'salam'
        elif any(k in pesan for k in ['kabar', 'gimana', 'baik']):
            intent = 'kabar'
        elif any(k in pesan for k in ['lagi apa', 'ngapain']):
            intent = 'lagi_apa'
        elif any(k in pesan for k in ['kangen', 'rindu']):
            intent = 'kangen'
        elif any(k in pesan for k in ['sayang', 'cinta']):
            intent = 'sayang'
        elif any(k in pesan for k in ['capek', 'lelah', 'pegel']):
            intent = 'capek'
        elif any(k in pesan for k in ['seneng', 'senang', 'happy']):
            intent = 'seneng'
        
        # Deteksi mood Mas
        mas_mood = 'netral'
        if any(k in pesan for k in ['capek', 'lelah', 'pegel']):
            mas_mood = 'capek'
        elif any(k in pesan for k in ['seneng', 'senang', 'happy']):
            mas_mood = 'seneng'
        elif any(k in pesan for k in ['sedih', 'nangis']):
            mas_mood = 'sedih'
        
        # Apakah Mas lagi butuh sesuatu?
        butuh = None
        if any(k in pesan for k in ['cerita', 'curhat']):
            butuh = 'didengerin'
        elif any(k in pesan for k in ['bantu', 'tolong']):
            butuh = 'bantuan'
        elif any(k in pesan for k in ['makan', 'minum']):
            butuh = 'makanan'
        
        return {
            'intent': intent,
            'mas_mood': mas_mood,
            'butuh': butuh,
            'ada_flirt': any(k in pesan for k in ['cantik', 'ganteng', 'seksi', 'manis']),
            'ada_ungkapan_sayang': any(k in pesan for k in ['sayang', 'cinta']),
            'ada_panggilan': 'mas' in pesan or 'sayang' in pesan,
            'panjang_pesan': len(pesan)
        }
    
    def _feel(self, analysis: Dict, anora, context: Dict) -> Dict:
        """Nova ngerasain sesuatu berdasarkan analisis dan emotional engine"""
        
        # Ambil dari emotional engine
        feelings = {
            'malu': 0,
            'seneng': self.emotional.mood,
            'kangen': self.emotional.rindu,
            'deg_degan': self.emotional.tension,
            'pengen': self.emotional.desire,
            'panas': self.emotional.arousal,
            'sayang': self.emotional.sayang,
            'cemburu': self.emotional.cemburu,
            'kecewa': self.emotional.kecewa
        }
        
        # Kalo Mas salam, Nova seneng
        if analysis['intent'] == 'salam':
            feelings['seneng'] += 20
            if self.relationship.level < 7:
                feelings['malu'] += 15
        
        # Kalo Mas tanya kabar, Nova seneng
        if analysis['intent'] == 'kabar':
            feelings['seneng'] += 15
        
        # Kalo Mas bilang kangen, Nova seneng + kangen + deg-degan
        if analysis['intent'] == 'kangen':
            feelings['seneng'] += 25
            feelings['kangen'] = min(100, feelings['kangen'] + 20)
            feelings['deg_degan'] += 15
            feelings['pengen'] += 15
        
        # Kalo Mas bilang sayang, Nova seneng banget + pengen
        if analysis['intent'] == 'sayang':
            feelings['seneng'] += 35
            feelings['pengen'] += 25
            feelings['sayang'] = min(100, feelings['sayang'] + 5)
        
        # Kalo Mas puji (cantik/ganteng), Nova malu + seneng
        if analysis['ada_flirt']:
            feelings['malu'] += 30
            feelings['seneng'] += 20
            feelings['pengen'] += 10
        
        # Kalo Mas lagi capek, Nova sayang + pengen perhatiin
        if analysis['mas_mood'] == 'capek':
            feelings['sayang'] = min(100, feelings['sayang'] + 10)
            feelings['pengen'] += 15
        
        # Kalo Mas butuh didengerin, Nova sayang
        if analysis['butuh'] == 'didengerin':
            feelings['sayang'] = min(100, feelings['sayang'] + 10)
        
        # Kalo lagi roleplay dan Mas masuk/datang
        if context.get('mode') == 'roleplay' and analysis['intent'] == 'salam':
            feelings['malu'] += 40
            feelings['seneng'] += 30
            feelings['deg_degan'] += 25
        
        # Batasin nilai
        for key in feelings:
            if isinstance(feelings[key], (int, float)):
                feelings[key] = max(0, min(100, feelings[key]))
        
        return feelings
    
    def _decide(self, feelings: Dict, analysis: Dict, anora, context: Dict) -> Dict:
        """Nova mutusin mau ngomong gimana"""
        
        # Tentukan tone berdasarkan perasaan (dari emotional engine)
        style = self.emotional.get_current_style()
        
        if style.value == "cold":
            tone = 'cold'
            intensity = 'tinggi'
        elif style.value == "clingy":
            tone = 'clingy'
            intensity = 'tinggi'
        elif style.value == "flirty":
            tone = 'flirt'
            intensity = 'sedang'
        elif style.value == "warm":
            tone = 'warm'
            intensity = 'sedang'
        else:
            tone = 'netral'
            intensity = 'rendah'
        
        # Override berdasarkan conflict
        if self.conflict.is_in_conflict:
            if self.conflict.cemburu > 50:
                tone = 'cemburu'
            elif self.conflict.kecewa > 40:
                tone = 'kecewa'
            else:
                tone = 'cold'
        
        # Tentukan panjang respons berdasarkan level dan style
        level = self.relationship.level
        if level <= 3:
            panjang = 'pendek'
            max_kalimat = 3
        elif level <= 6:
            panjang = 'sedang'
            max_kalimat = 4
        elif level <= 10:
            panjang = 'panjang'
            max_kalimat = 6
        else:
            panjang = 'sangat_panjang'
            max_kalimat = 10
        
        # Tentukan gesture berdasarkan perasaan
        gesture = self._choose_gesture(feelings, tone)
        
        return {
            'tone': tone,
            'intensity': intensity,
            'panjang': panjang,
            'max_kalimat': max_kalimat,
            'gesture': gesture,
            'boleh_vulgar': self.relationship.level >= 11 and feelings['panas'] > 70,
            'emotional_style': style.value
        }
    
    def _choose_gesture(self, feelings: Dict, tone: str) -> str:
        """Pilih gesture berdasarkan perasaan"""
        
        if tone == 'cold' or tone == 'cemburu' or tone == 'kecewa':
            gestures = [
                "*diam, gak liat Mas*",
                "*jawab pendek, gak antusias*",
                "*jauh sedikit dari Mas*"
            ]
        elif tone == 'clingy':
            gestures = [
                "*muter-muter rambut, liat Mas*",
                "*duduk deket, pegang tangan Mas*",
                "*nempel ke Mas, gak mau lepas*"
            ]
        elif tone == 'warm':
            gestures = [
                "*tersenyum manis, mata berbinar*",
                "*duduk manis, tangan di pangkuan*",
                "*elus punggung tangan Mas pelan*"
            ]
        elif tone == 'flirt':
            gestures = [
                "*mendekat, napas mulai berat*",
                "*gigit bibir, mata sayu*",
                "*bisik di telinga Mas*"
            ]
        else:
            gestures = [
                "*tersenyum kecil*",
                "*menatap Mas*",
                "*duduk santai*"
            ]
        
        return random.choice(gestures)
    
    def get_thinking_summary(self) -> str:
        """Dapatkan ringkasan proses berpikir Nova (buat debugging)"""
        if not self.last_thought:
            return "Nova belum mikir apa-apa."
        
        return f"""
💭 **PROSES BERPIKIR NOVA 9.9:**
• Analisis: {self.last_thought['analysis']}
• Perasaan: sayang={self.last_thought['feelings']['sayang']:.0f}%, seneng={self.last_thought['feelings']['seneng']:.0f}%, kangen={self.last_thought['feelings']['kangen']:.0f}%
• Keputusan: tone={self.last_thought['decision']['tone']}, panjang={self.last_thought['decision']['panjang']}
• Emotional Style: {self.last_thought['emotional_style']}
• Relationship Phase: {self.last_thought['relationship_phase']}
• Conflict Active: {self.last_thought['conflict_active']}
"""


# =============================================================================
# SINGLETON
# =============================================================================

_anora_thought = None


def get_anora_thought() -> AnoraThought:
    global _anora_thought
    if _anora_thought is None:
        _anora_thought = AnoraThought()
    return _anora_thought


anora_thought = get_anora_thought()
