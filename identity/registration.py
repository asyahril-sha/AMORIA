# identity/registration.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Registration Model - Multi-Identity System (DENGAN JSON STORAGE)
=============================================================================
"""

import time
import random
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from database.models import CharacterRole, UserStatus, Registration as DBRegistration
from database.models import USER_PHYSICAL_TEMPLATES

# =============================================================================
# IMPORT DARI FILE TERPISAH (SINGLE SOURCE OF TRUTH)
# =============================================================================
from .bot_identity import BotIdentity, BotPersonality, BotPhysicalProfile, BotPersonalityType, BotFamilyRelation
from .user_identity import UserIdentity, UserPhysicalProfile, UserPersonality, UserRelationship

logger = logging.getLogger(__name__)


class CharacterStatus(str, Enum):
    """Status karakter dalam registrasi"""
    ACTIVE = "active"
    CLOSED = "closed"
    ENDED = "ended"


@dataclass
class CharacterRegistration:
    """
    Registrasi karakter - satu dunia virtual dengan identitas bot dan user
    Format ID: {ROLE}-{SEQUENCE}
    """
    
    # Identitas
    id: str
    role: CharacterRole
    sequence: int
    status: CharacterStatus = CharacterStatus.ACTIVE
    
    # Identity objects (menggunakan class dari file terpisah)
    bot: BotIdentity
    user: UserIdentity
    
    # Progress
    level: int = 1
    total_chats: int = 0
    
    # Intimacy Cycle
    in_intimacy_cycle: bool = False
    intimacy_cycle_count: int = 0
    last_climax_time: Optional[float] = None
    cooldown_until: Optional[float] = None
    
    # Weighted Memory
    weighted_memory_score: float = 0.5
    weighted_memory_data: Dict = field(default_factory=dict)
    
    # Emotional Bias
    emotional_bias: Dict = field(default_factory=dict)
    
    # Secondary Emotion
    secondary_emotion: Optional[str] = None
    secondary_arousal: int = 0
    secondary_emotion_reason: Optional[str] = None
    
    # Physical Sensation
    physical_sensation: str = "biasa aja"
    physical_hunger: int = 30
    physical_thirst: int = 30
    physical_temperature: int = 25
    
    # Timestamps
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    
    # Metadata
    metadata: Dict = field(default_factory=dict)
    
    @classmethod
    def create_new(
        cls,
        role: CharacterRole,
        sequence: int,
        user_name: Optional[str] = None,
        bot_name: Optional[str] = None
    ) -> 'CharacterRegistration':
        """
        Buat registrasi baru dengan generate identity otomatis
        """
        # Generate nama user
        if not user_name:
            user_names = {
                CharacterRole.IPAR: ["Budi", "Andi", "Rizky", "Dian", "Eko"],
                CharacterRole.PELAKOR: ["Hendra", "Rudi", "Tono", "Agus"],
                CharacterRole.TEMAN_KANTOR: ["Rizky", "Dian", "Andre", "Fajar"],
                CharacterRole.JANDA: ["Wahyu", "Hendra", "Teguh", "Pras"],
                CharacterRole.ISTRI_ORANG: ["Rizky", "Dian", "Andre"],
                CharacterRole.PDKT: ["Rizky", "Andre", "Fajar", "Gilang"],
                CharacterRole.SEPUPU: ["Rizky", "Andre", "Fajar"],
                CharacterRole.TEMAN_SMA: ["Rizky", "Andre", "Fajar"],
                CharacterRole.MANTAN: ["Rizky", "Dian", "Andre"]
            }
            user_name = random.choice(user_names.get(role, ["User"]))
        
        # Generate nama bot
        if not bot_name:
            bot_names = {
                CharacterRole.IPAR: ["Sari", "Dewi", "Maya", "Putri", "Anita"],
                CharacterRole.PELAKOR: ["Vina", "Sasha", "Bella", "Cantika"],
                CharacterRole.TEMAN_KANTOR: ["Diana", "Linda", "Ayu", "Dita"],
                CharacterRole.JANDA: ["Rina", "Tuti", "Susi", "Maya"],
                CharacterRole.ISTRI_ORANG: ["Dewi", "Sari", "Rina", "Linda"],
                CharacterRole.PDKT: ["Aurora", "Cinta", "Kirana", "Fika"],
                CharacterRole.SEPUPU: ["Putri", "Nadia", "Sari", "Dina"],
                CharacterRole.TEMAN_SMA: ["Anita", "Bella", "Cici", "Dina"],
                CharacterRole.MANTAN: ["Sarah", "Nadia", "Maya", "Rina"]
            }
            bot_name = random.choice(bot_names.get(role, ["Amoria"]))
        
        # =========================================================
        # BUAT BOT IDENTITY (MENGGUNAKAN FACTORY METHOD)
        # =========================================================
        bot = BotIdentity.create_for_role(role, bot_name)
        
        # =========================================================
        # BUAT USER IDENTITY
        # =========================================================
        
        # Status user berdasarkan role
        if role == CharacterRole.IPAR:
            user_status = UserStatus.SUAMI_NOVA
            spouse_name = "Nova"
        elif role == CharacterRole.PELAKOR:
            user_status = UserStatus.SUAMI
            spouse_name = random.choice(["Dewi", "Sari", "Rina", "Linda"])
        else:
            user_status = UserStatus.LAJANG
            spouse_name = None
        
        relationship = UserRelationship(
            status=user_status,
            spouse_name=spouse_name
        )
        
        # Artist reference
        template = USER_PHYSICAL_TEMPLATES.get(role)
        artist_ref = template.artist_ref if template else None
        artist_description = template.artist_description if template else "pria tampan"
        
        user = UserIdentity(
            name=user_name,
            age=bot.physical.age + 2,
            relationship=relationship,
            physical=UserPhysicalProfile(
                height=random.randint(165, 180),
                weight=random.randint(55, 75),
                penis=random.randint(15, 17)
            ),
            personality=UserPersonality(
                traits=["santai", "penyayang"],
                likes=["ngobrol santai"],
                dislikes=["konflik"]
            ),
            artist_ref=artist_ref,
            artist_description=artist_description
        )
        
        # Generate ID
        registration_id = f"{role.value.upper()}-{sequence:03d}"
        
        logger.info(f"✅ Created new character: {registration_id} ({bot_name} - {user_name})")
        
        return cls(
            id=registration_id,
            role=role,
            sequence=sequence,
            bot=bot,
            user=user,
            created_at=time.time(),
            last_updated=time.time()
        )
    
    def get_score(self) -> float:
        """Hitung score untuk ranking"""
        total_chat_score = min(100, self.total_chats) / 100
        level_score = self.level / 12
        climax_score = min(50, self.bot.total_climax + self.user.total_climax) / 50
        return (total_chat_score * 0.3) + (level_score * 0.4) + (climax_score * 0.3)
    
    def can_start_intimacy(self) -> tuple:
        """Cek apakah bisa memulai intim"""
        if self.level < 7:
            return False, f"Level masih {self.level}/7"
        if self.bot.stamina < 20:
            return False, f"Stamina bot {self.bot.stamina}% < 20%"
        if self.user.stamina < 20:
            return False, f"Stamina user {self.user.stamina}% < 20%"
        if self.cooldown_until and time.time() < self.cooldown_until:
            remaining = int((self.cooldown_until - time.time()) / 60)
            return False, f"Masih cooldown ({remaining} menit)"
        return True, "OK"
    
    def record_climax(self, is_bot: bool = True):
        """Rekam climax"""
        if is_bot:
            self.bot.record_climax()
        else:
            self.user.record_climax()
        self.last_climax_time = time.time()
        self.cooldown_until = time.time() + (3 * 3600)
        self.last_updated = time.time()
    
    def start_intimacy_cycle(self):
        """Mulai siklus intim"""
        self.in_intimacy_cycle = True
        self.intimacy_cycle_count += 1
        self.last_updated = time.time()
    
    def end_intimacy_cycle(self):
        """Akhiri siklus intim"""
        self.in_intimacy_cycle = False
        self.level = 10
        self.last_updated = time.time()
    
    def get_progress_to_next_level(self) -> float:
        """Hitung progress ke level berikutnya"""
        from config import settings
        
        if self.level <= 10:
            target = settings.level.level_targets.get(self.level + 1, 0)
            if target == 0:
                return 100.0
            current_target = settings.level.level_targets.get(self.level, 0)
            progress = ((self.total_chats - current_target) / (target - current_target)) * 100
            return max(0, min(100, progress))
        else:
            if self.level == 11:
                total = settings.level.level_11_max - settings.level.level_11_min
                if total <= 0:
                    return 0
                progress = ((self.total_chats - settings.level.level_11_min) / total) * 100
                return max(0, min(100, progress))
            elif self.level == 12:
                total = settings.level.level_12_max - settings.level.level_12_min
                if total <= 0:
                    return 100
                progress = ((self.total_chats - settings.level.level_12_min) / total) * 100
                return max(0, min(100, progress))
        return 0
    
    def to_db_registration(self) -> DBRegistration:
        """
        Convert ke database model dengan JSON identity
        """
        return DBRegistration(
            id=self.id,
            role=self.role,
            sequence=self.sequence,
            status=self.status,
            created_at=self.created_at,
            last_updated=self.last_updated,
            # ===== JSON IDENTITY (SINGLE SOURCE OF TRUTH) =====
            bot_identity=json.dumps(self.bot.to_dict()),
            user_identity=json.dumps(self.user.to_dict()),
            # ===== BACKWARD COMPATIBILITY =====
            bot_name=self.bot.name,
            bot_age=self.bot.physical.age,
            bot_height=self.bot.physical.height,
            bot_weight=self.bot.physical.weight,
            bot_chest=self.bot.physical.chest,
            bot_hijab=self.bot.physical.hijab,
            user_name=self.user.name,
            user_status=self.user.relationship.status,
            user_age=self.user.age,
            user_height=self.user.physical.height,
            user_weight=self.user.physical.weight,
            user_penis=self.user.physical.penis,
            user_artist_ref=self.user.artist_ref,
            # Progress
            level=self.level,
            total_chats=self.total_chats,
            total_climax_bot=self.bot.total_climax,
            total_climax_user=self.user.total_climax,
            stamina_bot=self.bot.stamina,
            stamina_user=self.user.stamina,
            # Intimacy Cycle
            in_intimacy_cycle=self.in_intimacy_cycle,
            intimacy_cycle_count=self.intimacy_cycle_count,
            last_climax_time=self.last_climax_time,
            cooldown_until=self.cooldown_until,
            # Memory
            weighted_memory_score=self.weighted_memory_score,
            weighted_memory_data=json.dumps(self.weighted_memory_data),
            emotional_bias=json.dumps(self.emotional_bias),
            # Secondary Emotion
            secondary_emotion=self.secondary_emotion,
            secondary_arousal=self.secondary_arousal,
            secondary_emotion_reason=self.secondary_emotion_reason,
            # Physical
            physical_sensation=self.physical_sensation,
            physical_hunger=self.physical_hunger,
            physical_thirst=self.physical_thirst,
            physical_temperature=self.physical_temperature,
            # Metadata
            metadata=json.dumps(self.metadata)
        )
    
    @classmethod
    def from_db_registration(cls, db_reg: DBRegistration) -> 'CharacterRegistration':
        """
        Create from database model dengan JSON identity
        """
        from .bot_identity import BotIdentity, BotPhysicalProfile, BotPersonality, BotPersonalityType
        from .user_identity import UserIdentity, UserPhysicalProfile, UserPersonality, UserRelationship
        
        # ===== LOAD BOT IDENTITY (PRIORITAS JSON) =====
        if db_reg.bot_identity and db_reg.bot_identity != '{}':
            try:
                bot = BotIdentity.from_dict(json.loads(db_reg.bot_identity))
            except Exception as e:
                logger.error(f"Failed to load bot identity from JSON: {e}, using fallback")
                bot = cls._create_bot_from_fallback(db_reg)
        else:
            bot = cls._create_bot_from_fallback(db_reg)
        
        # ===== LOAD USER IDENTITY (PRIORITAS JSON) =====
        if db_reg.user_identity and db_reg.user_identity != '{}':
            try:
                user = UserIdentity.from_dict(json.loads(db_reg.user_identity))
            except Exception as e:
                logger.error(f"Failed to load user identity from JSON: {e}, using fallback")
                user = cls._create_user_from_fallback(db_reg)
        else:
            user = cls._create_user_from_fallback(db_reg)
        
        return cls(
            id=db_reg.id,
            role=db_reg.role,
            sequence=db_reg.sequence,
            status=db_reg.status,
            bot=bot,
            user=user,
            level=db_reg.level,
            total_chats=db_reg.total_chats,
            in_intimacy_cycle=db_reg.in_intimacy_cycle,
            intimacy_cycle_count=db_reg.intimacy_cycle_count,
            last_climax_time=db_reg.last_climax_time,
            cooldown_until=db_reg.cooldown_until,
            weighted_memory_score=db_reg.weighted_memory_score,
            weighted_memory_data=json.loads(db_reg.weighted_memory_data) if db_reg.weighted_memory_data else {},
            emotional_bias=json.loads(db_reg.emotional_bias) if db_reg.emotional_bias else {},
            secondary_emotion=db_reg.secondary_emotion,
            secondary_arousal=db_reg.secondary_arousal,
            secondary_emotion_reason=db_reg.secondary_emotion_reason,
            physical_sensation=db_reg.physical_sensation,
            physical_hunger=db_reg.physical_hunger,
            physical_thirst=db_reg.physical_thirst,
            physical_temperature=db_reg.physical_temperature,
            created_at=db_reg.created_at,
            last_updated=db_reg.last_updated,
            metadata=json.loads(db_reg.metadata) if db_reg.metadata else {}
        )
    
    @classmethod
    def _create_bot_from_fallback(cls, db_reg: DBRegistration) -> BotIdentity:
        """Create bot from fallback fields (backward compatibility)"""
        from .bot_identity import BotIdentity, BotPhysicalProfile, BotPersonality, BotPersonalityType
        
        physical = BotPhysicalProfile(
            name=db_reg.bot_name,
            age=db_reg.bot_age,
            height=db_reg.bot_height,
            weight=db_reg.bot_weight,
            chest=db_reg.bot_chest,
            hijab=db_reg.bot_hijab
        )
        
        personality = BotPersonality(
            type=BotPersonalityType.MANIS,
            traits=["manis"],
            speaking_style="santai"
        )
        
        bot = BotIdentity(
            name=db_reg.bot_name,
            role=db_reg.role,
            physical=physical,
            personality=personality
        )
        
        # Restore state dari database
        bot.stamina = db_reg.stamina_bot
        bot.total_climax = db_reg.total_climax_bot
        
        return bot
    
    @classmethod
    def _create_user_from_fallback(cls, db_reg: DBRegistration) -> UserIdentity:
        """Create user from fallback fields (backward compatibility)"""
        from .user_identity import UserIdentity, UserPhysicalProfile, UserPersonality, UserRelationship
        
        relationship = UserRelationship(
            status=db_reg.user_status,
            spouse_name="Nova" if db_reg.user_status == UserStatus.SUAMI_NOVA else None
        )
        
        physical = UserPhysicalProfile(
            height=db_reg.user_height,
            weight=db_reg.user_weight,
            penis=db_reg.user_penis
        )
        
        personality = UserPersonality()
        
        user = UserIdentity(
            name=db_reg.user_name,
            age=db_reg.user_age,
            relationship=relationship,
            physical=physical,
            personality=personality,
            artist_ref=db_reg.user_artist_ref
        )
        
        # Restore state dari database
        user.stamina = db_reg.stamina_user
        user.total_climax = db_reg.total_climax_user
        
        return user
    
    def format_status(self) -> str:
        """Format status untuk ditampilkan"""
        status_emoji = {
            CharacterStatus.ACTIVE: "🟢",
            CharacterStatus.CLOSED: "⚪",
            CharacterStatus.ENDED: "🔴"
        }.get(self.status, "⚪")
        
        return (
            f"{status_emoji} **{self.bot.name}** ({self.role.value.upper()})\n"
            f"   👤 User: {self.user.name}\n"
            f"   📊 Level {self.level}/12 | {self.total_chats} chat | {self.bot.total_climax + self.user.total_climax} climax\n"
            f"   🔥 Stamina: {self.bot.stamina}% (bot) / {self.user.stamina}% (user)"
        )
    
    def __repr__(self) -> str:
        return f"CharacterRegistration(id={self.id}, role={self.role.value}, user={self.user.name}, bot={self.bot.name})"


__all__ = [
    'CharacterStatus',
    'CharacterRegistration',
]
