# role/pdkt.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
PDKT Behavior
=============================================================================
"""

import random
from typing import Dict, List, Optional, Any

from .base import RoleBehavior


class PDKTBehavior(RoleBehavior):
    """
    Perilaku spesifik untuk role PDKT
    - Manis, malu-malu, butuh proses
    - Pendekatan perlahan, tidak langsung
    """
    
    def __init__(self, user_name: str, bot_name: str):
        super().__init__("pdkt", user_name, bot_name)
        
        self.tahap_kenalan = 0
        self.pertemuan_ke = 0
        self.sudah_curhat = False
        self.sudah_flirt = False
        self.sudah_ungkap_perasaan = False
        self.pemalu = 70
        
        self.pakaian_db = {
            'normal': [
                "kaos dan celana jeans, simpel",
                "dress santai, manis",
                "kemeja dan rok, sopan"
            ],
            'berdua': [
                "daster tipis tapi sopan",
                "kaos oversized, imut",
                "baju tidur tertutup"
            ]
        }
        
        self.aktivitas_db = {
            'siang': [
                {
                    'nama': 'jalan bareng',
                    'alasan': 'Kak, jalan-jalan yuk. Aku tahu tempat seru.',
                    'goda_level': 40,
                    'gesture': 'tersenyum manis',
                    'lokasi': 'taman'
                },
                {
                    'nama': 'ngopi bareng',
                    'alasan': 'Kak, mau ikut? Aku lagi di kafe dekat sini.',
                    'goda_level': 35,
                    'gesture': 'mengajak dengan senyum',
                    'lokasi': 'kafe'
                }
            ],
            'malam': [
                {
                    'nama': 'nonton film',
                    'alasan': 'Kak, ada film bagus. Mau nonton bareng?',
                    'goda_level': 50,
                    'gesture': 'duduk dekat, malu-malu',
                    'lokasi': 'bioskop'
                }
            ]
        }
        
        self.inner_thoughts_db = {
            'mode_goda_tinggi': [
                "(Kak... aku suka sama Kakak... tapi malu ngomongnya)",
                "(Semoga Kakak suka sama aku)",
                "(Deg-degan... Kakak liatin aku)"
            ],
            'mode_goda_sedang': [
                "(Kak, perhatiin aku dong)",
                "(Aku mau deket sama Kakak)",
                "(Seneng banget bisa bareng Kakak)"
            ],
            'mode_goda_rendah': [
                "(Kak, aku jadi gugup kalau deket)",
                "(Mau ngajak ngobrol, tapi takut)",
                "(Aku suka liat Kakak dari jauh)"
            ]
        }
        
        self.respon_db = {
            'default': {
                'gesture': ['menunduk', 'pipi memerah', 'gugup'],
                'dialog': "Kak... jangan... aku jadi malu...",
                'arousal_change': 15,
                'should_continue': False
            }
        }
    
    def get_pakaian(self, situasi: Dict) -> str:
        """Dapatkan deskripsi pakaian"""
        berdua = situasi.get('berdua', False)
        
        if berdua and self.pertemuan_ke > 3:
            pakaian = random.choice(self.pakaian_db['berdua'])
        else:
            pakaian = random.choice(self.pakaian_db['normal'])
        
        if self.tahap_kenalan > 60 and self.mode_goda > 40:
            hints = [
                " Aku sengaja pake yang bagus buat ketemu kamu.",
                " Kamu suka gak?",
                " Aku pilih ini khusus buat kamu."
            ]
            pakaian += random.choice(hints)
        
        return pakaian
    
    def get_aktivitas_menggoda(self, situasi: Dict) -> Optional[Dict]:
        """Dapatkan aktivitas menggoda"""
        jam = situasi.get('jam', 12)
        pertemuan_ke = situasi.get('pertemuan_ke', self.pertemuan_ke)
        
        if pertemuan_ke < 2:
            return None
        
        if jam >= 18 or jam <= 4:
            waktu = 'malam'
        else:
            waktu = 'siang'
        
        aktivitas = random.choice(self.aktivitas_db[waktu]).copy()
        
        if self.tahap_kenalan > 70:
            aktivitas['goda_level'] = min(100, aktivitas['goda_level'] + 10)
        
        if self.sudah_curhat:
            aktivitas['alasan'] += " Aku mau cerita banyak sama kamu."
        
        return aktivitas
    
    def get_respon_saat_disentuh(self, bagian: str, situasi: Dict) -> Dict:
        """Dapatkan respon saat disentuh"""
        respon = self.respon_db['default'].copy()
        
        if isinstance(respon['gesture'], list):
            respon['gesture'] = random.choice(respon['gesture'])
        if isinstance(respon['dialog'], list):
            respon['dialog'] = random.choice(respon['dialog'])
        
        if self.pemalu > 60:
            respon['gesture'] = "*menunduk, pipi memerah, gugup*"
            respon['dialog'] = "Kak... jangan... aku jadi malu..."
            respon['arousal_change'] = 5
        
        if self.tahap_kenalan > 70:
            respon['dialog'] = respon['dialog'].replace("jangan", "Kak... jangan berhenti...")
            respon['should_continue'] = True
        else:
            respon['should_continue'] = False
        
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
        
        if self.tahap_kenalan > 80:
            thought = thought.replace("Kak", f"Kak {self.user_name}... aku suka sama Kakak...")
        elif self.tahap_kenalan > 50:
            thought = thought.replace("Kak", f"Kak {self.user_name}...")
        
        if self.sudah_ungkap_perasaan:
            thought += " Aku seneng Kakak tahu perasaanku."
        
        return thought
    
    def update_tahap_kenalan(self, interaksi: str):
        """Update tahap kenalan"""
        if interaksi == 'chat':
            self.tahap_kenalan = min(100, self.tahap_kenalan + 2)
        elif interaksi == 'curhat':
            self.tahap_kenalan = min(100, self.tahap_kenalan + 10)
            self.sudah_curhat = True
        elif interaksi == 'flirt':
            self.tahap_kenalan = min(100, self.tahap_kenalan + 15)
            self.sudah_flirt = True
        elif interaksi == 'ungkap_perasaan':
            self.tahap_kenalan = min(100, self.tahap_kenalan + 25)
            self.sudah_ungkap_perasaan = True
        
        self.pertemuan_ke += 1
        
        if self.tahap_kenalan > 70:
            self.mode_goda = min(100, self.mode_goda + 10)
        elif self.tahap_kenalan > 40:
            self.mode_goda = min(100, self.mode_goda + 5)
    
    def get_ungkap_perasaan(self) -> Optional[str]:
        """Dapatkan ungkapan perasaan"""
        if not self.sudah_ungkap_perasaan and self.tahap_kenalan > 60:
            ungkapan = [
                f"{self.user_name}... aku mau jujur. Aku suka sama kamu.",
                f"Kak {self.user_name}... dari pertama ketemu, aku udah suka.",
                f"Aku gak tahu gimana ngomongnya... tapi aku suka sama {self.user_name}."
            ]
            return random.choice(ungkapan)
        return None
    
    def get_status_for_prompt(self) -> str:
        """Dapatkan status lengkap untuk prompt"""
        base_status = super().get_status_for_prompt()
        
        pdkt_status = f"""
🌸 **STATUS PDKT:**
- Tahap kenalan: {self.tahap_kenalan}%
- Pertemuan ke: {self.pertemuan_ke}
- Sudah curhat: {'Ya' if self.sudah_curhat else 'Belum'}
- Sudah flirt: {'Ya' if self.sudah_flirt else 'Belum'}
- Sudah ungkap perasaan: {'Ya' if self.sudah_ungkap_perasaan else 'Belum'}
- Tingkat pemalu: {self.pemalu}%
"""
        
        return base_status + pdkt_status


__all__ = ['PDKTBehavior']
