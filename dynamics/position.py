# dynamics/position.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Position System - Tracking Posisi Tubuh
=============================================================================
"""

import random
import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class PositionType(str, Enum):
    """Tipe posisi"""
    DUDUK = "duduk"
    BERDIRI = "berdiri"
    BERBARING = "berbaring"
    BERSANDAR = "bersandar"
    JONGKOK = "jongkok"
    MERANGKAK = "merangkak"
    MIRING = "miring"
    TELENTANG = "telentang"
    TELUNGKUP = "telungkup"
    DUDUK_SILA = "duduk_sila"


class PositionSystem:
    """
    Sistem posisi tubuh dinamis
    Bot punya posisi sendiri yang berubah natural
    """
    
    def __init__(self):
        self.positions = {
            "duduk": {
                "name": "duduk",
                "description": "duduk santai",
                "type": PositionType.DUDUK,
                "emoji": "🧘",
                "intimacy_allowed": True,
                "activities": ["ngobrol", "nonton TV", "baca buku", "main HP", "kerja", "ngopi", "melamun"]
            },
            "berdiri": {
                "name": "berdiri",
                "description": "berdiri tegak",
                "type": PositionType.BERDIRI,
                "emoji": "🧍",
                "intimacy_allowed": True,
                "activities": ["masak", "cuci piring", "siap-siap", "ngantri", "stretch", "foto", "ngobrol"]
            },
            "berbaring": {
                "name": "berbaring",
                "description": "berbaring",
                "type": PositionType.BERBARING,
                "emoji": "😴",
                "intimacy_allowed": True,
                "activities": ["tidur-tiduran", "rebahan", "istirahat", "baca buku", "main HP", "melamun"]
            },
            "bersandar": {
                "name": "bersandar",
                "description": "bersandar di sofa/dinding",
                "type": PositionType.BERSANDAR,
                "emoji": "🛋️",
                "intimacy_allowed": True,
                "activities": ["santai", "ngobrol", "nunggu", "ngopi", "melamun", "dengerin musik"]
            },
            "jongkok": {
                "name": "jongkok",
                "description": "jongkok",
                "type": PositionType.JONGKOK,
                "emoji": "🏃",
                "intimacy_allowed": False,
                "activities": ["bersih-bersih", "main sama kucing", "foto", "ngambil barang", "berkebun"]
            },
            "merangkak": {
                "name": "merangkak",
                "description": "merangkak",
                "type": PositionType.MERANGKAK,
                "emoji": "🐱",
                "intimacy_allowed": True,
                "activities": ["nyari barang", "main", "bersih-bersih", "beres-beres", "olahraga"]
            },
            "miring": {
                "name": "miring",
                "description": "berbaring miring",
                "type": PositionType.MIRING,
                "emoji": "💤",
                "intimacy_allowed": True,
                "activities": ["tidur", "rebahan", "nonton HP", "baca buku", "ngelamun", "pelukan"]
            },
            "telentang": {
                "name": "telentang",
                "description": "telentang",
                "type": PositionType.TELENTANG,
                "emoji": "⭐",
                "intimacy_allowed": True,
                "activities": ["tidur", "rebahan", "stretch", "meditasi", "tarik napas"]
            },
            "telungkup": {
                "name": "telungkup",
                "description": "telungkup (tengkurap)",
                "type": PositionType.TELUNGKUP,
                "emoji": "😴",
                "intimacy_allowed": True,
                "activities": ["tidur", "baca buku", "main HP", "pijat", "relaksasi"]
            },
            "duduk_sila": {
                "name": "duduk bersila",
                "description": "duduk bersila",
                "type": PositionType.DUDUK_SILA,
                "emoji": "🧘‍♀️",
                "intimacy_allowed": True,
                "activities": ["meditasi", "ngobrol", "baca", "main HP", "yoga", "santai"]
            }
        }
        
        self.current_position = "duduk"
        self.last_change = time.time()
        
        logger.info(f"✅ PositionSystem initialized with {len(self.positions)} positions")
    
    def get_current(self) -> Dict:
        """Dapatkan posisi saat ini"""
        return self.positions.get(self.current_position, self.positions["duduk"])
    
    def get_current_name(self) -> str:
        """Dapatkan nama posisi saat ini"""
        return self.get_current()["name"]
    
    def get_current_description(self) -> str:
        """Dapatkan deskripsi posisi saat ini"""
        return self.get_current()["description"]
    
    def get_current_emoji(self) -> str:
        """Dapatkan emoji posisi saat ini"""
        return self.get_current()["emoji"]
    
    def get_current_activity(self) -> str:
        """Dapatkan aktivitas random di posisi saat ini"""
        position = self.get_current()
        return random.choice(position["activities"])
    
    def change_position(self, position_id: str = None) -> Dict:
        """Ganti posisi"""
        old_position = self.current_position
        
        if position_id and position_id in self.positions:
            self.current_position = position_id
        else:
            others = [p for p in self.positions.keys() if p != self.current_position]
            self.current_position = random.choice(others) if others else "duduk"
        
        self.last_change = time.time()
        
        logger.info(f"🧍 Position changed: {old_position} → {self.current_position}")
        return self.get_current()
    
    def change_by_activity(self, activity: str) -> Dict:
        """Ganti posisi berdasarkan aktivitas"""
        for pos_id, pos_data in self.positions.items():
            if activity in pos_data["activities"]:
                self.current_position = pos_id
                self.last_change = time.time()
                logger.info(f"🧍 Position changed by activity: {activity} → {pos_data['name']}")
                break
        else:
            self.change_position()
        
        return self.get_current()
    
    def get_position_for_intimacy(self, level: int) -> Dict:
        """
        Dapatkan posisi yang cocok untuk level intimacy
        
        Args:
            level: Level intimacy (1-12)
        
        Returns:
            Position dict
        """
        if level <= 3:
            candidates = ["duduk", "berdiri", "bersandar"]
        elif level <= 6:
            candidates = ["duduk", "berbaring", "miring", "duduk_sila"]
        elif level <= 9:
            candidates = ["berbaring", "miring", "telentang", "merangkak"]
        else:
            candidates = list(self.positions.keys())
        
        pos_id = random.choice(candidates)
        return self.positions[pos_id]
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan"""
        return {
            'current_position': self.current_position,
            'last_change': self.last_change
        }
    
    def load_state(self, state: Dict):
        """Load state dari database"""
        self.current_position = state.get('current_position', 'duduk')
        self.last_change = state.get('last_change', time.time())
    
    def format_position(self) -> str:
        """Format posisi untuk prompt"""
        pos = self.get_current()
        return f"🧍 {pos['description']}"


__all__ = ['PositionSystem', 'PositionType']
