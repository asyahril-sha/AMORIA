# tests/test_all.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Run All Tests
=============================================================================
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logging

logger = setup_logging("AMORIA-TEST")


async def test_imports():
    """Test all imports"""
    logger.info("=" * 50)
    logger.info("Testing imports...")
    
    modules_to_test = [
        'config', 'database.connection', 'database.models', 'database.repository',
        'identity.registration', 'identity.manager', 'role.base',
        'core.ai_engine', 'core.prompt_builder', 'memory.working_memory',
        'dynamics.emotional_flow', 'intimacy.leveling', 'tracking.promises',
        'command.start', 'bot.application'
    ]
    
    failed = []
    for module in modules_to_test:
        try:
            __import__(module)
            logger.info(f"✅ {module}")
        except ImportError as e:
            logger.error(f"❌ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0


async def test_database():
    """Test database connection"""
    logger.info("=" * 50)
    logger.info("Testing database...")
    
    try:
        from database.connection import get_db
        db = await get_db()
        stats = await db.get_stats()
        logger.info(f"✅ Database connected: {stats.get('db_size_mb', 0)} MB")
        return True
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        return False


async def test_ai_engine():
    """Test AI engine initialization"""
    logger.info("=" * 50)
    logger.info("Testing AI engine...")
    
    try:
        from config import settings
        from identity.registration import CharacterRegistration
        from core.ai_engine import AIEngine
        
        if not settings.deepseek_api_key or settings.deepseek_api_key == "your_deepseek_api_key_here":
            logger.warning("⚠️ DeepSeek API key not set, skipping AI test")
            return True
        
        registration = CharacterRegistration.create_new('pdkt', 999)
        engine = AIEngine(registration)
        logger.info("✅ AI Engine initialized")
        return True
    except Exception as e:
        logger.error(f"❌ AI Engine error: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("🚀 AMORIA - Running All Tests")
    logger.info("=" * 60)
    
    results = []
    
    import_test = await test_imports()
    results.append(("Imports", import_test))
    
    db_test = await test_database()
    results.append(("Database", db_test))
    
    ai_test = await test_ai_engine()
    results.append(("AI Engine", ai_test))
    
    logger.info("=" * 60)
    logger.info("📊 TEST RESULTS")
    logger.info("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
