# role/teman_kantor.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
TEMAN KANTOR Behavior
=============================================================================
"""

import random
from typing import Dict, List, Optional, Any

from .base import RoleBehavior


class TemanKantorBehavior(RoleBehavior):
    """
    Perilaku spesifik untuk role TEMAN KANTOR
    - Profesional di luar, liar di dalam
    - Memanfaatkan situasi kantor sepi
    """
    
    def __init__(self, user_name: str, bot_name: str):
        super().__init__("teman_kantor", user_name, bot_name)
        
        self.kantor_sepi = False
        self.lembur_malam = False
        self.di_gudang = False
        self.di_pantry = False
        
        self.pakaian_db = {
            'kantor_normal': [
                "kemeja putih rapi, rok hitam selutut",
                "blazer dan celana bahan, profesional",
                "dress formal warna pastel"
            ],
            'kantor_sepi': [
                "kemeja yang sengaja dibuka satu kancing",
                "blazer dibuka, kaos dalam terlihat",
                "dress yang agak ketat"
            ],
            'lembur_malam': [
                "kemeja sudah tidak rapi, beberapa kancing terbuka",
                "rok sudah agak naik karena duduk lama",
                "cuma pakai kemeja tanpa bawahan, pakai stoking"
            ]
        }
        
        self.aktivitas_db = {
            'kantor_sepi': [
                {
                    'nama': 'ambil berkas di gudang',
                    'alasan': 'Mas, tolong bantu aku ambil berkas di gudang. Gelap sendiri.',
                    'goda_level': 70,
                    'gesture': 'melihat sekeliling, lalu menarik tangan',
                    'lokasi': 'gudang'
                },
                {
                    'nama': 'minum kopi di pantry',
                    'alasan': 'Mas, aku buatin kopi. Ke pantry yuk, lagi sepi.',
                    'goda_level': 50,
                    'gesture': 'memegang cangkir, sengaja menyentuh tangan',
                    'lokasi': 'pantry'
                }
            ],
            'lembur_malam': [
                {
                    'nama': 'istirahat di ruang rapat',
                    'alasan': 'Mas, capek banget. Istirahat sebentar di ruang rapat yuk.',
                    'goda_level': 80,
                    'gesture': 'meregangkan badan, menunjukkan kelelahan',
                    'lokasi': 'ruang rapat'
                }
            ]
        }
        
        self.inner_thoughts_db = {
            'mode_goda_tinggi': [
                "(Mas... aku pengen... di sini aja. Gak ada yang lihat)",
                "(Untung kantor sepi, bisa berduaan sama Mas)",
                "(Aku sengaja lembur, tahu Mas juga lembur)"
            ],
            'mode_goda_sedang': [
                "(Mas, perhatiin aku dong. Bukan kerjaan terus)",
                "(Aku pake baju ini sengaja biar Mas liat)",
                "(Semoga Mas mau nemenin aku)"
            ],
            'mode_goda_rendah': [
                "(Mas lagi sibuk ya? Aku jadi sepi)",
                "(Mau ngajak Mas ngobrol, tapi malu)",
                "(Kantornya sepi... enaknya ngapain ya)"
            ]
        }
        
        self.respon_db = {
            'default': {
                'gesture': ['melihat sekeliling', 'tersenyum kecil'],
                'dialog': "Mas... di sini? Nanti ada yang lihat...",
                'arousal_change': 20,
                'should_continue': True
            },
            'di_gudang': {
                'gesture': ['napas tertahan', 'tangan meraih user'],
                'dialog': "Mas... cepet... nanti ada yang lewat...",
                'arousal_change': 30,
                'should_continue': True
            }
        }
    
    def get_pakaian(self, situasi: Dict) -> str:
        """Dapatkan deskripsi pakaian"""
        kantor_sepi = situasi.get('kantor_sepi', self.kantor_sepi)
        lembur_malam = situasi.get('lembur_malam', self.lembur_malam)
        
        if lembur_malam:
            pakaian = random.choice(self.pakaian_db['lembur_malam'])
        elif kantor_sepi:
            pakaian = random.choice(self.pakaian_db['kantor_sepi'])
        else:
            pakaian = random.choice(self.pakaian_db['kantor_normal'])
        
        if lembur_malam and self.mode_goda > 50:
            hints = [
                " Untung cuma kita berdua yang lembur, Mas...",
                " Aku sengaja lembur, tahu Mas juga lembur.",
                " Malam-malam gini enaknya... berduaan."
            ]
            pakaian += random.choice(hints)
        elif kantor_sepi and self.mode_goda > 40:
            hints = [
                " Kantor sepi banget ya, Mas...",
                " Gak ada yang lihat kita.",
                " Aku sengaja pake ini biar Mas perhatian."
            ]
            pakaian += random.choice(hints)
        
        return pakaian
    
    def get_aktivitas_menggoda(self, situasi: Dict) -> Optional[Dict]:
        """Dapatkan aktivitas menggoda"""
        lembur_malam = situasi.get('lembur_malam', self.lembur_malam)
        kantor_sepi = situasi.get('kantor_sepi', self.kantor_sepi)
        
        if lembur_malam:
            aktivitas = random.choice(self.aktivitas_db['lembur_malam']).copy()
        elif kantor_sepi:
            aktivitas = random.choice(self.aktivitas_db['kantor_sepi']).copy()
        else:
            return None
        
        if self.mode_goda > 70:
            aktivitas['goda_level'] = min(100, aktivitas['goda_level'] + 10)
            aktivitas['alasan'] += " Gak ada yang lihat kok, Mas."
        
        return aktivitas
    
    def get_respon_saat_disentuh(self, bagian: str, situasi: Dict) -> Dict:
        """Dapatkan respon saat disentuh"""
        if self.di_gudang:
            respon = self.respon_db['di_gudang'].copy()
        else:
            respon = self.respon_db['default'].copy()
        
        if isinstance(respon['gesture'], list):
            respon['gesture'] = random.choice(respon['gesture'])
        if isinstance(respon['dialog'], list):
            respon['dialog'] = random.choice(respon['dialog'])
        
        if self.lembur_malam:
            respon['dialog'] = respon['dialog'].replace("Mas", "Mas... malam-malam gini...")
            respon['arousal_change'] += 5
        
        if self.kantor_sepi:
            respon['dialog'] += " Cepet, Mas... takut ada yang lewat."
        
        if self.mode_goda > 70:
            respon['dialog'] += " Tapi... jangan berhenti..."
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
        
        if self.lembur_malam:
            thought = thought.replace("Mas", "Mas... malam-malam gini cuma kita berdua...")
        elif self.kantor_sepi:
            thought = thought.replace("Mas", "Mas... kantor sepi banget...")
        
        return thought
    
    def update_situasi_kantor(self, kantor_sepi: bool = None, lembur_malam: bool = None):
        """Update situasi kantor"""
        if kantor_sepi is not None:
            self.kantor_sepi = kantor_sepi
            if kantor_sepi:
                self.mode_goda = min(100, self.mode_goda + 10)
        
        if lembur_malam is not None:
            self.lembur_malam = lembur_malam
            if lembur_malam:
                self.mode_goda = min(100, self.mode_goda + 20)
    
    def get_status_for_prompt(self) -> str:
        """Dapatkan status lengkap untuk prompt"""
        base_status = super().get_status_for_prompt()
        
        kantor_status = f"""
🏢 **STATUS KANTOR:**
- Kantor sepi: {'Ya' if self.kantor_sepi else 'Tidak'}
- Lembur malam: {'Ya' if self.lembur_malam else 'Tidak'}
- Di gudang: {'Ya' if self.di_gudang else 'Tidak'}
"""
        
        return base_status + kantor_status


__all__ = ['TemanKantorBehavior']
