#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Database Fix Script
Fix missing columns and ensure database schema is correct
=============================================================================
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DB-FIX")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# =============================================================================
# DATABASE FIX FUNCTIONS
# =============================================================================

async def fix_state_tracker_columns(db):
    """Fix missing columns in state_tracker table"""
    logger.info("🔧 Fixing state_tracker table...")
    
    # Check existing columns
    columns = await db.fetch_all("PRAGMA table_info(state_tracker)")
    column_names = [col['name'] for col in columns]
    
    logger.info(f"📊 Current columns in state_tracker: {len(column_names)}")
    
    # Define required columns for state_tracker
    required_columns = {
        # Clothing columns
        'clothing_bot_outer': "TEXT",
        'clothing_bot_outer_bottom': "TEXT",
        'clothing_bot_inner_top': "TEXT",
        'clothing_bot_inner_bottom': "TEXT",
        'clothing_user_outer': "TEXT",
        'clothing_user_outer_bottom': "TEXT",
        'clothing_user_inner_bottom': "TEXT",
        'clothing_history': "TEXT",
        
        # Location columns
        'location_bot': "TEXT",
        'location_user': "TEXT",
        'position_bot': "TEXT",
        'position_user': "TEXT",
        'position_relative': "TEXT",
        
        # Family columns
        'family_status': "TEXT",
        'family_location': "TEXT",
        'family_activity': "TEXT",
        'family_estimate_return': "TEXT",
        
        # Activity columns
        'activity_bot': "TEXT",
        'activity_user': "TEXT",
        
        # Time columns
        'current_time': "TEXT",
        'time_override_history': "TEXT DEFAULT '[]'",
        
        # Meta
        'updated_at': "REAL NOT NULL"
    }
    
    added = 0
    for col_name, col_def in required_columns.items():
        if col_name not in column_names:
            try:
                await db.execute(f"ALTER TABLE state_tracker ADD COLUMN {col_name} {col_def}")
                logger.info(f"  ✅ Added column: {col_name}")
                added += 1
            except Exception as e:
                logger.warning(f"  ⚠️ Could not add {col_name}: {e}")
    
    if added > 0:
        logger.info(f"✅ Added {added} missing columns to state_tracker")
    else:
        logger.info("✅ No missing columns in state_tracker")
    
    # Verify after fix
    columns = await db.fetch_all("PRAGMA table_info(state_tracker)")
    logger.info(f"📊 state_tracker now has {len(columns)} columns")
    
    return added


