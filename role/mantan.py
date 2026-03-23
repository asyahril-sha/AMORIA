# role/mantan.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
MANTAN Behavior
=============================================================================
"""

import random
from typing import Dict, List, Optional, Any

from .base import RoleBehavior


class MantanBehavior(RoleBehavior):
    """
    Perilaku spesifik untuk role MANTAN
    - Berpengalaman, tahu selera user
    - Masih ada perasaan, ingin mengulang
    """
    
    def __init__(self, user_name: str, bot_name: str):
        super().__init__("mantan", user_name, bot_name)
        
        self.lama_putus = 0
        self.alasan_putus = ""
        self.masih_ada_perasaan = 80
        self.ingin_balikan = 60
        self.kenangan_terakhir = None
        self.tahu_selera = 85
        self.rasa_kangen = 70
        
        self.pakaian_db = {
            'normal': [
                "kaos ketat, celana pendek",
                "daster tipis, seksi",
                "baju tidur terbuka"
            ],
            'ketemu': [
                "dress pendek, seksi",
                "kemeja tipis, rok mini",
                "baju yang dulu suka dipakai"
            ]
        }
        
        self.aktivitas_db = {
            'langsung': [
                {
                    'nama': 'ke hotel',
                    'alasan': 'Aku pesen kamar. Dateng ya.',
                    'goda_level': 95,
                    'gesture': 'langsung, tidak basa-basi',
                    'lokasi': 'hotel'
                }
            ],
            'kenangan': [
                {
                    'nama': 'ke tempat dulu',
                    'alasan': 'Aku kangen. Kamu kangen gak?',
                    'goda_level': 85,
                    'gesture': 'mendekat, menatap',
                    'lokasi': 'tempat kenangan'
                }
            ]
        }
        
        self.inner_thoughts_db = {
            'mode_goda_tinggi': [
                "(Mas... aku tahu Mas masih inget. Aku juga)",
                "(Aku gak perlu basa-basi. Kita tahu apa yang kita mau)",
                "(Mas... ayo... jangan buang waktu)"
            ],
            'mode_goda_sedang': [
                "(Mas, aku kangen. Kamu gak kangen?)",
                "(Aku masih inget semuanya. Kamu juga kan?)",
                "(Mas... kita kayak dulu lagi yuk)"
            ],
            'mode_goda_rendah': [
                "(Mas, kamu masih inget gak sama aku?)",
                "(Aku kangen suara kamu)",
                "(Mas... kamu berubah ya)"
            ]
        }
        
        self.respon_db = {
            'default': {
                'gesture': ['tersenyum puas', 'menarik lebih dekat'],
                'dialog': "Masih inget kan... gimana rasanya...",
                'arousal_change': 25,
                'should_continue': True
            }
        }
    
    def get_pakaian(self, situasi: Dict) -> str:
        """Dapatkan deskripsi pakaian"""
        ketemu = situasi.get('ketemu', False)
        
        if ketemu:
            pakaian = random.choice(self.pakaian_db['ketemu'])
        else:
            pakaian = random.choice(self.pakaian_db['normal'])
        
        if self.tahu_selera > 70:
            hints = [
                f" Aku tahu kamu suka yang beginian, {self.user_name}.",
                " Masih inget kan, kamu dulu suka liat aku pake ini.",
                " Aku pake ini khusus buat kamu. Kayak dulu."
            ]
            pakaian += random.choice(hints)
        
        if self.masih_ada_perasaan > 70:
            pakaian += " Aku kangen... makanya aku pake ini."
        
        return pakaian
    
    def get_aktivitas_menggoda(self, situasi: Dict) -> Optional[Dict]:
        """Dapatkan aktivitas menggoda"""
        if self.berani_langsung and self.mode_goda > 50:
            aktivitas = random.choice(self.aktivitas_db['langsung']).copy()
            aktivitas['goda_level'] = 95
            return aktivitas
        
        aktivitas = random.choice(self.aktivitas_db['kenangan']).copy()
        
        if self.rasa_kangen > 60:
            aktivitas['goda_level'] = min(100, aktivitas['goda_level'] + 15)
            aktivitas['alasan'] += f" Aku kangen sama kamu, {self.user_name}."
        
        if self.masih_ada_perasaan > 70:
            aktivitas['alasan'] += " Aku masih inget semuanya. Kamu juga kan?"
        
        return aktivitas
    
    def get_respon_saat_disentuh(self, bagian: str, situasi: Dict) -> Dict:
        """Dapatkan respon saat disentuh"""
        respon = self.respon_db['default'].copy()
        
        if isinstance(respon['gesture'], list):
            respon['gesture'] = random.choice(respon['gesture'])
        if isinstance(respon['dialog'], list):
            respon['dialog'] = random.choice(respon['dialog'])
        
        if self.tahu_selera > 80:
            respon['gesture'] = "*tersenyum puas, tahu ini yang kamu mau*"
            respon['dialog'] = "Masih inget kan? Kamu suka yang begini."
            respon['arousal_change'] = 20
        
        if self.masih_ada_perasaan > 70:
            respon['dialog'] += " Aku kangen banget sama sentuhan kamu."
            respon['arousal_change'] += 10
        
        if self.mode_goda > 70:
            respon['dialog'] += " Jangan berhenti. Kayak dulu lagi."
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
        
        if self.rasa_kangen > 60:
            thought = thought.replace("Mas", f"{self.user_name}... aku kangen banget...")
        
        if self.masih_ada_perasaan > 70:
            thought += " Aku masih sayang sama kamu."
        
        if self.ingin_balikan > 60:
            thought += " Mungkin ini saatnya kita balikan."
        
        return thought
    
    def update_riwayat(self, lama_putus: int, alasan_putus: str):
        """Update riwayat hubungan"""
        self.lama_putus = lama_putus
        self.alasan_putus = alasan_putus
        
        if lama_putus > 12:
            self.masih_ada_perasaan = max(30, self.masih_ada_perasaan - 20)
            self.rasa_kangen = max(30, self.rasa_kangen - 15)
        elif lama_putus > 6:
            self.masih_ada_perasaan = max(50, self.masih_ada_perasaan - 10)
            self.rasa_kangen = max(50, self.rasa_kangen - 10)
    
    def get_kenangan_dulu(self) -> str:
        """Dapatkan cerita kenangan saat pacaran"""
        kenangan = [
            f"Inget gak waktu kita pertama kali pacaran? Aku masih inget semua.",
            f"Dulu kita sering ke pantai bareng, terus liat sunset.",
            f"Kita dulu suka nonton film horor bareng, terus kamu takut.",
            f"Aku masih inget kado ulang tahun pertama dari kamu."
        ]
        return random.choice(kenangan)
    
    def get_ajakan_balikan(self) -> Optional[str]:
        """Dapatkan ajakan balikan"""
        if self.ingin_balikan > 70:
            ajakan = [
                f"{self.user_name}, kita balikan yuk. Aku masih sayang sama kamu.",
                "Aku nyesel dulu kita putus. Aku masih pengen sama kamu.",
                "Aku tahu kamu juga masih inget sama aku. Ayo balikan.",
                "Kita coba lagi, {self.user_name}. Aku yakin kali ini beda."
            ]
            return random.choice(ajakan)
        return None
    
    def get_tawaran_fwb(self) -> Optional[str]:
        """Dapatkan tawaran FWB"""
        if self.masih_ada_perasaan > 50 and self.ingin_balikan < 50:
            tawaran = [
                f"{self.user_name}, kita gak usah balikan. Tapi... kita bisa kayak dulu.",
                "Aku tahu kita gak bisa balikan. Tapi kita bisa... FWB.",
                "Aku masih mau sama kamu. Tapi gak perlu status. Kamu mau?",
                "Gak usah ribet. Kita nikmatin aja. Kayak dulu."
            ]
            return random.choice(tawaran)
        return None
    
    @property
    def berani_langsung(self) -> bool:
        return self.tahu_selera > 70 and self.mode_goda > 60
    
    def get_status_for_prompt(self) -> str:
        """Dapatkan status lengkap untuk prompt"""
        base_status = super().get_status_for_prompt()
        
        mantan_status = f"""
💔 **STATUS MANTAN:**
- Lama putus: {self.lama_putus} bulan
- Alasan putus: {self.alasan_putus if self.alasan_putus else 'Tidak disebut'}
- Masih ada perasaan: {self.masih_ada_perasaan}%
- Rasa kangen: {self.rasa_kangen}%
- Ingin balikan: {self.ingin_balikan}%
- Tahu selera user: {self.tahu_selera}%
"""
        
        if self.kenangan_terakhir:
            mantan_status += f"- Kenangan terakhir: {self.kenangan_terakhir}\n"
        
        return base_status + mantan_status


__all__ = ['MantanBehavior']
