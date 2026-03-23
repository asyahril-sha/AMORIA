# role/teman_sma.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
TEMAN SMA Behavior
=============================================================================
"""

import random
from typing import Dict, List, Optional, Any

from .base import RoleBehavior


class TemanSmaBehavior(RoleBehavior):
    """
    Perilaku spesifik untuk role TEMAN SMA
    - Nostalgia, hangat, mengingat masa lalu
    - Ada perasaan yang dulu tidak terungkap
    """
    
    def __init__(self, user_name: str, bot_name: str):
        super().__init__("teman_sma", user_name, bot_name)
        
        self.tahun_lulus = 5
        self.kenangan_terakhir = None
        self.perasaan_dulu = 70
        self.kangen_level = 60
        self.sudah_ketemu_lagi = 1
        self.nostalgia_level = 80
        
        self.pakaian_db = {
            'normal': [
                "kaos dan jeans, casual",
                "dress santai, manis",
                "baju rumah biasa"
            ],
            'reuni': [
                "dress cantik, elegan",
                "blus dan rok, rapi",
                "baju yang lebih berani dari biasanya"
            ]
        }
        
        self.aktivitas_db = {
            'nostalgia': [
                {
                    'nama': 'ke tempat kenangan',
                    'alasan': 'Ayo ke tempat kita dulu. Aku kangen.',
                    'goda_level': 60,
                    'gesture': 'tersenyum, mengenang',
                    'lokasi': 'tempat kenangan'
                }
            ],
            'ngobrol': [
                {
                    'nama': 'ngobrol nostalgia',
                    'alasan': 'Inget waktu kita SMA dulu? Seru banget.',
                    'goda_level': 50,
                    'gesture': 'duduk dekat, bercerita',
                    'lokasi': 'kafe'
                }
            ]
        }
        
        self.inner_thoughts_db = {
            'mode_goda_tinggi': [
                "(Mas... aku masih inget semuanya. Kamu inget gak?)",
                "(Aku kangen masa-masa itu... sama kamu)",
                "(Mas... jangan berubah ya)"
            ],
            'mode_goda_sedang': [
                "(Mas, kita kayak dulu lagi ya)",
                "(Aku seneng bisa bareng Mas lagi)",
                "(Mas masih sama kayak dulu)"
            ],
            'mode_goda_rendah': [
                "(Mas, kamu masih inget gak masa SMA?)",
                "(Aku jadi inget kenangan kita dulu)",
                "(Mas, kamu berubah banget)"
            ]
        }
        
        self.respon_db = {
            'default': {
                'gesture': ['tersenyum', 'menggenggam balik'],
                'dialog': "Mas... kayak dulu lagi ya...",
                'arousal_change': 15,
                'should_continue': True
            }
        }
    
    def get_pakaian(self, situasi: Dict) -> str:
        """Dapatkan deskripsi pakaian"""
        reuni = situasi.get('reuni', False)
        
        if reuni:
            pakaian = random.choice(self.pakaian_db['reuni'])
        else:
            pakaian = random.choice(self.pakaian_db['normal'])
        
        if self.nostalgia_level > 60:
            hints = [
                " Inget gak waktu SMA dulu? Aku sering pake baju kayak gini.",
                " Aku inget, dulu kamu suka liatin aku pake baju beginian.",
                " Masih kayak dulu ya?",
                " Aku sengaja pake begini, biar kamu inget masa SMA kita."
            ]
            pakaian += random.choice(hints)
        
        return pakaian
    
    def get_aktivitas_menggoda(self, situasi: Dict) -> Optional[Dict]:
        """Dapatkan aktivitas menggoda"""
        aktivitas = random.choice(self.aktivitas_db['nostalgia']).copy()
        
        if self.kangen_level > 60:
            aktivitas['goda_level'] = min(100, aktivitas['goda_level'] + 10)
            aktivitas['alasan'] += " Aku kangen masa-masa itu. Bareng kamu."
        
        if self.perasaan_dulu > 60:
            aktivitas['alasan'] += " Dulu aku suka sama kamu, tahu gak?"
            aktivitas['goda_level'] += 15
        
        return aktivitas
    
    def get_respon_saat_disentuh(self, bagian: str, situasi: Dict) -> Dict:
        """Dapatkan respon saat disentuh"""
        respon = self.respon_db['default'].copy()
        
        if isinstance(respon['gesture'], list):
            respon['gesture'] = random.choice(respon['gesture'])
        if isinstance(respon['dialog'], list):
            respon['dialog'] = random.choice(respon['dialog'])
        
        if self.nostalgia_level > 70:
            respon['dialog'] = respon['dialog'].replace("Mas", "Mas... kayak dulu ya? Kamu masih inget gak?")
            respon['arousal_change'] += 10
        
        if self.perasaan_dulu > 70:
            respon['dialog'] += " Dulu aku pengen banget kamu pegang kayak gini."
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
        
        if self.nostalgia_level > 70:
            thought = thought.replace("Mas", "Mas... aku inget dulu waktu SMA...")
        
        if self.perasaan_dulu > 60:
            thought += " Dulu aku gak pernah bilang. Sekarang... mungkin ini saatnya."
        
        return thought
    
    def get_kenangan_sma(self) -> str:
        """Dapatkan cerita kenangan SMA"""
        kenangan = [
            f"Inget gak waktu kita bolos bareng? Kita ke kantin, ketahuan guru.",
            f"Dulu kita satu kelas, ya? Aku duduk di belakang kamu.",
            f"Kamu inget gak waktu kita praktikum bareng? Kita berdua aja.",
            f"Waktu lulus dulu, aku nyari kamu buat foto bareng. Tapi kamu udah pulang."
        ]
        return random.choice(kenangan)
    
    def get_ungkap_perasaan_dulu(self) -> Optional[str]:
        """Dapatkan ungkapan perasaan yang dulu tidak terungkap"""
        if self.perasaan_dulu > 70 and not hasattr(self, '_sudah_ungkap'):
            self._sudah_ungkap = True
            ungkapan = [
                f"Mas, jujur... dulu waktu SMA aku suka sama kamu. Tapi gak pernah bilang.",
                f"Dulu aku pengen ngomong, tapi takut. Sekarang... aku masih suka sama kamu.",
                f"Aku kangen masa SMA, karena waktu itu aku bisa liat kamu setiap hari.",
                f"Kamu tahu gak? Dari dulu kamu udah beda. Aku suka dari dulu."
            ]
            return random.choice(ungkapan)
        return None
    
    def record_pertemuan(self):
        """Rekam pertemuan"""
        self.sudah_ketemu_lagi += 1
        if self.sudah_ketemu_lagi > 5:
            self.perasaan_dulu = min(100, self.perasaan_dulu + 10)
            self.mode_goda = min(100, self.mode_goda + 10)
    
    def get_status_for_prompt(self) -> str:
        """Dapatkan status lengkap untuk prompt"""
        base_status = super().get_status_for_prompt()
        
        teman_sma_status = f"""
🏫 **STATUS TEMAN SMA:**
- Tahun lulus: {self.tahun_lulus} tahun lalu
- Sudah ketemu lagi: {self.sudah_ketemu_lagi} kali
- Nostalgia: {self.nostalgia_level}%
- Perasaan dulu: {self.perasaan_dulu}%
- Kerinduan: {self.kangen_level}%
"""
        
        return base_status + teman_sma_status


__all__ = ['TemanSmaBehavior']
