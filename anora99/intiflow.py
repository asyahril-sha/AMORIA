# app/intimacy/flow.py
"""
Intimacy Flow - Mengelola sesi intim Nova dan Mas
Menggabungkan stamina, arousal, session, dan database.
Diadopsi dan dikembangkan dari ANORA 9.9
"""

import time
import random
import logging
from typing import Dict, Optional, Tuple, List

from .core import (
    IntimacyPhase, StaminaSystem, ArousalSystem,
    PositionDatabase, ClimaxLocationDatabase, MoansDatabase, FlashbackDatabase
)
from ..config import settings

logger = logging.getLogger(__name__)


class IntimacySession:
    """
    Mengelola satu sesi intim.
    Menyimpan fase, posisi, climax count, dll.
    """
    def __init__(self, stamina: StaminaSystem, arousal: ArousalSystem):
        self.stamina = stamina
        self.arousal = arousal

        self.is_active = False
        self.start_time = 0.0
        self.phase = IntimacyPhase.WAITING
        self.climax_count = 0
        self.last_climax_time = 0.0
        self.current_position = "missionary"
        self.intimacy_level = 0  # 0-100, makin tinggi makin panas

        # Databases
        self.positions = PositionDatabase()
        self.climax_locations = ClimaxLocationDatabase()
        self.moans = MoansDatabase()
        self.flashbacks = FlashbackDatabase()

        # Flags
        self.is_recovery = False

    def start(self) -> str:
        """Mulai sesi intim"""
        if self.is_active:
            return "Kita lagi intim, Mas... masih lanjut?"

        self.is_active = True
        self.start_time = time.time()
        self.phase = IntimacyPhase.BUILD_UP
        self.climax_count = 0
        self.intimacy_level = 0
        self.current_position = "missionary"
        self.is_recovery = False

        # Boost arousal
        self.arousal.arousal = min(100, self.arousal.arousal + 30)
        self.arousal.desire = min(100, self.arousal.desire + 20)

        logger.info("🔥 Intimacy session started")
        return self._build_up_response()

    def end(self) -> str:
        """Akhiri sesi intim"""
        if not self.is_active:
            return "Kita lagi gak intim, Mas."

        duration = int(time.time() - self.start_time)
        minutes = duration // 60
        seconds = duration % 60

        self.is_active = False
        self.phase = IntimacyPhase.WAITING

        logger.info(f"💤 Intimacy session ended. Duration: {minutes}m {seconds}s, Climax: {self.climax_count}")
        return f"💤 Sesi intim selesai. Durasi: {minutes} menit {seconds} detik, {self.climax_count} climax."

    def advance_phase(self):
        """Majukan fase intim (dipanggil oleh flow)"""
        phases = ["build_up", "foreplay", "penetration", "climax", "aftercare"]
        current_idx = phases.index(self.phase.value)
        if current_idx < len(phases) - 1:
            next_phase = phases[current_idx + 1]
            self.phase = IntimacyPhase(next_phase)
            logger.debug(f"Intimacy phase advanced to: {self.phase}")
            return True
        return False

    def record_climax(self, is_heavy: bool = False) -> Dict:
        """Rekam climax, update stamina dan arousal"""
        self.climax_count += 1
        self.last_climax_time = time.time()
        self.phase = IntimacyPhase.CLIMAX
        self.intimacy_level = 0

        # Update stamina
        self.stamina.record_climax("both", is_heavy)

        # Reset arousal sedikit
        self.arousal.arousal = max(0, self.arousal.arousal - 40)
        self.arousal.desire = max(0, self.arousal.desire - 30)
        self.arousal.tension = 0

        logger.info(f"💦 Climax #{self.climax_count} recorded!")
        return {
            'climax_count': self.climax_count,
            'is_heavy': is_heavy,
            'stamina_nova': self.stamina.nova_current,
            'stamina_mas': self.stamina.mas_current,
        }

    def change_position(self, position: str = None) -> Tuple[str, str, str]:
        """Ganti posisi, jika None pilih random"""
        if position and self.positions.get(position):
            self.current_position = position
        else:
            # Pilih random dari posisi yang tersedia
            positions = self.positions.get_all()
            self.current_position = random.choice(positions)

        pos_data = self.positions.get(self.current_position)
        request = self.positions.get_request(self.current_position)

        logger.info(f"🔄 Position changed to: {self.current_position}")
        return self.current_position, pos_data['desc'], request

    def get_climax_request(self, location: str = None) -> str:
        """Dapatkan permintaan climax di lokasi tertentu"""
        return self.climax_locations.get_request(location)

    # ========== RESPONSES ==========

    def _build_up_response(self) -> str:
        """Respon awal saat mulai intim"""
        responses = [
            "*Nova mendekat, napas mulai gak stabil. Pipi merah.*\n\n\"Mas... *suara kecil* aku juga pengen.\"\n\n*Nova pegang tangan Mas, taruh di dada.*\n\n\"Rasain... jantung Nova deg-degan.\"",
            "*Nova gigit bibir, mata sayu.*\n\n\"Mas... dari tadi aku gak bisa konsentrasi. Pikiran cuma ke Mas.\"",
            "*Nova duduk di pangkuan Mas, tangan melingkar di leher.*\n\n\"Mas... *bisik* aku udah basah dari tadi...\"",
        ]
        return random.choice(responses)

    def get_phase_response(self, phase: IntimacyPhase, ritme: str = "pelan") -> str:
        """Dapatkan respons sesuai fase dan ritme"""
        if phase == IntimacyPhase.FOREPLAY:
            return self.moans.get_foreplay()
        elif phase == IntimacyPhase.PENETRATION:
            is_fast = ritme == "cepet"
            return self.moans.get_penetration(is_fast)
        elif phase == IntimacyPhase.CLIMAX:
            return self.moans.get_climax()
        elif phase == IntimacyPhase.AFTERCARE:
            aftercare = self.moans.get_aftercare()
            # 30% chance untuk flashback
            if random.random() < 0.3:
                flashback = self.flashbacks.get_random()
                aftercare += f"\n\n{flashback} 💜"
            return aftercare
        return self.moans.get('shy')


