# dynamics/time_awareness.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Time Awareness - Waktu Real Time dengan Override
=============================================================================
"""

import time
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TimeAwareness:
    """
    Sistem kesadaran waktu
    - Waktu berjalan mengikuti real time
    - User bisa override waktu dengan menyebutkan waktu spesifik
    - Override menjadi memory baru, waktu berjalan lagi dari situ
    """
    
    def __init__(self, start_time: Optional[str] = None):
        """
        Args:
            start_time: Waktu awal (format "HH:MM") atau None untuk random
        """
        if start_time:
            self._current_time = start_time
        else:
            self._current_time = self._random_start_time()
        
        self._start_time = self._current_time
        self._real_start = time.time()
        self._last_update = time.time()
        self._overrides: List[Dict] = []
        self._paused = False
        self._pause_time = 0
        
        logger.info(f"✅ TimeAwareness initialized at {self._current_time}")
    
    def _random_start_time(self) -> str:
        """Generate waktu awal random"""
        times = ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00", "19:00", "20:00", "21:00"]
        return random.choice(times)
    
    def _parse_time(self, time_str: str) -> Tuple[int, int]:
        """Parse string waktu ke (hour, minute)"""
        parts = time_str.split(':')
        return int(parts[0]), int(parts[1])
    
    def _format_time(self, hour: int, minute: int) -> str:
        """Format waktu ke string"""
        return f"{hour:02d}:{minute:02d}"
    
    def _add_minutes(self, time_str: str, minutes: int) -> str:
        """Tambah menit ke waktu"""
        hour, minute = self._parse_time(time_str)
        total_minutes = hour * 60 + minute + minutes
        new_hour = (total_minutes // 60) % 24
        new_minute = total_minutes % 60
        return self._format_time(new_hour, new_minute)
    
    def update(self) -> str:
        """
        Update waktu berdasarkan real time
        
        Returns:
            Waktu saat ini setelah update
        """
        if self._paused:
            return self._current_time
        
        now = time.time()
        elapsed_minutes = (now - self._last_update) / 60
        
        if elapsed_minutes >= 1:
            self._current_time = self._add_minutes(self._current_time, int(elapsed_minutes))
            self._last_update = now
        
        return self._current_time
    
    def override(self, new_time: str, reason: str = "") -> bool:
        """
        Override waktu
        
        Args:
            new_time: Waktu baru (format "HH:MM" atau deskripsi seperti "jam 8 pagi")
            reason: Alasan override
        
        Returns:
            True jika berhasil
        """
        # Parse dari berbagai format
        parsed_time = self._parse_time_from_message(new_time)
        
        if not parsed_time:
            logger.warning(f"Could not parse time: {new_time}")
            return False
        
        old_time = self._current_time
        self._current_time = parsed_time
        self._real_start = time.time()
        self._last_update = time.time()
        
        # Catat override
        self._overrides.append({
            'timestamp': time.time(),
            'old_time': old_time,
            'new_time': self._current_time,
            'reason': reason,
            'raw_input': new_time
        })
        
        # Keep only last 20 overrides
        if len(self._overrides) > 20:
            self._overrides = self._overrides[-20:]
        
        logger.info(f"⏰ Time overridden: {old_time} → {self._current_time} ({reason})")
        return True
    
    def _parse_time_from_message(self, message: str) -> Optional[str]:
        """Parse waktu dari pesan user"""
        msg_lower = message.lower()
        
        # Format: "jam 8 pagi", "pukul 2 siang", dll
        patterns = [
            # "jam 8 pagi" → 08:00
            (r'(jam|pukul)\s+(\d{1,2})\s+(pagi|siang|sore|malam)', self._parse_with_period),
            # "jam 8" → 08:00
            (r'(jam|pukul)\s+(\d{1,2})', self._parse_hour_only),
            # "08:00" atau "8:00"
            (r'(\d{1,2}):(\d{2})', self._parse_exact),
            # "jam setengah 9" → 08:30
            (r'setengah\s+(\d{1,2})', self._parse_half),
            # "jam 8 lewat 15" → 08:15
            (r'(\d{1,2})\s+lewat\s+(\d{1,2})', self._parse_past),
        ]
        
        for pattern, parser in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                return parser(match)
        
        # Kata kunci langsung
        time_keywords = {
            "pagi": "08:00",
            "siang": "12:00",
            "sore": "16:00",
            "malam": "19:00",
            "tengah malam": "00:00",
            "subuh": "04:00"
        }
        
        for keyword, time_str in time_keywords.items():
            if keyword in msg_lower:
                return time_str
        
        return None
    
    def _parse_with_period(self, match) -> str:
        """Parse format "jam 8 pagi" """
        hour = int(match.group(2))
        period = match.group(3)
        
        if period == "malam" and hour < 12:
            hour += 12
        elif period == "pagi" and hour == 12:
            hour = 0
        elif period == "siang" and hour == 12:
            pass
        
        return self._format_time(hour % 24, 0)
    
    def _parse_hour_only(self, match) -> str:
        """Parse format "jam 8" """
        hour = int(match.group(2))
        # Default ke format 24 jam
        return self._format_time(hour % 24, 0)
    
    def _parse_exact(self, match) -> str:
        """Parse format "08:00" """
        hour = int(match.group(1))
        minute = int(match.group(2))
        return self._format_time(hour, minute)
    
    def _parse_half(self, match) -> str:
        """Parse format "setengah 9" (berarti 8:30)"""
        hour = int(match.group(1))
        return self._format_time(hour - 1, 30)
    
    def _parse_past(self, match) -> str:
        """Parse format "8 lewat 15" """
        hour = int(match.group(1))
        minute = int(match.group(2))
        return self._format_time(hour, minute)
    
    def pause(self):
        """Pause waktu"""
        if not self._paused:
            self._paused = True
            self._pause_time = time.time()
            logger.info("⏸️ Time paused")
    
    def resume(self):
        """Resume waktu"""
        if self._paused:
            self._paused = False
            paused_duration = time.time() - self._pause_time
            self._last_update = time.time() - paused_duration
            logger.info("▶️ Time resumed")
    
    def get_current(self) -> str:
        """Dapatkan waktu saat ini"""
        self.update()
        return self._current_time
    
    def get_time_of_day(self) -> str:
        """Dapatkan waktu dalam kategori"""
        hour = int(self.get_current().split(':')[0])
        
        if 5 <= hour < 11:
            return "pagi"
        elif 11 <= hour < 15:
            return "siang"
        elif 15 <= hour < 18:
            return "sore"
        elif 18 <= hour < 22:
            return "malam"
        else:
            return "tengah malam"
    
    def get_elapsed_minutes(self) -> int:
        """Dapatkan menit yang telah berlalu sejak mulai"""
        start_hour, start_min = self._parse_time(self._start_time)
        current_hour, current_min = self._parse_time(self.get_current())
        
        start_total = start_hour * 60 + start_min
        current_total = current_hour * 60 + current_min
        
        if current_total < start_total:
            current_total += 24 * 60
        
        return current_total - start_total
    
    def get_override_count(self) -> int:
        """Dapatkan jumlah override yang terjadi"""
        return len(self._overrides)
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan"""
        return {
            'current_time': self._current_time,
            'start_time': self._start_time,
            'real_start': self._real_start,
            'last_update': self._last_update,
            'overrides': self._overrides,
            'paused': self._paused
        }
    
    def load_state(self, state: Dict):
        """Load state dari database"""
        self._current_time = state.get('current_time', self._random_start_time())
        self._start_time = state.get('start_time', self._current_time)
        self._real_start = state.get('real_start', time.time())
        self._last_update = state.get('last_update', time.time())
        self._overrides = state.get('overrides', [])
        self._paused = state.get('paused', False)
    
    def format_for_prompt(self) -> str:
        """Format waktu untuk prompt"""
        self.update()
        return f"🕐 Waktu: {self._current_time} ({self.get_time_of_day()})"
    
    def format_override_history(self) -> str:
        """Format history override untuk display"""
        if not self._overrides:
            return "Belum ada override waktu"
        
        lines = ["⏰ **RIWAYAT OVERRIDE WAKTU:**"]
        for o in self._overrides[-5:]:
            time_str = datetime.fromtimestamp(o['timestamp']).strftime("%H:%M")
            lines.append(f"• [{time_str}] {o['old_time']} → {o['new_time']} ({o['reason']})")
        
        return "\n".join(lines)


__all__ = ['TimeAwareness']