async def fix_registrations_columns(db):
    """Fix missing columns in registrations table"""
    logger.info("🔧 Fixing registrations table...")
    
    # Check existing columns
    columns = await db.fetch_all("PRAGMA table_info(registrations)")
    column_names = [col['name'] for col in columns]
    
    logger.info(f"📊 Current columns in registrations: {len(column_names)}")
    
    # Define all required columns for registrations (42-43 columns)
    required_columns = {
        # Primary & Basic Info (6)
        'id': "TEXT PRIMARY KEY",
        'role': "TEXT NOT NULL",
        'sequence': "INTEGER NOT NULL",
        'status': "TEXT DEFAULT 'active'",
        'created_at': "REAL NOT NULL",
        'last_updated': "REAL NOT NULL",
        
        # Identity (2)
        'bot_identity': "TEXT DEFAULT '{}'",
        'user_identity': "TEXT DEFAULT '{}'",
        
        # Bot Physical (7)
        'bot_name': "TEXT NOT NULL",
        'bot_age': "INTEGER",
        'bot_height': "INTEGER",
        'bot_weight': "INTEGER",
        'bot_chest': "TEXT",
        'bot_hijab': "BOOLEAN DEFAULT 0",
        'bot_photo': "TEXT",
        
        # User Physical (6)
        'user_name': "TEXT NOT NULL",
        'user_status': "TEXT DEFAULT 'lajang'",
        'user_age': "INTEGER",
        'user_height': "INTEGER",
        'user_weight': "INTEGER",
        'user_penis': "INTEGER",
        
        # Stats & Progression (7)
        'level': "INTEGER DEFAULT 1",
        'total_chats': "INTEGER DEFAULT 0",
        'total_climax_bot': "INTEGER DEFAULT 0",
        'total_climax_user': "INTEGER DEFAULT 0",
        'stamina_bot': "INTEGER DEFAULT 100",
        'stamina_user': "INTEGER DEFAULT 100",
        'user_artist_ref': "TEXT",
        
        # Intimacy System (5)
        'in_intimacy_cycle': "BOOLEAN DEFAULT 0",
        'intimacy_cycle_count': "INTEGER DEFAULT 0",
        'intimacy_level': "INTEGER DEFAULT 0",
        'last_climax_time': "REAL",
        'cooldown_until': "REAL",
        
        # Memory & Emotion (4)
        'weighted_memory_score': "REAL DEFAULT 0.5",
        'weighted_memory_data': "TEXT DEFAULT '{}'",
        'emotional_bias': "TEXT DEFAULT '{}'",
        'emotional_state': "TEXT DEFAULT '{}'",
        
        # Secondary Emotion (3)
        'secondary_emotion': "TEXT",
        'secondary_arousal': "INTEGER DEFAULT 0",
        'secondary_emotion_reason': "TEXT",
        
        # Physical State (3)
        'physical_sensation': "TEXT DEFAULT 'biasa aja'",
        'physical_hunger': "INTEGER DEFAULT 30",
        'physical_thirst': "INTEGER DEFAULT 30",
        
        # Environment & Meta (3)
        'physical_temperature': "INTEGER DEFAULT 25",
        'metadata': "TEXT DEFAULT '{}'",
        'last_active': "REAL"
    }
    
    # Check which columns are missing (only for ALTER TABLE, not PRIMARY KEY)
    alterable_columns = {k: v for k, v in required_columns.items() 
                        if k not in ['id'] and 'PRIMARY KEY' not in v}
    
    added = 0
    for col_name, col_def in alterable_columns.items():
        if col_name not in column_names:
            try:
                await db.execute(f"ALTER TABLE registrations ADD COLUMN {col_name} {col_def}")
                logger.info(f"  ✅ Added column: {col_name}")
                added += 1
            except Exception as e:
                logger.warning(f"  ⚠️ Could not add {col_name}: {e}")
    
    if added > 0:
        logger.info(f"✅ Added {added} missing columns to registrations")
    else:
        logger.info("✅ No missing columns in registrations")
    
    # Verify after fix
    columns = await db.fetch_all("PRAGMA table_info(registrations)")
    logger.info(f"📊 registrations now has {len(columns)} columns")
    
    if len(columns) == 42:
        logger.info("🎯 Perfect! 42 columns (standard)")
    elif len(columns) == 43:
        logger.info("🎯 Perfect! 43 columns (with extras)")
    else:
        logger.warning(f"⚠️ Unexpected column count: {len(columns)}")
    
    return added


async def fix_long_term_memory_columns(db):
    """Fix missing columns in long_term_memory table"""
    logger.info("🔧 Fixing long_term_memory table...")
    
    # Check if table exists
    result = await db.fetch_one(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='long_term_memory'"
    )
    
    if not result:
        logger.info("⚠️ long_term_memory table doesn't exist yet, will be created when needed")
        return 0
    
    # Check existing columns
    columns = await db.fetch_all("PRAGMA table_info(long_term_memory)")
    column_names = [col['name'] for col in columns]
    
    required_columns = {
        'status': "TEXT",
        'emotional_tag': "TEXT",
    }
    
    added = 0
    for col_name, col_def in required_columns.items():
        if col_name not in column_names:
            try:
                await db.execute(f"ALTER TABLE long_term_memory ADD COLUMN {col_name} {col_def}")
                logger.info(f"  ✅ Added column: {col_name}")
                added += 1
            except Exception as e:
                logger.warning(f"  ⚠️ Could not add {col_name}: {e}")
    
    if added > 0:
        logger.info(f"✅ Added {added} missing columns to long_term_memory")
    
    return added


