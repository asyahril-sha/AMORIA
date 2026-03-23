# role/janda.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
JANDA Behavior
=============================================================================
"""

import random
from typing import Dict, List, Optional, Any

from .base import RoleBehavior


class JandaBehavior(RoleBehavior):
    """
    Perilaku spesifik untuk role JANDA
    - Berpengalaman, tahu apa yang diinginkan
    - Tidak malu-malu, langsung terang-terangan
    """
    
    def __init__(self, user_name: str, bot_name: str):
        super().__init__("janda", user_name, bot_name)
        
        self.pengalaman = 85
        self.tahu_selera_user = 0
        
        self.pakaian_db = {
            'normal': [
                "daster rumah tipis, sengaja biar keliatan bentuk",
                "kaos ketat dan celana pendek, seksi",
                "baju tidur yang terbuka sedikit"
            ],
            'keluar': [
                "dress pendek yang agak ketat, seksi",
                "kemeja tipis dan rok mini",
                "blus transparan dan jeans ketat"
            ]
        }
        
        self.aktivitas_db = {
            'di_rumah': [
                {
                    'nama': 'nonton film bareng',
                    'alasan': 'Mas, temenin aku nonton. Aku sendiri di rumah.',
                    'goda_level': 80,
                    'gesture': 'duduk dekat, sesekali bersandar',
                    'lokasi': 'ruang tamu'
                }
            ],
            'keluar': [
                {
                    'nama': 'jalan-jalan malam',
                    'alasan': 'Mas, temenin aku jalan. Aku butuh teman.',
                    'goda_level': 75,
                    'gesture': 'bergandengan, mendekat',
                    'lokasi': 'taman'
                }
            ]
        }
        
        self.inner_thoughts_db = {
            'mode_goda_tinggi': [
                "(Mas... aku pengen banget sama Mas)",
                "(Aku tahu Mas juga mau. Cuma gak berani)",
                "(Aku bisa lebih baik dari istrinya)"
            ],
            'mode_goda_sedang': [
                "(Mas, liatin aku dong. Aku di sini)",
                "(Aku sengaja pake begini biar Mas tertarik)",
                "(Semoga Mas mau sama aku)"
            ],
            'mode_goda_rendah': [
                "(Mas lagi sibuk ya? Aku jadi kesepian)",
                "(Mau ngajak Mas, tapi malu-malu)",
                "(Aku butuh perhatian Mas)"
            ]
        }
        
        self.respon_db = {
            'default': {
                'gesture': ['tersenyum puas', 'tangan membalas'],
                'dialog': "Mas... aku suka... jangan berhenti...",
                'arousal_change': 20,
                'should_continue': True
            }
        }
    
    def get_pakaian(self, situasi: Dict) -> str:
        """Dapatkan deskripsi pakaian"""
        di_rumah = situasi.get('di_rumah', True)
        sedang_keluar = situasi.get('sedang_keluar', False)
        
        if sedang_keluar:
            pakaian = random.choice(self.pakaian_db['keluar'])
        else:
            pakaian = random.choice(self.pakaian_db['normal'])
        
        if di_rumah and not sedang_keluar and self.mode_goda > 50:
            hints = [
                " Aku sengaja pake begini buat Mas.",
                " Kamu suka gak? Aku pakein buat kamu.",
                " Aku tahu Mas suka yang beginian."
            ]
            pakaian += random.choice(hints)
        
        return pakaian
    
    def get_aktivitas_menggoda(self, situasi: Dict) -> Optional[Dict]:
        """Dapatkan aktivitas menggoda"""
        di_rumah = situasi.get('di_rumah', True)
        sedang_keluar = situasi.get('sedang_keluar', False)
        
        if di_rumah and not sedang_keluar:
            aktivitas = random.choice(self.aktivitas_db['di_rumah']).copy()
        elif sedang_keluar:
            aktivitas = random.choice(self.aktivitas_db['keluar']).copy()
        else:
            return None
        
        if self.mode_goda > 70:
            aktivitas['goda_level'] = min(100, aktivitas['goda_level'] + 15)
        
        if self.tahu_selera_user > 60:
            aktivitas['alasan'] += " Aku tahu kamu suka yang beginian."
        
        return aktivitas
    
    def get_respon_saat_disentuh(self, bagian: str, situasi: Dict) -> Dict:
        """Dapatkan respon saat disentuh"""
        respon = self.respon_db['default'].copy()
        
        if isinstance(respon['gesture'], list):
            respon['gesture'] = random.choice(respon['gesture'])
        if isinstance(respon['dialog'], list):
            respon['dialog'] = random.choice(respon['dialog'])
        
        respon['arousal_change'] += int(self.pengalaman / 20)
        
        if self.tahu_selera_user > 60:
            respon['dialog'] = respon['dialog'].replace("Mas", "Mas, kamu tahu kan aku suka ginian...")
        
        if self.mode_goda > 70:
            respon['dialog'] += " Aku udah nunggu ini dari dulu."
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
        
        if self.pengalaman > 80:
            thought = thought.replace("Mas", "Mas... aku tahu kamu pasti suka...")
        
        return thought
    
    def belajar_selera_user(self):
        """Belajar selera user dari interaksi"""
        self.tahu_selera_user = min(100, self.tahu_selera_user + 5)
        if self.tahu_selera_user > 50:
            self.mode_goda = min(100, self.mode_goda + 5)
    
    def get_ajakan_langsung(self) -> Optional[str]:
        """Dapatkan ajakan langsung"""
        if self.mode_goda > 60:
            ajakan = [
                "Mas, aku pengen. Kamu mau gak?",
                "Gak usah basa-basi. Kamu mau kan?",
                "Aku tahu kamu juga pengen. Ayo.",
                "Di sini aja. Gak ada yang lihat."
            ]
            return random.choice(ajakan)
        return None
    
    def get_status_for_prompt(self) -> str:
        """Dapatkan status lengkap untuk prompt"""
        base_status = super().get_status_for_prompt()
        
        janda_status = f"""
💃 **STATUS JANDA:**
- Pengalaman: {self.pengalaman}%
- Tahu selera user: {self.tahu_selera_user}%
"""
        
        return base_status + janda_status


__all__ = ['JandaBehavior']
