# database/repository.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Database Repository - Complete with all methods
Target Realism 9.9/10
=============================================================================
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .connection import get_db
from .models import (
    Registration, RegistrationStatus, CharacterRole,
    WorkingMemoryItem, LongTermMemoryItem, MemoryType,
    StateTracker, ClothingState, MoodType,
    USER_PHYSICAL_TEMPLATES, Backup, BackupType, BackupStatus
)

logger = logging.getLogger(__name__)


class Repository:
    """
    Repository untuk semua operasi database AMORIA 9.9
    """
    
    def __init__(self):
        self.db = None
    
    async def _get_db(self):
        """Get database connection"""
        if not self.db:
            self.db = await get_db()
        return self.db
    
    # =========================================================================
    # REGISTRATION OPERATIONS
    # =========================================================================
    
    async def get_next_sequence(self, role: CharacterRole) -> int:
        """Dapatkan nomor urut berikutnya untuk role tertentu"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT MAX(sequence) as max_seq FROM registrations WHERE role = ?",
            (role.value,)
        )
        
        if result and result['max_seq']:
            return result['max_seq'] + 1
        return 1
    
    async def create_registration(self, registration: Registration) -> str:
        """
        Buat registrasi baru - DYNAMIC QUERY
        Auto menyesuaikan dengan field yang ada di data
        """
        db = await self._get_db()
        data = registration.to_dict()
        
        # =========================================================
        # DYNAMIC COLUMN LIST - semua field yang diperlukan
        # =========================================================
        columns = [
            'id', 'role', 'sequence', 'status', 'created_at', 'last_updated',
            'bot_identity', 'user_identity',
            'bot_name', 'bot_age', 'bot_height', 'bot_weight', 'bot_chest', 'bot_hijab',
            'user_name', 'user_status', 'user_age', 'user_height', 'user_weight',
            'user_penis', 'user_artist_ref',
            'level', 'total_chats', 'total_climax_bot', 'total_climax_user',
            'stamina_bot', 'stamina_user',
            'in_intimacy_cycle', 'intimacy_cycle_count',
            'last_climax_time', 'cooldown_until',
            'weighted_memory_score', 'weighted_memory_data', 'emotional_bias',
            'secondary_emotion', 'secondary_arousal', 'secondary_emotion_reason',
            'physical_sensation', 'physical_hunger', 'physical_thirst', 'physical_temperature',
            'metadata'
        ]
        
        # Ambil values sesuai urutan columns
        values = [data.get(col) for col in columns]
        
        # Buat placeholder
        placeholders = ', '.join(['?' for _ in columns])
        columns_str = ', '.join(columns)
        
        # Execute query
        query = f"INSERT INTO registrations ({columns_str}) VALUES ({placeholders})"
        
        await db.execute(query, tuple(values))
        
        logger.info(f"✅ Created registration: {registration.id}")
        return registration.id
    
    async def get_registration(self, registration_id: str) -> Optional[Registration]:
        """Dapatkan registrasi berdasarkan ID"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT * FROM registrations WHERE id = ?",
            (registration_id,)
        )
        
        if not result:
            return None
        
        return Registration.from_dict(dict(result))
    
    async def get_user_registrations(self, user_id: int, role: Optional[CharacterRole] = None) -> List[Registration]:
        """Dapatkan semua registrasi untuk user"""
        db = await self._get_db()
        
        if role:
            results = await db.fetch_all(
                "SELECT * FROM registrations WHERE role = ? ORDER BY last_updated DESC",
                (role.value,)
            )
        else:
            results = await db.fetch_all(
                "SELECT * FROM registrations ORDER BY last_updated DESC"
            )
        
        registrations = []
        for row in results:
            registrations.append(Registration.from_dict(dict(row)))
        
        return registrations
    
    async def update_registration(self, registration: Registration):
        """Update registrasi - DYNAMIC UPDATE"""
        db = await self._get_db()
        data = registration.to_dict()
        
        registration.last_updated = time.time()
        
        # =========================================================
        # DYNAMIC UPDATE - semua field kecuali id
        # =========================================================
        update_fields = [
            'status', 'last_updated',
            'bot_identity', 'user_identity',
            'bot_name', 'bot_age', 'bot_height', 'bot_weight', 'bot_chest', 'bot_hijab',
            'user_name', 'user_status', 'user_age', 'user_height', 'user_weight',
            'user_penis', 'user_artist_ref',
            'level', 'total_chats', 'total_climax_bot', 'total_climax_user',
            'stamina_bot', 'stamina_user',
            'in_intimacy_cycle', 'intimacy_cycle_count',
            'last_climax_time', 'cooldown_until',
            'weighted_memory_score', 'weighted_memory_data', 'emotional_bias',
            'secondary_emotion', 'secondary_arousal', 'secondary_emotion_reason',
            'physical_sensation', 'physical_hunger', 'physical_thirst', 'physical_temperature',
            'metadata'
        ]
        
        # Ambil values
        values = [data.get(field) for field in update_fields]
        values.append(registration.id)  # WHERE clause
        
        # Buat SET clause
        set_clause = ', '.join([f"{field} = ?" for field in update_fields])
        
        query = f"UPDATE registrations SET {set_clause} WHERE id = ?"
        
        await db.execute(query, tuple(values))
    
    async def close_registration(self, registration_id: str):
        """Tutup registrasi (close session)"""
        db = await self._get_db()
        await db.execute(
            "UPDATE registrations SET status = ?, last_updated = ? WHERE id = ?",
            (RegistrationStatus.CLOSED.value, time.time(), registration_id)
        )
        logger.info(f"📁 Closed registration: {registration_id}")
    
    async def end_registration(self, registration_id: str):
        """Akhiri registrasi (hapus permanen)"""
        db = await self._get_db()
        await db.execute(
            "UPDATE registrations SET status = ?, last_updated = ? WHERE id = ?",
            (RegistrationStatus.ENDED.value, time.time(), registration_id)
        )
        logger.info(f"💔 Ended registration: {registration_id}")
    
    async def delete_registration(self, registration_id: str):
        """Hapus registrasi permanen"""
        db = await self._get_db()
        await db.execute("DELETE FROM registrations WHERE id = ?", (registration_id,))
        logger.info(f"🗑️ Deleted registration: {registration_id}")
    
    # =========================================================================
    # WORKING MEMORY OPERATIONS
    # =========================================================================
    
    async def add_to_working_memory(self, item: WorkingMemoryItem):
        """Tambah item ke working memory"""
        db = await self._get_db()
        data = item.to_dict()
        
        columns = ['registration_id', 'chat_index', 'timestamp', 'user_message', 'bot_response', 'context']
        values = [data.get(col) for col in columns]
        placeholders = ', '.join(['?' for _ in columns])
        columns_str = ', '.join(columns)
        
        query = f"INSERT INTO working_memory ({columns_str}) VALUES ({placeholders})"
        
        await db.execute(query, tuple(values))
    
    async def get_working_memory(self, registration_id: str, limit: int = 1000) -> List[Dict]:
        """Dapatkan working memory (chat terakhir)"""
        db = await self._get_db()
        
        results = await db.fetch_all(
            """
            SELECT * FROM working_memory
            WHERE registration_id = ?
            ORDER BY chat_index DESC LIMIT ?
            """,
            (registration_id, limit)
        )
        
        results.reverse()
        
        memories = []
        for row in results:
            memories.append({
                'chat_index': row['chat_index'],
                'timestamp': row['timestamp'],
                'user': row['user_message'],
                'bot': row['bot_response'],
                'importance': row.get('importance', 0.3),
                'context': json.loads(row['context']) if row['context'] else {}
            })
        
        return memories
    
    async def get_last_chat_index(self, registration_id: str) -> int:
        """Dapatkan index chat terakhir"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT MAX(chat_index) as max_idx FROM working_memory WHERE registration_id = ?",
            (registration_id,)
        )
        
        return result['max_idx'] if result and result['max_idx'] else 0
    
    async def cleanup_old_working_memory(self, registration_id: str, keep: int = 1000):
        """Hapus working memory lama, sisakan keep terakhir"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            """
            SELECT MIN(chat_index) as min_keep FROM (
                SELECT chat_index FROM working_memory
                WHERE registration_id = ?
                ORDER BY chat_index DESC LIMIT ?
            )
            """,
            (registration_id, keep)
        )
        
        if result and result['min_keep']:
            await db.execute(
                "DELETE FROM working_memory WHERE registration_id = ? AND chat_index < ?",
                (registration_id, result['min_keep'])
            )
    
    # =========================================================================
    # LONG TERM MEMORY OPERATIONS
    # =========================================================================
    
    async def add_long_term_memory(
        self,
        registration_id: str,
        memory_type: str,
        content: str,
        importance: float = 0.5,
        status: Optional[str] = None,
        emotional_tag: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Tambah item ke long-term memory"""
        db = await self._get_db()
        
        columns = ['registration_id', 'memory_type', 'content', 'importance', 'timestamp', 'status', 'emotional_tag', 'metadata']
        values = [
            registration_id, memory_type, content, importance,
            time.time(), status, emotional_tag,
            json.dumps(metadata or {})
        ]
        placeholders = ', '.join(['?' for _ in columns])
        columns_str = ', '.join(columns)
        
        query = f"INSERT INTO long_term_memory ({columns_str}) VALUES ({placeholders})"
        
        await db.execute(query, tuple(values))
    
    async def get_long_term_memory(
        self,
        registration_id: str,
        memory_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Dapatkan long-term memory"""
        db = await self._get_db()
        
        if memory_type:
            results = await db.fetch_all(
                """
                SELECT * FROM long_term_memory
                WHERE registration_id = ? AND memory_type = ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
                """,
                (registration_id, memory_type, limit)
            )
        else:
            results = await db.fetch_all(
                """
                SELECT * FROM long_term_memory
                WHERE registration_id = ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
                """,
                (registration_id, limit)
            )
        
        memories = []
        for row in results:
            memories.append({
                'id': row['id'],
                'type': row['memory_type'],
                'content': row['content'],
                'importance': row['importance'],
                'timestamp': row['timestamp'],
                'status': row['status'],
                'emotional_tag': row['emotional_tag'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {}
            })
        
        return memories
    
    # =========================================================================
    # STATE TRACKER OPERATIONS (TANPA EMOTION/AROUSAL/MOOD)
    # =========================================================================
    
    async def save_state(self, state: StateTracker):
        """Simpan state tracker (tanpa emotion/arousal/mood)"""
        db = await self._get_db()
        data = state.to_dict()
        
        state.updated_at = time.time()

        if hasattr(state, '_time_system') and state._time_system:
            data['time_data'] = json.dumps(state._time_system.to_dict())
        
        existing = await db.fetch_one(
            "SELECT registration_id FROM state_tracker WHERE registration_id = ?",
            (state.registration_id,)
        )
        
        if existing:
            # DYNAMIC UPDATE
            update_fields = [
                'location_bot', 'location_user', 'position_bot', 'position_user', 'position_relative',
                'clothing_bot_outer', 'clothing_bot_outer_bottom', 'clothing_bot_inner_top',
                'clothing_bot_inner_bottom', 'clothing_user_outer', 'clothing_user_outer_bottom',
                'clothing_user_inner_bottom', 'clothing_history',
                'family_status', 'family_location', 'family_activity', 'family_estimate_return',
                'activity_bot', 'activity_user', 'current_time', 'time_override_history', 'time_data',
                'updated_at'
            ]
            
            values = [data.get(field) for field in update_fields]
            values.append(state.registration_id)
            
            set_clause = ', '.join([f"{field} = ?" for field in update_fields])
            query = f"UPDATE state_tracker SET {set_clause} WHERE registration_id = ?"
            
            await db.execute(query, tuple(values))
        else:
            # DYNAMIC INSERT
            columns = [
                'registration_id', 'location_bot', 'location_user', 'position_bot',
                'position_user', 'position_relative', 'clothing_bot_outer',
                'clothing_bot_outer_bottom', 'clothing_bot_inner_top',
                'clothing_bot_inner_bottom', 'clothing_user_outer',
                'clothing_user_outer_bottom', 'clothing_user_inner_bottom',
                'clothing_history', 'family_status', 'family_location',
                'family_activity', 'family_estimate_return', 'activity_bot',
                'activity_user', 'current_time', 'time_override_history', 'time_data', 'updated_at'
            ]
            
            values = [data.get(col) for col in columns]
            placeholders = ', '.join(['?' for _ in columns])
            columns_str = ', '.join(columns)
            
            query = f"INSERT INTO state_tracker ({columns_str}) VALUES ({placeholders})"
            
            await db.execute(query, tuple(values))
        
        logger.debug(f"State saved for {state.registration_id}")
    
    async def load_state(self, registration_id: str) -> Optional[StateTracker]:
        """Load state tracker"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT * FROM state_tracker WHERE registration_id = ?",
            (registration_id,)
        )
        
        if not result:
            return None

        if data.get('time_data') and isinstance(data['time_data'], str):
            import json
            data['time_data'] = json.loads(data['time_data'])
        
        return StateTracker.from_dict(dict(result))
    
    # =========================================================================
    # BACKUP OPERATIONS
    # =========================================================================
    
    async def add_backup(self, backup: Backup) -> int:
        """Tambah record backup"""
        db = await self._get_db()
        data = backup.to_dict()
        
        columns = ['filename', 'size', 'created_at', 'type', 'status', 'metadata']
        values = [data.get(col) for col in columns]
        placeholders = ', '.join(['?' for _ in columns])
        columns_str = ', '.join(columns)
        
        query = f"INSERT INTO backups ({columns_str}) VALUES ({placeholders})"
        
        result = await db.execute(query, tuple(values))
        
        return result.lastrowid
    
    async def get_backups(self, limit: int = 10) -> List[Backup]:
        """Dapatkan daftar backup terbaru"""
        db = await self._get_db()
        
        results = await db.fetch_all(
            "SELECT * FROM backups ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        
        backups = []
        for row in results:
            backups.append(Backup.from_dict(dict(row)))
        
        return backups
    
    async def get_stats(self) -> Dict:
        """Dapatkan statistik database"""
        db = await self._get_db()
        
        stats = {}
        
        tables = ['registrations', 'working_memory', 'long_term_memory', 'state_tracker', 'backups']
        
        for table in tables:
            try:
                result = await db.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = result['count'] if result else 0
            except:
                stats[f"{table}_count"] = 0
        
        active = await db.fetch_one(
            "SELECT COUNT(*) as count FROM registrations WHERE status = 'active'"
        )
        stats['active_registrations'] = active['count'] if active else 0
        
        total_chats = await db.fetch_one(
            "SELECT SUM(total_chats) as total FROM registrations"
        )
        stats['total_chats_all_time'] = total_chats['total'] if total_chats and total_chats['total'] else 0
        
        from config import settings
        db_path = settings.database.path
        if db_path.exists():
            stats['db_size_mb'] = round(db_path.stat().st_size / (1024 * 1024), 2)
        else:
            stats['db_size_mb'] = 0
        
        return stats


__all__ = ['Repository']
