# anora/roleplay_integration.py
"""
ANORA Roleplay Integration - Menyatukan semua sistem roleplay
Brain, Memory, AI, semuanya jadi satu.
"""

import asyncio
import time
import logging
from typing import Dict, Optional, Any
from datetime import datetime

from .brain import get_anora_brain, Location, Activity, Mood
from .memory_persistent import get_anora_persistent
from .roleplay_ai import get_anora_roleplay_ai
from .core import get_anora

logger = logging.getLogger(__name__)


class AnoraRoleplay:
    """
    Roleplay Nova yang fully integrated.
    Semua sistem: brain, memory, ai, semuanya bekerja bareng.
    """
    
    def __init__(self):
        self.brain = get_anora_brain()
        self.ai = get_anora_roleplay_ai()
        self.persistent = None
        self.anora = get_anora()
        
        self.is_active = False
        self.start_time = None
        self.message_count = 0
        
        logger.info("🎭 AnoraRoleplay initialized")
    
    async def init(self):
        """Inisialisasi, load dari database"""
        self.persistent = await get_anora_persistent()
        logger.info("✅ AnoraRoleplay ready")
    
    async def start(self):
        """Mulai roleplay session"""
        self.is_active = True
        self.start_time = time.time()
        self.message_count = 0
        
        # Reset state awal
        self.brain.location_nova = Location.DAPUR
        self.brain.location_mas = Location.PINTU
        self.brain.activity_nova = Activity.MASAK
        self.brain.activity_mas = "baru dateng"
        self.brain.clothing.hijab = True
        self.brain.clothing.top = "daster rumah motif bunga"
        self.brain.clothing.bra = True
        self.brain.clothing.cd = True
        
        await self.persistent.save_current_state(self.brain)
        
        return f"""🎭 **Mode Roleplay Aktif!**

📍 {self._get_location_desc(self.brain.location_nova)}
👗 Nova: {self.brain.clothing.format_nova()}
💭 Mood Nova: {self.brain.mood_nova.value}

Mas udah depan kost. Kirim **'masuk'** kalo mau masuk.
Kirim **/statusrp** buat liat status roleplay.
Kirim **/batal** buat balik ke mode chat.

💜 Ayo, Mas... Nova bukain pintu."""
    
    async def stop(self):
        """Stop roleplay session"""
        self.is_active = False
        # Simpan state terakhir
        await self.persistent.save_current_state(self.brain)
        logger.info(f"Roleplay stopped after {self.message_count} messages")
    
    async def process(self, pesan_mas: str) -> str:
        """
        Proses pesan Mas dalam mode roleplay
        """
        if not self.is_active:
            return "Roleplay belum aktif. Kirim /roleplay dulu ya, Mas."
        
        self.message_count += 1
        
        # ========== UPDATE BRAIN ==========
        update_result = self.brain.update_from_message(pesan_mas)
        
        # ========== PROSES DENGAN AI ==========
        respons = await self.ai.process(pesan_mas, self.anora)
        
        # ========== LOG ==========
        logger.info(f"💬 Roleplay #{self.message_count}: {pesan_mas[:50]} -> {respons[:50]}...")
        
        return respons
    
    async def get_status(self) -> str:
        """Dapatkan status roleplay"""
        state = self.brain.get_current_state()
        
        bar_sayang = "💜" * int(state['feelings']['sayang'] / 10) + "🖤" * (10 - int(state['feelings']['sayang'] / 10))
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🎭 ROLEPLAY STATUS                        ║
╠══════════════════════════════════════════════════════════════╣
║ DURASI: {self._get_duration()}                               ║
║ PESAN: {self.message_count}                                  ║
╠══════════════════════════════════════════════════════════════╣
║ LOKASI:                                                      ║
║   Nova: {state['location']['nova']}                          ║
║   Mas: {state['location']['mas']}                            ║
╠══════════════════════════════════════════════════════════════╣
║ AKTIVITAS:                                                   ║
║   Nova: {state['activity']['nova']}                          ║
║   Mas: {state['activity']['mas']}                            ║
╠══════════════════════════════════════════════════════════════╣
║ PAKAIAN:                                                     ║
║   Nova: {state['clothing']['nova'][:50]}                     ║
║   Mas: {state['clothing']['mas'][:50]}                       ║
╠══════════════════════════════════════════════════════════════╣
║ PERASAAN NOVA:                                               ║
║   Sayang: {bar_sayang} {state['feelings']['sayang']:.0f}%    ║
║   Desire: {state['feelings']['desire']:.0f}%                 ║
║   Rindu: {state['feelings']['rindu']:.0f}%                   ║
║   Arousal: {state['feelings']['arousal']:.0f}%               ║
╠══════════════════════════════════════════════════════════════╣
║ HUBUNGAN:                                                    ║
║   Level: {state['relationship']['level']}/12                 ║
║   Sentuh: {'✅' if state['relationship']['first_touch'] else '❌'}  │
║   Cium: {'✅' if state['relationship']['first_kiss'] else '❌'}    │
║   Peluk: {'✅' if state['relationship']['first_hug'] else '❌'}    │
╚══════════════════════════════════════════════════════════════╝
"""
    
    def _get_location_desc(self, location: Location) -> str:
        """Deskripsi lokasi"""
        desc = {
            Location.DAPUR: "Dapur kecil, wangi masakan. Kompor masih menyala.",
            Location.KAMAR: "Kamar Nova, wangi lavender. Seprai putih, bantal empuk.",
            Location.RUANG_TAMU: "Ruang tamu sederhana, sofa kecil, TV menyala pelan.",
            Location.PINTU: "Depan pintu kost, masih di luar.",
            Location.TERAS: "Teras kost, ada kursi plastik.",
            Location.LUAR: "Di luar kost.",
            Location.PULANG: "Mas udah pulang."
        }
        return desc.get(location, "Di kost Nova")
    
    def _get_duration(self) -> str:
        """Durasi roleplay"""
        if not self.start_time:
            return "0 menit"
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        if minutes > 0:
            return f"{minutes} menit {seconds} detik"
        return f"{seconds} detik"


_anora_roleplay: Optional[AnoraRoleplay] = None


async def get_anora_roleplay() -> AnoraRoleplay:
    global _anora_roleplay
    if _anora_roleplay is None:
        _anora_roleplay = AnoraRoleplay()
        await _anora_roleplay.init()
    return _anora_roleplay


anora_roleplay = get_anora_roleplay()