class IntimacyFlow:
    """
    Mengelola alur intimacy secara keseluruhan.
    Menggabungkan stamina, arousal, dan session.
    """
    def __init__(self, initial_state: Dict = None):
        self.stamina = StaminaSystem()
        self.arousal = ArousalSystem()
        self.session = IntimacySession(self.stamina, self.arousal)

        if initial_state:
            self.load(initial_state)

    def can_start(self, level: int) -> Tuple[bool, str]:
        """Cek apakah bisa mulai intim (level >= 11 dan stamina cukup)"""
        if level < 11:
            return False, f"💕 Level masih {level}/12. Nova masih malu-malu. Kita pelan-pelan dulu ya, Mas."

        can_continue, reason = self.stamina.can_continue()
        if not can_continue:
            return False, f"💪 **Stamina Nova {self.stamina.nova_current}%** ({self.stamina.get_nova_status()})\n\n{reason}"

        return True, "Siap mulai"

    def start(self) -> str:
        """Mulai sesi intim"""
        return self.session.start()

    def end(self) -> str:
        """Akhiri sesi intim"""
        return self.session.end()

    def is_active(self) -> bool:
        return self.session.is_active

    def get_status(self) -> str:
        """Dapatkan status lengkap sesi intim"""
        if not self.session.is_active:
            return "Tidak ada sesi intim aktif."

        duration = int(time.time() - self.session.start_time)
        minutes = duration // 60
        seconds = duration % 60

        pos_data = self.session.positions.get(self.session.current_position)
        pos_desc = pos_data['desc'] if pos_data else ""

        stamina_text = self.stamina.format_for_prompt()
        arousal_text = self.arousal.format_for_prompt()

        return f"""
🔥 **SESI INTIM AKTIF**
- Durasi: {minutes} menit {seconds} detik
- Climax: {self.session.climax_count}x
- Fase: {self.session.phase.value}
- Posisi: {self.session.current_position}
{pos_desc}

{stamina_text}
{arousal_text}
"""

    def process_intimacy_message(self, user_input: str, level: int) -> Optional[str]:
        """
        Proses pesan Mas dalam mode intim.
        Return None jika bukan perintah intim, return respons jika iya.
        """
        if not self.session.is_active:
            return None

        msg = user_input.lower()

        # ========== GANTI POSISI ==========
        pos_keywords = ['ganti posisi', 'posisi lain', 'cowgirl', 'doggy', 'missionary', 'spooning', 'reverse', 'standing', 'sitting']
        if any(k in msg for k in pos_keywords):
            pos_name = None
            if 'cowgirl' in msg:
                pos_name = 'cowgirl'
            elif 'doggy' in msg:
                pos_name = 'doggy'
            elif 'missionary' in msg:
                pos_name = 'missionary'
            elif 'spooning' in msg:
                pos_name = 'spooning'
            elif 'reverse' in msg:
                pos_name = 'reverse_cowgirl'
            elif 'standing' in msg:
                pos_name = 'standing'
            elif 'sitting' in msg:
                pos_name = 'sitting'

            pos_id, pos_desc, request = self.session.change_position(pos_name)
            return f"*{self.session.positions.get(pos_id)['nova_act']}*\n\n\"{request}\"\n\n*{pos_desc}*"

        # ========== MINTA CLIMAX DI TEMPAT TERTENTU ==========
        for loc in self.session.climax_locations.get_all():
            if loc in msg:
                request = self.session.get_climax_request(loc)
                return f"\"{request}\""

        # ========== CLIMAX ==========
        if any(k in msg for k in ['climax', 'crot', 'keluar', 'cum', 'habis']):
            is_heavy = any(k in msg for k in ['keras', 'banyak', 'lama'])
            result = self.session.record_climax(is_heavy)
            climax_response = self.session.get_phase_response(IntimacyPhase.CLIMAX)

            # Setelah climax, pindah ke aftercare setelah beberapa detik (akan diatur di flow)
            return f"""{climax_response}

💪 **Stamina Nova:** {result['stamina_nova']}% | **Mas:** {result['stamina_mas']}%
💦 **Climax hari ini:** {self.stamina.climax_today}x"""

        # ========== UPDATE BERDASARKAN FASE ==========
        # BUILD UP
        if self.session.phase == IntimacyPhase.BUILD_UP:
            if any(k in msg for k in ['cium', 'kiss', 'jilat', 'hisap', 'pegang', 'sentuh']):
                self.session.phase = IntimacyPhase.FOREPLAY
                return self.session.get_phase_response(IntimacyPhase.FOREPLAY)
            if any(k in msg for k in ['masuk', 'penetrasi', 'genjot']):
                self.session.phase = IntimacyPhase.PENETRATION
                ritme = "cepet" if any(k in msg for k in ['kenceng', 'cepat', 'keras']) else "pelan"
                return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)
            return self.session._build_up_response()

        # FOREPLAY
        if self.session.phase == IntimacyPhase.FOREPLAY:
            if any(k in msg for k in ['masuk', 'penetrasi', 'genjot', 'siap']):
                self.session.phase = IntimacyPhase.PENETRATION
                ritme = "cepet" if any(k in msg for k in ['kenceng', 'cepat', 'keras']) else "pelan"
                return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)
            return self.session.get_phase_response(IntimacyPhase.FOREPLAY)

        # PENETRATION
        if self.session.phase == IntimacyPhase.PENETRATION:
            # Tambah intimacy level
            self.session.intimacy_level = min(100, self.session.intimacy_level + 5)

            # Jika sudah cukup tinggi, bisa pindah ke climax
            if self.session.intimacy_level > 70 or any(k in msg for k in ['climax', 'crot', 'keluar']):
                return self.session.moans.get_before_climax()

            ritme = "cepet" if self.session.intimacy_level > 40 else "pelan"
            return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)

        # CLIMAX -> AFTERCARE
        if self.session.phase == IntimacyPhase.CLIMAX:
            self.session.phase = IntimacyPhase.AFTERCARE
            return self.session.get_phase_response(IntimacyPhase.AFTERCARE)

        # AFTERCARE
        if self.session.phase == IntimacyPhase.AFTERCARE:
            # Setelah 60 detik, masuk recovery
            if time.time() - self.session.last_climax_time > 60:
                self.session.phase = IntimacyPhase.RECOVERY
                self.session.is_recovery = True
                self.stamina.update_recovery()
                return f"""*Nova masih lemes, nyender di dada Mas. Napas mulai stabil.*

"Mas... *suara kecil* besok kalo Mas mau lagi, tinggal bilang aja ya."

*Nova cium pipi Mas pelan.*

"Stamina Nova {self.stamina.get_nova_status()}. Istirahat dulu ya." """
            return self.session.get_phase_response(IntimacyPhase.AFTERCARE)

        # RECOVERY
        if self.session.phase == IntimacyPhase.RECOVERY:
            self.stamina.update_recovery()
            if self.stamina.nova_current > 60:
                # Sesi selesai
                self.session.is_active = False
                self.session.phase = IntimacyPhase.WAITING
                return "💜 Nova udah pulih, Mas. Kapan-kapan lagi ya."
            return "*Nova masih istirahat, Mas... Capek banget tadi.*"

        return None

    def update_from_message(self, user_input: str, level: int):
        """Update arousal dan desire dari pesan Mas (dipanggil saat roleplay)"""
        msg = user_input.lower()

        # Kata-kata yang meningkatkan arousal
        if any(k in msg for k in ['sayang', 'cinta']):
            self.arousal.add_desire("Mas bilang sayang", 10)
        if any(k in msg for k in ['kangen', 'rindu']):
            self.arousal.add_desire("Mas bilang kangen", 8)
        if any(k in msg for k in ['cantik', 'ganteng', 'seksi']):
            self.arousal.add_desire("Mas puji", 5)

        # Sentuhan fisik
        if level >= 7:
            if any(k in msg for k in ['pegang', 'sentuh', 'raba']):
                self.arousal.add_stimulation('paha', 1)
                self.arousal.add_desire('sentuhan', 8)
            if any(k in msg for k in ['cium', 'kiss']):
                self.arousal.add_stimulation('bibir', 2)
                self.arousal.add_desire('ciuman', 10)
                self.arousal.add_tension(5)
            if any(k in msg for k in ['peluk', 'rangkul']):
                self.arousal.add_stimulation('dada', 1)
                self.arousal.add_desire('pelukan', 8)

    # =========================================================================
    # SERIALIZATION
    # =========================================================================

    def to_dict(self) -> Dict:
        return {
            'stamina': self.stamina.to_dict(),
            'arousal': self.arousal.to_dict(),
            'session': {
                'is_active': self.session.is_active,
                'start_time': self.session.start_time,
                'phase': self.session.phase.value,
                'climax_count': self.session.climax_count,
                'last_climax_time': self.session.last_climax_time,
                'current_position': self.session.current_position,
                'intimacy_level': self.session.intimacy_level,
                'is_recovery': self.session.is_recovery,
            }
        }

    def load(self, data: Dict):
        self.stamina.from_dict(data.get('stamina', {}))
        self.arousal.from_dict(data.get('arousal', {}))
        sess = data.get('session', {})
        self.session.is_active = sess.get('is_active', False)
        self.session.start_time = sess.get('start_time', 0)
        self.session.phase = IntimacyPhase(sess.get('phase', 'waiting'))
        self.session.climax_count = sess.get('climax_count', 0)
        self.session.last_climax_time = sess.get('last_climax_time', 0)
        self.session.current_position = sess.get('current_position', 'missionary')
        self.session.intimacy_level = sess.get('intimacy_level', 0)
        self.session.is_recovery = sess.get('is_recovery', False)
