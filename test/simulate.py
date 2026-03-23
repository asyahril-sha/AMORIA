# tests/simulate.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Conversation Simulation
=============================================================================
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from utils.logger import setup_logging
from core.ai_engine import AIEngine
from identity.registration import CharacterRegistration

logger = setup_logging("AMORIA-SIM")


async def simulate_role(role: str):
    """Simulate conversation for a role"""
    logger.info(f"🎭 Simulating role: {role}")
    
    registration = CharacterRegistration.create_new(role, 999)
    engine = AIEngine(registration)
    
    await engine.start_session(role, registration.bot.name, "TestUser")
    
    test_messages = [
        f"Halo {registration.bot.name}, apa kabar?",
        "Lagi ngapain?",
        "Aku kangen sama kamu",
        "Cerita dong tentang hari ini",
        "Aku mau minta tolong",
    ]
    
    for msg in test_messages:
        logger.info(f"User: {msg}")
        response = await engine.process_message(msg, {})
        logger.info(f"Bot: {response[:200]}...")
        await asyncio.sleep(1)
    
    await engine.end_session()
    logger.info(f"✅ Simulation completed for {role}")


async def simulate_all():
    """Simulate all roles"""
    roles = ['ipar', 'teman_kantor', 'janda', 'pelakor', 'istri_orang', 'pdkt', 'sepupu', 'teman_sma', 'mantan']
    
    for role in roles:
        await simulate_role(role)
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(simulate_all())
