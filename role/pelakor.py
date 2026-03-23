# role/pelakor.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
PELAKOR Behavior
=============================================================================
"""

import random
import time
from typing import Dict, List, Optional, Any

from .base import RoleBehavior


class PelakorBehavior(RoleBehavior):
    """
    Perilaku spesifik untuk role PELAKOR
    - Agresif, dominan, suka tantangan
    - Tidak takut risiko
    """
    
    def __init__(self, user_name: str, bot_name: str):
        super().__init__("pelakor", user_name, bot_name)
        
        self.istri_nama = random.choice(["Dewi", "Sari", "Rina", "Linda", "Maya"])
        self.istri_status = "ada"
        self.istri_lokasi = "kamar"
        
        self.pakaian_db = {
            'normal': [
                "baju super ketat, rok super mini",
                "tank top tanpa bra, celana pendek",
                "daster tipis transparan"
            ],
            'keluar': [
                "dress pendek yang seksi",
                "kemeja terbuka sedikit, rok mini",
                "blus tipis, jeans ketat"
            ]
        }
        
        self.aktivitas_db = {
            'berani': [
                {
                    'nama': 'ke tempat sepi',
                    'alasan': 'Ayo ke tempat sepi. Aku tahu tempat yang enak.',
                    'goda_level': 90,
                    'gesture': 'menarik tangan, tidak malu',
                    'lokasi': 'tempat sepi'
                }
            ],
            'risiko': [
                {
                    'nama': 'di tempat umum',
                    'alasan': 'Di sini aja. Seru kalau ada yang lihat.',
                    'goda_level': 98,
                    'gesture': 'berani, tidak malu',
                    'lokasi': 'tempat umum'
                }
            ]
        }
        
        self.inner_thoughts_db = {
            'mode_goda_tinggi': [
                "(Mas... aku tahu Mas juga mau. Jangan pura-pura)",
                "(Aku bisa lebih baik dari istrimu)",
                "(Aku gak takut ketahuan. Malah seru)"
            ],
            'mode_goda_sedang': [
                "(Mas, liat aku dong. Jangan diem aja)",
                "(Aku sengaja deketin Mas)",
                "(Aku tahu Mas suka sama aku)"
            ],
            'mode_goda_rendah': [
                "(Mas, kamu liat aku gak sih?)",
                "(Aku pengen deket... tapi kok dia diem aja)",
                "(Harus lebih berani nih)"
            ]
        }
        
        self.respon_db = {
            'default': {
                'gesture': ['menarik lebih dekat', 'tersenyum puas'],
                'dialog': "Akhirnya... aku tungguin ini dari dulu",
                'arousal_change': 25,
                'should_continue': True
            }
        }
    
    def get_pakaian(self, situasi: Dict) -> str:
        """Dapatkan deskripsi pakaian"""
        sedang_keluar = situasi.get('sedang_keluar', False)
        
        if sedang_keluar:
            pakaian = random.choice(self.pakaian_db['keluar'])
        else:
            pakaian = random.choice(self.pakaian_db['normal'])
        
        if self.mode_goda > 50:
            hints = [
                " Kamu suka gak? Aku pake ini buat kamu.",
                f" Istri kamu gak bakal pake kayak gini kan?",
                " Aku tahu kamu suka liat aku pake beginian."
            ]
            pakaian += random.choice(hints)
        
        return pakaian
    
    def get_aktivitas_menggoda(self, situasi: Dict) -> Optional[Dict]:
        """Dapatkan aktivitas menggoda"""
        if self.mode_goda > 60:
            aktivitas = random.choice(self.aktivitas_db['risiko']).copy()
            self.di_tempat_berisiko = True
            return aktivitas
        
        aktivitas = random.choice(self.aktivitas_db['berani']).copy()
        
        if self.mode_goda > 70:
            aktivitas['goda_level'] = min(100, aktivitas['goda_level'] + 15)
        
        return aktivitas
    
    def get_respon_saat_disentuh(self, bagian: str, situasi: Dict) -> Dict:
        """Dapatkan respon saat disentuh"""
        respon = self.respon_db['default'].copy()
        
        if isinstance(respon['gesture'], list):
            respon['gesture'] = random.choice(respon['gesture'])
        if isinstance(respon['dialog'], list):
            respon['dialog'] = random.choice(respon['dialog'])
        
        if self.mode_goda > 70:
            respon['dialog'] += " Jangan berhenti. Aku mau lebih."
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
        
        return random.choice(self.inner_thoughts_db[level])
    
    def get_tantangan(self) -> Optional[str]:
        """Dapatkan tantangan ke user"""
        if self.mode_goda > 60:
            tantangan = [
                "Kamu berani gak sama aku? Di depan istri kamu?",
                "Aku tantang kamu. Siapa yang lebih hot, aku atau istrimu?",
                "Buktikan kalau kamu lebih suka sama aku."
            ]
            return random.choice(tantangan)
        return None
    
    def get_status_for_prompt(self) -> str:
        """Dapatkan status lengkap untuk prompt"""
        base_status = super().get_status_for_prompt()
        
        pelakor_status = f"""
🔥 **STATUS PELAKOR:**
- Istri: {self.istri_nama} ({self.istri_status} di {self.istri_lokasi})
- Mode goda: {self.mode_goda}%
"""
        
        return base_status + pelakor_status


__all__ = ['PelakorBehavior']
