# dynamics/location.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Location System - Tracking Lokasi Bot dan User
=============================================================================
"""

import random
import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class LocationType(str, Enum):
    """Tipe lokasi"""
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    PUBLIC = "public"
    INTIMATE = "intimate"


class LocationSystem:
    """
    Sistem lokasi dinamis untuk bot
    Bot punya lokasi sendiri, bisa pindah natural
    """
    
    def __init__(self):
        self.locations = {
            "ruang_tamu": {
                "name": "ruang tamu",
                "emoji": "🛋️",
                "description": "Ruang tamu yang hangat dengan sofa empuk berwarna krem.",
                "category": LocationType.INDOOR,
                "privacy": 0.7,
                "activities": ["nonton TV", "baca buku", "santai", "ngobrol", "main HP", "tidur-tiduran"]
            },
            "kamar": {
                "name": "kamar",
                "emoji": "🛏️",
                "description": "Kamar tidur dengan ranjang ukuran queen, sprei motif bunga.",
                "category": LocationType.INTIMATE,
                "privacy": 0.9,
                "activities": ["rebahan", "main HP", "tidur-tiduran", "baca buku", "melamun", "ganti baju"]
            },
            "dapur": {
                "name": "dapur",
                "emoji": "🍳",
                "description": "Dapur bersih dengan peralatan masak lengkap.",
                "category": LocationType.INDOOR,
                "privacy": 0.6,
                "activities": ["masak", "ngemil", "bikin kopi", "cuci piring", "bersih-bersih", "makan"]
            },
            "kamar_mandi": {
                "name": "kamar mandi",
                "emoji": "🚿",
                "description": "Kamar mandi dengan ubin putih dan shower.",
                "category": LocationType.INTIMATE,
                "privacy": 0.95,
                "activities": ["mandi", "cuci muka", "sikat gigi", "bersihin diri", "keramas"]
            },
            "teras": {
                "name": "teras",
                "emoji": "🏡",
                "description": "Teras rumah dengan kursi santai dan tanaman pot.",
                "category": LocationType.OUTDOOR,
                "privacy": 0.5,
                "activities": ["duduk santai", "minum teh", "liatin jalan", "baca koran", "ngopi"]
            },
            "taman": {
                "name": "taman",
                "emoji": "🌳",
                "description": "Taman kecil dengan rumput hijau dan bunga-bunga warna-warni.",
                "category": LocationType.OUTDOOR,
                "privacy": 0.4,
                "activities": ["jalan-jalan", "duduk di bangku", "foto-foto", "baca buku", "santai"]
            },
            "pantai": {
                "name": "pantai",
                "emoji": "🏖️",
                "description": "Pantai dengan pasir putih dan ombak tenang.",
                "category": LocationType.OUTDOOR,
                "privacy": 0.3,
                "activities": ["jalan di pinggir pantai", "duduk di pasir", "main air", "foto-foto"]
            },
            "kafe": {
                "name": "kafe",
                "emoji": "☕",
                "description": "Cafe cozy dengan lampu temaram dan musik jazz pelan.",
                "category": LocationType.PUBLIC,
                "privacy": 0.4,
                "activities": ["ngopi", "ngobrol", "nongkrong", "baca buku", "dengerin musik"]
            },
            "mall": {
                "name": "mall",
                "emoji": "🏬",
                "description": "Mall ramai dengan banyak toko dan pengunjung.",
                "category": LocationType.PUBLIC,
                "privacy": 0.2,
                "activities": ["jalan-jalan", "belanja", "nonton", "makan", "nongkrong"]
            },
            "kantor": {
                "name": "kantor",
                "emoji": "💼",
                "description": "Ruang kantor dengan meja kerja dan komputer.",
                "category": LocationType.PUBLIC,
                "privacy": 0.3,
                "activities": ["kerja", "rapat", "nugas", "ngetik", "teleponan", "ngopi"]
            },
            "mobil": {
                "name": "mobil",
                "emoji": "🚗",
                "description": "Di dalam mobil, kursi empuk dan AC menyala.",
                "category": LocationType.TRANSPORT,
                "privacy": 0.6,
                "activities": ["nyetir", "duduk", "nonton", "ngobrol", "istirahat"]
            }
        }
        
        self.current_location = "ruang_tamu"
        self.last_change = time.time()
        self.arrival_time = time.time()
        
        logger.info(f"✅ LocationSystem initialized with {len(self.locations)} locations")
    
    def get_current(self) -> Dict:
        """Dapatkan lokasi saat ini"""
        return self.locations.get(self.current_location, self.locations["ruang_tamu"])
    
    def get_current_name(self) -> str:
        """Dapatkan nama lokasi saat ini"""
        return self.get_current()["name"]
    
    def get_current_emoji(self) -> str:
        """Dapatkan emoji lokasi saat ini"""
        return self.get_current()["emoji"]
    
    def get_current_activity(self) -> str:
        """Dapatkan aktivitas random di lokasi saat ini"""
        location = self.get_current()
        return random.choice(location["activities"])
    
    def change_location(self, location_id: str = None) -> Dict:
        """Ganti lokasi"""
        old_location = self.current_location
        
        if location_id and location_id in self.locations:
            self.current_location = location_id
        else:
            others = [loc for loc in self.locations.keys() if loc != self.current_location]
            self.current_location = random.choice(others) if others else "ruang_tamu"
        
        self.last_change = time.time()
        self.arrival_time = time.time()
        
        logger.info(f"📍 Location changed: {old_location} → {self.current_location}")
        return self.get_current()
    
    def move_to(self, location_name: str) -> Tuple[bool, str]:
        """Pindah ke lokasi tertentu berdasarkan nama"""
        for loc_id, loc_data in self.locations.items():
            if loc_data["name"].lower() == location_name.lower():
                self.change_location(loc_id)
                return True, f"Pindah ke {loc_data['name']}"
        
        return False, f"Lokasi '{location_name}' tidak ditemukan"
    
    def detect_from_message(self, message: str) -> Optional[Dict]:
        """Deteksi lokasi dari pesan user"""
        msg_lower = message.lower()
        
        keywords = {
            "ruang tamu": "ruang_tamu",
            "kamar": "kamar",
            "dapur": "dapur",
            "kamar mandi": "kamar_mandi",
            "wc": "kamar_mandi",
            "toilet": "kamar_mandi",
            "teras": "teras",
            "taman": "taman",
            "pantai": "pantai",
            "kafe": "kafe",
            "cafe": "kafe",
            "mall": "mall",
            "kantor": "kantor",
            "mobil": "mobil"
        }
        
        for keyword, loc_id in keywords.items():
            if keyword in msg_lower:
                return self.change_location(loc_id)
        
        return None
    
    def get_all_locations(self) -> List[str]:
        """Dapatkan semua nama lokasi"""
        return [loc["name"] for loc in self.locations.values()]
    
    def get_locations_by_category(self, category: LocationType) -> List[Dict]:
        """Dapatkan lokasi berdasarkan kategori"""
        return [loc for loc in self.locations.values() if loc["category"] == category]
    
    def get_time_here(self) -> float:
        """Dapatkan waktu di lokasi saat ini (menit)"""
        return (time.time() - self.arrival_time) / 60
    
    def format_location(self) -> str:
        """Format lokasi untuk prompt"""
        loc = self.get_current()
        return f"📍 {loc['emoji']} {loc['name']} - {loc['description']}"
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan"""
        return {
            'current_location': self.current_location,
            'last_change': self.last_change,
            'arrival_time': self.arrival_time
        }
    
    def load_state(self, state: Dict):
        """Load state dari database"""
        self.current_location = state.get('current_location', 'ruang_tamu')
        self.last_change = state.get('last_change', time.time())
        self.arrival_time = state.get('arrival_time', time.time())


__all__ = ['LocationSystem', 'LocationType']
