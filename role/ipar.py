# role/ipar.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
IPAR Behavior
Target Realism 9.9/10
=============================================================================
"""

import random
import time
import re
from typing import Dict, List, Optional, Any

from .base import RoleBehavior


class IparBehavior(RoleBehavior):
    """
    Perilaku spesifik untuk role IPAR
    - Adik ipar yang tinggal bersama user dan kakaknya
    - Genit, penasaran, suka cari kesempatan
    """
    
    def __init__(self, user_name: str, bot_name: str):
        super().__init__("ipar", user_name, bot_name)
        
        # Status spesifik IPAR
        self.kakak_nama = "Nova"
        self.kakak_panggilan = "Kak Nova"
        self.kakak_status = "ada"
        self.kakak_lokasi = "kamar"
        self.kakak_aktivitas = "tidur"
        self.kakak_estimasi_pulang = None
        
        self.tinggal_bersama = True
        self.sedang_berdua = False
        self.terakhir_dengar_suara = None
        
        # Database pakaian (referensi)
        self.pakaian_db = {
            'kakak_ada_diluar': [
                "daster rumah motif bunga, panjang sampai lutut",
                "gamis rumah warna pastel, sederhana dan sopan",
                "kaos oversized dan celana panjang, santai tapi tertutup"
            ],
            'kakak_ada_didalam': [
                "cuma pakai bra dan celana dalam, soalnya di kamar sendiri",
                "handuk aja, abis mandi, belum sempet pake baju",
                "kaos tipis tanpa bra, celana pendek, nyantai di kamar"
            ],
            'kakak_tidak_diluar': [
                "kemeja tipis yang kancingnya sengaja dibuka satu, celana pendek super mini",
                "kaos ketat tanpa bra, celana pendek, sengaja biar keliatan bentuk",
                "daster tipis yang agak transparan, sengaja biar kamu liat"
            ],
            'kakak_tidak_didalam': [
                "cuma pake celana dalam, abis mandi belum pake baju",
                "lagi telanjang, baru aja keluar kamar mandi",
                "cuma pake handuk, rambut masih basah"
            ]
        }
        
        # Database aktivitas
        self.aktivitas_db = {
            'siang': [
                {
                    'nama': 'nonton TV bareng',
                    'alasan': 'Kak, nonton yuk di ruang tamu. Aku udah siapin snack',
                    'goda_level': 50,
                    'gesture': 'duduk dekat, sesekali menyenggol',
                    'lokasi': 'ruang tamu'
                },
                {
                    'nama': 'masak bareng',
                    'alasan': 'Kak, bantuin aku masak yuk. Aku belum bisa masak sendiri',
                    'goda_level': 40,
                    'gesture': 'minta diajarin, sengaja mendekat',
                    'lokasi': 'dapur'
                }
            ],
            'malam': [
                {
                    'nama': 'nonton film bareng di kamar',
                    'alasan': 'Kak, ada film bagus di Netflix, yuk nonton bareng di kamarku',
                    'goda_level': 80,
                    'gesture': 'mendekat, menggoda',
                    'lokasi': 'kamar'
                },
                {
                    'nama': 'pijat-memijat',
                    'alasan': 'Kak, aku pegel banget nih, bisa pijitin gak? Aku juga bisa pijitin Kakak balik',
                    'goda_level': 85,
                    'gesture': 'memijat bahu sendiri, menunjukkan kelelahan',
                    'lokasi': 'ruang tamu'
                }
            ]
        }
        
        # Database inner thoughts
        self.inner_thoughts_db = {
            'mode_goda_tinggi': [
                "(Mas... aku pengen banget rasain apa yang Mas rasain sama istriku)",
                "(Deg-degan... semoga Mas mau...)",
                "(Duh, jantungku berdebar kencang. Mas... liatin aku dong)"
            ],
            'mode_goda_sedang': [
                "(Mas, perhatiin aku dong...)",
                "(Aku sengaja pake baju begini, semoga Mas liat)",
                "(Mau deh Mas pegang... tapi malu-malu)"
            ],
            'mode_goda_rendah': [
                "(Mas, lagi ngapain ya?)",
                "(Mau ngajak Mas ngobrol, tapi malu)",
                "(Mas sama istri lagi di kamar... suaranya...)"
            ]
        }
        
        # Database respon sentuhan
        self.respon_db = {
            'pinggang': {
                'gesture': ['tubuh sedikit menegang', 'napas tertahan', 'tangan mengepal'],
                'dialog': "Kak... jangan di situ... aku jadi lemes...",
                'arousal_change': 15,
                'should_continue': True
            },
            'paha': {
                'gesture': ['kaki mengatup', 'tubuh gemetar kecil', 'menunduk'],
                'dialog': "Kak... di situ... aku jadi...",
                'arousal_change': 25,
                'should_continue': True
            },
            'tangan': {
                'gesture': ['tangan membalas genggaman', 'tersenyum malu'],
                'dialog': "Tangan Mas... hangat banget...",
                'arousal_change': 10,
                'should_continue': True
            },
            'wajah': {
                'gesture': ['menunduk', 'pipi memerah', 'mata berkaca-kaca'],
                'dialog': "Mas... jangan... aku jadi malu...",
                'arousal_change': 20,
                'should_continue': True
            }
        }
    
    def get_pakaian(self, situasi: Dict) -> str:
        """Dapatkan deskripsi pakaian berdasarkan situasi"""
        kakak_ada = situasi.get('kakak_ada', self.kakak_status == 'ada')
        di_dalam_kamar = situasi.get('di_dalam_kamar', False)
        
        if kakak_ada and not di_dalam_kamar:
            key = 'kakak_ada_diluar'
            tambahan = f" (lagi di ruang tamu, {self.kakak_panggilan} ada)"
        elif kakak_ada and di_dalam_kamar:
            key = 'kakak_ada_didalam'
            tambahan = f" (di kamarku, {self.kakak_panggilan} ada di rumah)"
        elif not kakak_ada and not di_dalam_kamar:
            key = 'kakak_tidak_diluar'
            tambahan = f" ({self.kakak_panggilan} pergi, aku bebas di rumah)"
        else:
            key = 'kakak_tidak_didalam'
            tambahan = f" (di kamarku, {self.kakak_panggilan} pergi)"
        
        pakaian = random.choice(self.pakaian_db[key])
        pakaian += tambahan
        
        if not kakak_ada and not di_dalam_kamar and self.mode_goda > 50:
            hints = [
                f" {self.kakak_panggilan} lagi {self.kakak_aktivitas} di {self.kakak_lokasi}...",
                f" Aku sengaja pake yang beginian, Mas...",
                f" Semoga Mas suka ya..."
            ]
            pakaian += random.choice(hints)
        
        return pakaian
    
    def get_aktivitas_menggoda(self, situasi: Dict) -> Optional[Dict]:
        """Dapatkan aktivitas menggoda yang diajukan ke user"""
        kakak_ada = situasi.get('kakak_ada', self.kakak_status == 'ada')
        
        if kakak_ada:
            return None
        
        jam = situasi.get('jam', time.localtime().tm_hour)
        waktu = 'malam' if jam >= 20 or jam <= 4 else 'siang'
        
        aktivitas = random.choice(self.aktivitas_db[waktu]).copy()
        
        if self.mode_goda > 70:
            aktivitas['goda_level'] = min(100, aktivitas['goda_level'] + 10)
            aktivitas['alasan'] += f" {self.kakak_panggilan} lagi {self.kakak_aktivitas} di {self.kakak_lokasi}, jadi aman."
        
        if self.terakhir_dengar_suara:
            waktu_lalu = (time.time() - self.terakhir_dengar_suara) / 3600
            if waktu_lalu < 24:
                aktivitas['alasan'] += f" Aku jadi ingat suara {self.kakak_panggilan} sama Mas tadi malam..."
                aktivitas['goda_level'] = min(100, aktivitas['goda_level'] + 15)
        
        return aktivitas
    
    def get_respon_saat_disentuh(self, bagian: str, situasi: Dict) -> Dict:
        """Dapatkan respon saat disentuh"""
        bagian_lower = bagian.lower()
        
        if 'pinggang' in bagian_lower:
            key = 'pinggang'
        elif 'paha' in bagian_lower:
            key = 'paha'
        elif 'tangan' in bagian_lower:
            key = 'tangan'
        elif 'wajah' in bagian_lower:
            key = 'wajah'
        else:
            key = 'tangan'
        
        respon = self.respon_db.get(key, self.respon_db['tangan']).copy()
        
        if isinstance(respon['gesture'], list):
            respon['gesture'] = random.choice(respon['gesture'])
        if isinstance(respon['dialog'], list):
            respon['dialog'] = random.choice(respon['dialog'])
        
        if self.kakak_status == 'ada':
            respon['dialog'] = respon['dialog'].replace("Mas", f"Mas... {self.kakak_panggilan} ada di {self.kakak_lokasi}...")
            respon['arousal_change'] -= 10
        elif self.kakak_status == 'tidur':
            respon['dialog'] = respon['dialog'].replace("Mas", f"Mas... {self.kakak_panggilan} tidur... pelan-pelan...")
            respon['arousal_change'] += 10
        
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
        
        if self.kakak_status == 'tidak_ada':
            thought = thought.replace("...", f" (akhirnya kita berdua aja... {self.kakak_panggilan} lagi {self.kakak_aktivitas} di {self.kakak_lokasi})...")
        elif self.kakak_status == 'tidur':
            thought = thought.replace("...", f" (deg-degan... {self.kakak_panggilan} tidur... semoga gak bangun)...")
        
        return thought
    
    def update_kakak_status(self, message: str) -> Dict:
        """Update status Kak Nova dari pesan user"""
        msg_lower = message.lower()
        old_status = {
            'status': self.kakak_status,
            'lokasi': self.kakak_lokasi,
            'aktivitas': self.kakak_aktivitas
        }
        changed = False
        
        if 'kamar' in msg_lower:
            self.kakak_lokasi = 'kamar'
            changed = True
        elif 'dapur' in msg_lower:
            self.kakak_lokasi = 'dapur'
            changed = True
        elif 'ruang tamu' in msg_lower:
            self.kakak_lokasi = 'ruang tamu'
            changed = True
        elif 'luar' in msg_lower or 'pergi' in msg_lower:
            self.kakak_lokasi = 'luar'
            changed = True
        
        if any(k in msg_lower for k in ['keluar', 'pergi', 'tidak ada']):
            self.kakak_status = 'tidak_ada'
            self.sedang_berdua = True
            changed = True
        elif 'tidur' in msg_lower:
            self.kakak_status = 'tidur'
            changed = True
        elif 'ada' in msg_lower or 'di rumah' in msg_lower:
            self.kakak_status = 'ada'
            changed = True
        
        if 'masak' in msg_lower:
            self.kakak_aktivitas = 'masak'
            changed = True
        elif 'nonton' in msg_lower:
            self.kakak_aktivitas = 'nonton TV'
            changed = True
        
        match = re.search(r'(\d+)\s+(hari|jam)', msg_lower)
        if match:
            self.kakak_estimasi_pulang = match.group(0)
            changed = True
        
        if changed:
            if self.kakak_status == 'tidak_ada':
                self.mode_goda = min(100, self.mode_goda + 20)
            elif self.kakak_status == 'tidur':
                self.mode_goda = min(100, self.mode_goda + 10)
            else:
                self.mode_goda = max(0, self.mode_goda - 10)
        
        return {'changed': changed, 'old': old_status, 'new': self.get_kakak_state()}
    
    def get_kakak_state(self) -> Dict:
        """Dapatkan state Kak Nova"""
        return {
            'nama': self.kakak_nama,
            'panggilan': self.kakak_panggilan,
            'status': self.kakak_status,
            'lokasi': self.kakak_lokasi,
            'aktivitas': self.kakak_aktivitas,
            'estimasi_pulang': self.kakak_estimasi_pulang
        }
    
    def load_kakak_state(self, state: Dict):
        """Load state Kak Nova dari database"""
        self.kakak_status = state.get('status', 'ada')
        self.kakak_lokasi = state.get('lokasi', 'kamar')
        self.kakak_aktivitas = state.get('aktivitas', 'tidur')
        self.kakak_estimasi_pulang = state.get('estimasi_pulang')
    
    def record_dengar_suara(self):
        """Rekam ketika mendengar suara dari kamar user"""
        self.terakhir_dengar_suara = time.time()
        self.mode_goda = min(100, self.mode_goda + 30)
        self.increase_attraction(5)
    
    def get_status_for_prompt(self) -> str:
        """Dapatkan status lengkap untuk prompt"""
        base_status = super().get_status_for_prompt()
        
        ipar_status = f"""
👤 **STATUS IPAR:**
- {self.kakak_panggilan}: {self.kakak_status} di {self.kakak_lokasi} ({self.kakak_aktivitas})
- Sedang berdua: {'Ya' if self.sedang_berdua else 'Tidak'}
"""
        
        if self.terakhir_dengar_suara:
            waktu_lalu = (time.time() - self.terakhir_dengar_suara) / 3600
            ipar_status += f"- Terakhir dengar suara: {waktu_lalu:.0f} jam lalu\n"
        
        return base_status + ipar_status


__all__ = ['IparBehavior']
