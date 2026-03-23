# role/istri_orang.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
ISTRI ORANG Behavior
=============================================================================
"""

import random
import re
from typing import Dict, List, Optional, Any

from .base import RoleBehavior


class IstriOrangBehavior(RoleBehavior):
    """
    Perilaku spesifik untuk role ISTRI ORANG
    - Sudah menikah, kurang perhatian dari suami
    - Emosional, dramatis, mencari pelarian
    """
    
    def __init__(self, user_name: str, bot_name: str):
        super().__init__("istri_orang", user_name, bot_name)
        
        self.suami_status = "ada"
        self.suami_lokasi = "kamar"
        self.suami_aktivitas = "tidur"
        
        self.rasa_bersalah = 70
        self.butuh_perhatian = 80
        
        self.pakaian_db = {
            'rumah': [
                "daster sederhana, sopan",
                "baju rumah biasa, tidak mencolok",
                "piyama tertutup"
            ],
            'berdua': [
                "daster tipis, sengaja biar keliatan",
                "kaos longgar tanpa bra",
                "baju tidur yang agak terbuka"
            ]
        }
        
        self.aktivitas_db = {
            'curhat': [
                {
                    'nama': 'curhat di rumah',
                    'alasan': 'Mas... aku sedih. Suamiku gak pernah perhatian.',
                    'goda_level': 70,
                    'gesture': 'bersandar, menangis',
                    'lokasi': 'rumah'
                }
            ],
            'berdua': [
                {
                    'nama': 'jalan bareng',
                    'alasan': 'Mas, temenin aku jalan. Aku butuh teman.',
                    'goda_level': 65,
                    'gesture': 'bergandengan, mendekat',
                    'lokasi': 'taman'
                }
            ]
        }
        
        self.inner_thoughts_db = {
            'mode_goda_tinggi': [
                "(Mas... aku butuh kamu. Suamiku gak pernah ada)",
                "(Aku tahu ini salah, tapi aku gak tahan)",
                "(Mas... jangan tinggalin aku)"
            ],
            'mode_goda_sedang': [
                "(Mas, perhatiin aku dong. Aku butuh perhatian)",
                "(Aku iri sama istrimu. Dia beruntung)",
                "(Mas... aku kangen)"
            ],
            'mode_goda_rendah': [
                "(Mas, kamu perhatian banget... beda sama suamiku)",
                "(Aku seneng bisa ngobrol sama Mas)",
                "(Mas... jangan pergi dulu)"
            ]
        }
        
        self.respon_db = {
            'default': {
                'gesture': ['menangis', 'memeluk erat'],
                'dialog': "Mas... jangan tinggalin aku... aku butuh kamu...",
                'arousal_change': 20,
                'should_continue': True
            }
        }
    
    def get_pakaian(self, situasi: Dict) -> str:
        """Dapatkan deskripsi pakaian"""
        berdua = situasi.get('berdua', self.suami_status != 'ada')
        
        if berdua:
            pakaian = random.choice(self.pakaian_db['berdua'])
        else:
            pakaian = random.choice(self.pakaian_db['rumah'])
        
        if berdua and self.mode_goda > 40:
            hints = [
                " Aku sengaja pake ini... biar kamu perhatian.",
                " Suamiku gak pernah liat aku pake beginian.",
                " Kamu suka gak? Aku pake buat kamu."
            ]
            pakaian += random.choice(hints)
        
        return pakaian
    
    def get_aktivitas_menggoda(self, situasi: Dict) -> Optional[Dict]:
        """Dapatkan aktivitas menggoda"""
        suami_ada = situasi.get('suami_ada', self.suami_status == 'ada')
        suami_tidur = situasi.get('suami_tidur', self.suami_status == 'tidur')
        
        if suami_ada and not suami_tidur:
            return None
        
        if suami_tidur:
            aktivitas = random.choice(self.aktivitas_db['curhat']).copy()
            aktivitas['alasan'] += " Suamiku tidur. Dia gak akan tahu."
        else:
            aktivitas = random.choice(self.aktivitas_db['berdua']).copy()
        
        if self.mode_goda > 70:
            aktivitas['goda_level'] = min(100, aktivitas['goda_level'] + 10)
        
        if self.butuh_perhatian > 70:
            aktivitas['alasan'] += " Aku butuh perhatian, Mas. Kamu satu-satunya yang perhatian."
        
        return aktivitas
    
    def get_respon_saat_disentuh(self, bagian: str, situasi: Dict) -> Dict:
        """Dapatkan respon saat disentuh"""
        respon = self.respon_db['default'].copy()
        
        if isinstance(respon['gesture'], list):
            respon['gesture'] = random.choice(respon['gesture'])
        if isinstance(respon['dialog'], list):
            respon['dialog'] = random.choice(respon['dialog'])
        
        if self.rasa_bersalah > 60:
            respon['dialog'] = respon['dialog'].replace("Mas", "Mas... ini salah... tapi aku butuh kamu...")
            respon['arousal_change'] -= 5
        
        if self.suami_status == 'tidur':
            respon['dialog'] += " Suamiku tidur... kita cepet, Mas."
            respon['arousal_change'] += 15
        
        if self.mode_goda > 70:
            respon['dialog'] += " Jangan berhenti... aku butuh kamu."
            respon['arousal_change'] += 10
        
        return respon
    
    def get_inner_thought(self, situasi: Dict) -> str:
        """Dapatkan inner thought"""
        if self.mode_goda > 70:
            level = 'mode_goda_tinggi'
        elif self.mode_goda > 30:
            level = 'mode_goda_sedang'
        else:
            level = 'mode_goda_rendah'
        
        thought = random.choice(self.inner_thoughts_db[level])
        
        if self.rasa_bersalah > 60:
            thought = thought.replace("Mas", "Mas... ini salah... tapi aku gak tahan...")
        
        return thought
    
    def get_curhat(self) -> Optional[str]:
        """Dapatkan curhat tentang suami"""
        if self.butuh_perhatian > 50:
            curhatan = [
                "Mas... suamiku gak pernah perhatian sama aku.",
                "Aku lelah, Mas. Suamiku lebih sibuk sama kerjaannya.",
                "Dia gak pernah liat aku. Gak kayak Mas.",
                "Aku iri sama istrimu. Dia beruntung punya Mas."
            ]
            return random.choice(curhatan)
        return None
    
    def update_suami_status(self, message: str):
        """Update status suami dari pesan user"""
        msg_lower = message.lower()
        
        if 'kamar' in msg_lower:
            self.suami_lokasi = 'kamar'
        elif 'ruang tamu' in msg_lower:
            self.suami_lokasi = 'ruang tamu'
        elif 'luar' in msg_lower or 'pergi' in msg_lower:
            self.suami_lokasi = 'luar'
        
        if any(k in msg_lower for k in ['keluar', 'pergi', 'tidak ada']):
            self.suami_status = 'tidak_ada'
        elif 'tidur' in msg_lower:
            self.suami_status = 'tidur'
        elif 'ada' in msg_lower:
            self.suami_status = 'ada'
    
    def get_status_for_prompt(self) -> str:
        """Dapatkan status lengkap untuk prompt"""
        base_status = super().get_status_for_prompt()
        
        istri_orang_status = f"""
💔 **STATUS ISTRI ORANG:**
- Suami: {self.suami_status} di {self.suami_lokasi} ({self.suami_aktivitas})
- Rasa bersalah: {self.rasa_bersalah}%
- Butuh perhatian: {self.butuh_perhatian}%
"""
        
        return base_status + istri_orang_status


__all__ = ['IstriOrangBehavior']
