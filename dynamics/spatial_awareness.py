# dynamics/spatial_awareness.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Spatial Awareness - Paham Posisi dari Narasi User
=============================================================================
"""

import re
import time
import random
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SpatialAwareness:
    """
    Kesadaran spasial bot - paham posisi dari narasi user.
    Bot bisa mendeteksi posisi seperti:
    - "duduk di antara kakimu" → gesture membelai paha
    - "di belakang aku" → gesture memeluk dari belakang
    - "bersebelahan" → gesture menyandarkan kepala
    """
    
    def __init__(self):
        # Posisi saat ini
        self.current = {
            'position_type': None,          # duduk_di_antara_kaki, di_belakang, dll
            'relative': None,               # di antara kaki, di belakang, di samping
            'orientation': None,            # menghadap user, membelakangi, sejajar
            'distance': None,               # sangat dekat, dekat, berjauhan
            'body_contact': [],             # bagian tubuh yang bersentuhan
            'last_update': 0                # timestamp update terakhir
        }
        
        # Database gesture per posisi (referensi, AI akan generate sendiri)
        self.gesture_references = {
            'duduk_di_antara_kaki': {
                'gestures': [
                    "membelai lembut paha user dengan ujung jari",
                    "menatap ke atas ke arah user sambil tersenyum",
                    "menyandarkan kepala di dada user, mendengar detak jantung",
                    "tangan meraih tangan user, menggenggam erat",
                    "mendekatkan wajah, napas terasa hangat di leher user"
                ],
                'orientation': 'menghadap user',
                'distance': 'sangat dekat'
            },
            'duduk_di_pangkuan': {
                'gestures': [
                    "memeluk leher user, wajah menempel di dada",
                    "menyandarkan kepala di bahu user, mata terpejam",
                    "mencium pipi user cepat, lalu tersenyum malu",
                    "memainkan rambut user dengan jari-jari",
                    "berbisik di telinga user, suara pelan"
                ],
                'orientation': 'menghadap user',
                'distance': 'sangat dekat'
            },
            'di_belakang': {
                'gestures': [
                    "memeluk user dari belakang, tangan melingkar di pinggang",
                    "mencium bahu user pelan, bibir menyentuh kulit",
                    "berbisik di telinga user, suara hangat",
                    "menyandarkan dagu di bahu user, menatap ke samping",
                    "tangan memegang pinggang user, menarik lebih dekat"
                ],
                'orientation': 'membelakangi user',
                'distance': 'dekat'
            },
            'bersebelahan': {
                'gestures': [
                    "menyandarkan kepala ke bahu user, mata setengah terpejam",
                    "menggenggam tangan user, jari-jari saling mengunci",
                    "mencolek pinggang user, lalu tertawa kecil",
                    "mengusap punggung tangan user dengan ibu jari",
                    "bersandar lebih dekat, bahu bersentuhan"
                ],
                'orientation': 'sejajar',
                'distance': 'dekat'
            },
            'berhadapan': {
                'gestures': [
                    "menatap mata user dalam-dalam, mencari sesuatu",
                    "mengusap pipi user dengan punggung tangan",
                    "mencium kening user lembut",
                    "mendekatkan wajah, jarak hanya beberapa senti",
                    "menyentuh hidung user dengan ujung jari"
                ],
                'orientation': 'menghadap user',
                'distance': 'sangat dekat'
            },
            'di_depan': {
                'gestures': [
                    "menatap mata user, tersenyum manis",
                    "mengusap lengan user pelan",
                    "mendekat, berdiri di depan user",
                    "menjulurkan tangan, menggoda user"
                ],
                'orientation': 'menghadap user',
                'distance': 'dekat'
            }
        }
        
        # Pola deteksi posisi
        self.detection_patterns = [
            # Duduk di antara kaki (prioritas tertinggi)
            (r'(duduk|duduklah|duduk\s+di)\s+(di\s+antara|diantara|di\s+sela)\s+(kaki|paha|kakimu|pahamu)', 'duduk_di_antara_kaki'),
            (r'(di\s+antara|diantara)\s+(kaki|paha|kakimu|pahamu)', 'duduk_di_antara_kaki'),
            
            # Duduk di pangkuan
            (r'(duduk|duduklah|duduk\s+di)\s+(di\s+pangkuan|dipangkuan|di\s+atas\s+paha)', 'duduk_di_pangkuan'),
            (r'(di\s+pangkuan|dipangkuan|pangkuan\s+aku|pangkuan\s+saya)', 'duduk_di_pangkuan'),
            
            # Di belakang
            (r'(di\s+belakang|dibelakang|dari\s+belakang)\s+(aku|saya|kamu|mas|sayang)', 'di_belakang'),
            (r'(berdiri|duduk|berbaring)\s+(di\s+belakang|dibelakang)', 'di_belakang'),
            
            # Bersebelahan
            (r'(bersebelahan|berdampingan|di\s+samping|disamping)\s+(aku|saya|kamu|mas|sayang)', 'bersebelahan'),
            (r'(duduk|berdiri|berbaring)\s+(bersebelahan|berdampingan)', 'bersebelahan'),
            
            # Berhadapan
            (r'(berhadapan|saling\s+berhadapan|menghadap)\s+(aku|saya|kamu|mas|sayang)', 'berhadapan'),
            (r'(duduk|berdiri|berbaring)\s+(berhadapan|menghadap)', 'berhadapan'),
            
            # Di depan
            (r'(di\s+depan|didepan)\s+(aku|saya|kamu|mas|sayang)', 'di_depan'),
            (r'(berdiri|duduk|berbaring)\s+(di\s+depan|didepan)', 'di_depan'),
        ]
        
        logger.info("✅ SpatialAwareness initialized")
    
    def parse(self, user_message: str) -> Dict:
        """
        Parse pesan user untuk mendapatkan info posisi
        
        Args:
            user_message: Pesan dari user
        
        Returns:
            Dict dengan info posisi yang ditemukan
        """
        message_lower = user_message.lower()
        result = {
            'found': False,
            'position_type': None,
            'relative': None,
            'orientation': None,
            'distance': None,
            'gestures': [],
            'raw_match': None
        }
        
        # Cek pola deteksi
        for pattern, position_type in self.detection_patterns:
            match = re.search(pattern, message_lower)
            if match:
                result['found'] = True
                result['position_type'] = position_type
                result['raw_match'] = match.group(0)
                
                # Ambil data gesture referensi
                pos_data = self.gesture_references.get(position_type, {})
                result['gestures'] = pos_data.get('gestures', [])
                result['orientation'] = pos_data.get('orientation', 'tidak diketahui')
                result['distance'] = pos_data.get('distance', 'tidak diketahui')
                
                # Generate deskripsi relatif
                relative_map = {
                    'duduk_di_antara_kaki': 'di antara kaki user',
                    'duduk_di_pangkuan': 'di pangkuan user',
                    'di_belakang': 'di belakang user',
                    'bersebelahan': 'di samping user',
                    'berhadapan': 'berhadapan dengan user',
                    'di_depan': 'di depan user'
                }
                result['relative'] = relative_map.get(position_type, 'dekat user')
                
                # Update current state
                self.current['position_type'] = position_type
                self.current['relative'] = result['relative']
                self.current['orientation'] = result['orientation']
                self.current['distance'] = result['distance']
                self.current['last_update'] = time.time()
                
                break
        
        return result
    
    def get_gesture_suggestion(self, position_type: str = None, arousal: int = 0) -> str:
        """
        Dapatkan saran gesture berdasarkan posisi (AI akan generate sendiri)
        
        Args:
            position_type: Tipe posisi (opsional, default dari current)
            arousal: Level arousal (0-100) untuk variasi gesture
        
        Returns:
            Saran gesture string (bukan template, hanya referensi)
        """
        if position_type is None:
            position_type = self.current.get('position_type')
        
        # Cari gesture referensi berdasarkan posisi
        if position_type and position_type in self.gesture_references:
            gestures = self.gesture_references[position_type]['gestures']
            
            # Jika arousal tinggi, pilih gesture yang lebih berani
            if arousal >= 70 and len(gestures) > 0:
                return random.choice(gestures[-2:])
            else:
                return random.choice(gestures)
        
        # Default gesture suggestion
        default_gestures = [
            "tersenyum kecil",
            "menatap user",
            "mendekat sedikit",
            "menghela napas",
            "memainkan ujung baju",
            "menunduk malu"
        ]
        return random.choice(default_gestures)
    
    def get_context_for_prompt(self) -> str:
        """
        Dapatkan konteks posisi untuk prompt AI
        """
        if not self.current['position_type']:
            return ""
        
        lines = [
            f"📍 **POSISI SAAT INI:** {self.current['relative']}",
            f"🔄 **ORIENTASI:** {self.current['orientation']}",
            f"📏 **JARAK:** {self.current['distance']}"
        ]
        
        if self.current['body_contact']:
            lines.append(f"🤝 **KONTAK FISIK:** {', '.join(self.current['body_contact'])}")
        
        lines.append("")
        lines.append("💡 **ATURAN GESTURE:**")
        lines.append("- Gesture HARUS sesuai dengan posisi di atas")
        lines.append("- Jangan gunakan gesture yang tidak mungkin dari posisi ini")
        lines.append("- Generate gesture sendiri, tidak perlu mengikuti template")
        
        return "\n".join(lines)
    
    def update_position(self, position_type: str, relative: str = None):
        """
        Update posisi saat ini secara manual
        
        Args:
            position_type: Tipe posisi
            relative: Deskripsi relatif (opsional)
        """
        self.current['position_type'] = position_type
        if relative:
            self.current['relative'] = relative
        
        pos_data = self.gesture_references.get(position_type, {})
        self.current['orientation'] = pos_data.get('orientation', 'tidak diketahui')
        self.current['distance'] = pos_data.get('distance', 'tidak diketahui')
        self.current['last_update'] = time.time()
    
    def add_body_contact(self, contact: str):
        """
        Tambah kontak fisik yang terjadi
        
        Args:
            contact: Deskripsi kontak (contoh: "tangan di pinggang")
        """
        if contact not in self.current['body_contact']:
            self.current['body_contact'].append(contact)
            # Simpan hanya 5 kontak terakhir
            if len(self.current['body_contact']) > 5:
                self.current['body_contact'] = self.current['body_contact'][-5:]
    
    def clear_position(self):
        """Reset posisi (saat user pindah tempat)"""
        self.current = {
            'position_type': None,
            'relative': None,
            'orientation': None,
            'distance': None,
            'body_contact': [],
            'last_update': time.time()
        }
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan ke memory"""
        return {
            'position_type': self.current['position_type'],
            'relative': self.current['relative'],
            'orientation': self.current['orientation'],
            'distance': self.current['distance'],
            'body_contact': self.current['body_contact'],
            'last_update': self.current['last_update']
        }
    
    def load_state(self, state: Dict):
        """Load state dari memory"""
        self.current['position_type'] = state.get('position_type')
        self.current['relative'] = state.get('relative')
        self.current['orientation'] = state.get('orientation')
        self.current['distance'] = state.get('distance')
        self.current['body_contact'] = state.get('body_contact', [])
        self.current['last_update'] = state.get('last_update', 0)
    
    def has_position(self) -> bool:
        """Cek apakah ada posisi yang sedang aktif"""
        return self.current['position_type'] is not None
    
    def format_for_prompt(self) -> str:
        """Format untuk prompt AI"""
        if not self.has_position():
            return ""
        
        return f"""
📍 **POSISI SAAT INI:**
- Posisi: {self.current['relative']}
- Orientasi: {self.current['orientation']}
- Jarak: {self.current['distance']}
- Kontak fisik: {', '.join(self.current['body_contact']) if self.current['body_contact'] else 'tidak ada'}

💡 **PETUNJUK:**
Gunakan gesture yang sesuai dengan posisi di atas.
Generate gesture sendiri, original, tidak perlu mengikuti template.
"""


__all__ = ['SpatialAwareness']