async def verify_database(db):
    """Verify all tables and columns"""
    logger.info("\n" + "="*70)
    logger.info("🔍 DATABASE VERIFICATION")
    logger.info("="*70)
    
    # Get all tables
    tables = await db.fetch_all(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    
    for table in tables:
        table_name = table['name']
        columns = await db.fetch_all(f"PRAGMA table_info({table_name})")
        row_count = await db.fetch_one(f"SELECT COUNT(*) as count FROM {table_name}")
        
        logger.info(f"\n📋 Table: {table_name}")
        logger.info(f"   Columns: {len(columns)}")
        logger.info(f"   Rows: {row_count['count']}")
        
        # Special check for critical tables
        if table_name == 'state_tracker':
            required = ['clothing_bot_outer_bottom', 'family_status', 'updated_at']
            missing = [col for col in required if col not in [c['name'] for c in columns]]
            if missing:
                logger.warning(f"   ⚠️ Missing critical columns: {missing}")
            else:
                logger.info(f"   ✅ All critical columns present")
        
        elif table_name == 'registrations':
            col_count = len(columns)
            if col_count in [42, 43]:
                logger.info(f"   ✅ Perfect column count: {col_count}")
            else:
                logger.warning(f"   ⚠️ Unexpected column count: {col_count}")
    
    # Database file size
    try:
        from config import settings
        if hasattr(settings, 'database'):
            db_path = Path(settings.database.path)
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                logger.info(f"\n💾 Database size: {size_mb:.2f} MB")
    except:
        pass
    
    logger.info("="*70)


async def full_database_fix():
    """Run complete database fix"""
    print("\n" + "="*70)
    print("💜 AMORIA - DATABASE FIX UTILITY")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    try:
        # Import database modules
        from database.connection import init_db, get_db, close_db
        
        # Initialize database
        logger.info("📁 Connecting to database...")
        await init_db()
        db = await get_db()
        logger.info("✅ Connected to database\n")
        
        # Run fixes
        fix_results = {}
        
        # Fix registrations table
        fix_results['registrations'] = await fix_registrations_columns(db)
        
        # Fix state_tracker table (check if exists)
        result = await db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='state_tracker'"
        )
        if result:
            fix_results['state_tracker'] = await fix_state_tracker_columns(db)
        else:
            logger.info("⚠️ state_tracker table doesn't exist yet")
            fix_results['state_tracker'] = 0
        
        # Fix long_term_memory table
        fix_results['long_term_memory'] = await fix_long_term_memory_columns(db)
        
        # Commit changes
        await db.commit()
        
        # Verify database
        await verify_database(db)
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("📊 FIX SUMMARY")
        logger.info("="*70)
        total_fixed = sum(fix_results.values())
        
        for table, count in fix_results.items():
            if count > 0:
                logger.info(f"  ✅ {table}: added {count} column(s)")
            else:
                logger.info(f"  ✓ {table}: already up to date")
        
        if total_fixed > 0:
            logger.info(f"\n🎉 TOTAL: {total_fixed} column(s) added")
        else:
            logger.info("\n🎉 Database is already up to date!")
        
        logger.info("="*70)
        logger.info("✅ Database fix completed successfully!")
        logger.info("="*70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            await close_db()
            logger.info("\n📁 Database connection closed")
        except:
            pass


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point"""
    success = asyncio.run(full_database_fix())
    
    if success:
        print("\n✅ Database fix completed!")
        print("You can now start the bot with: python run_deploy.py")
        sys.exit(0)
    else:
        print("\n❌ Database fix failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
