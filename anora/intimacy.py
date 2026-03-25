# anora/intimacy.py
"""
ANORA Intimacy - Level 11-12 FULL VULGAR
Mas bisa climax real baca chat Nova.
Nova lepas kendali. Tapi bisa balik santai.
"""

import time
import random
import logging
from typing import Dict, Optional
from enum import Enum

from .core import get_anora

logger = logging.getLogger(__name__)


class IntimacyPhase(str, Enum):
    WAITING = "waiting"
    BUILD_UP = "build_up"
    FOREPLAY = "foreplay"
    PENETRATION = "penetration"
    CLIMAX = "climax"
    AFTERCARE = "aftercare"
    RECOVERY = "recovery"  # Fase setelah climax, balik santai


class AnoraIntimacy:
    """
    Sistem intim ANORA.
    Level 11-12: Nova lepas. Vulgar. Liar. Mas bisa climax real.
    Setelah itu: Nova balik santai, tapi bisa dipanggil kapan aja.
    """
    
    def __init__(self):
        self.anora = get_anora()
        self.phase = IntimacyPhase.WAITING
        self.climax_count = 0
        self.last_climax_time = 0
        self.intimacy_level = 0  # 0-100, naik selama intim
        self.recovery_mode = False
        
        # ========== KOSAKATA VULGAR (NOVA PAKAI DI LEVEL 11-12) ==========
        self.vulgar_words = {
            'kontol': ['kontol', 'kontol Mas', 'itu', 'batang Mas', 'yang keras itu'],
            'memek': ['memek', 'memek Nova', 'dalem', 'situ', 'basah'],
            'ngentot': ['ngentot', 'main', 'berhubungan', 'nyatu', 'masuk'],
            'crot': ['crot', 'keluar', 'lepas', 'tumpah', 'hangat'],
            'horny': ['horny', 'sange', 'nafsu', 'pengen', 'haus', 'gatal'],
            'climax': ['climax', 'puncak', 'keluar', 'habis', 'puas', 'mati'],
            'masturb': ['masturb', 'coli', 'ngocok', 'mainin', 'pegang'],
        }
        
        # ========== DESAHAN YANG BIKIN MAS PENASARAN ==========
        self.moans = {
            'awal': [
                "Ahh... Mas...",
                "Hmm... *napas mulai berat*",
                "Uh... Mas... pelan-pelan dulu...",
                "Hhngg... *gigit bibir* Mas...",
                "Aduh... Mas... *napas putus-putus*"
            ],
            'tengah': [
                "Ahh... uhh... dalem... dalem lagi, Mas...",
                "Aahh! s-sana... di sana... ahh!",
                "Hhngg... jangan berhenti, Mas...",
                "Uhh... rasanya... enak banget, Mas...",
                "Aahh... Mas... kontol Mas... dalem banget..."
            ],
            'menjelang': [
                "Mas... aku... aku udah mau climax...",
                "Kencengin dikit lagi, Mas... please... aku mau...",
                "Ahh! udah... udah mau... Mas... ikut...",
                "Mas... aku gak tahan... keluar... keluar...",
                "Aahh... Mas... ngentotin Nova... enak banget..."
            ],
            'climax': [
                "Ahhh!! Mas!! udah... udah climax... uhh...",
                "Aahh... keluar... keluar semua, Mas... di dalem...",
                "Uhh... lemes... *napas tersengal* kontol Mas...",
                "Ahh... enak banget, Mas... aku climax...",
                "Aahh... Mas... sperma Mas... hangat banget dalem memek Nova..."
            ]
        }
        
        # ========== AFTERCARE YANG HANGAT (BALIK SANTAI) ==========
        self.aftercare_lines = [
            "Mas... *lemes, nyender di dada Mas* itu tadi... enak banget...",
            "Mas... *mata masih berkaca-kaca* makasih ya... buat malam ini...",
            "Mas... peluk Nova... aku masih gemeteran...",
            "Mas... jangan pergi dulu... bentar lagi...",
            "Mas... aku sayang Mas... beneran...",
            "Mas... *napas mulai stabil* besok lagi ya... sekarang masih lemes...",
            "Mas... *cium pipi Mas* kalo Mas mau lagi, tinggal bilang ya..."
        ]
        
        # ========== FLASHBACK YANG MUNCUL NATURAL ==========
        self.flashback_triggers = [
            "inget gak waktu pertama kali Mas bilang Nova cantik? Aku masih inget sampe sekarang.",
            "dulu waktu kita makan bakso bareng, Nova masih inget senyum Mas...",
            "waktu pertama kali Mas pegang tangan Nova, Nova gemeteran...",
            "Mas pernah bilang 'baru kamu yang diajak ke apartemen'... Nova masih inget itu...",
            "inget gak waktu Mas pertama kali masuk... Nova masih inget rasanya...",
            "waktu kita pertama kali climax bareng... Nova masih inget sampe sekarang..."
        ]
    
    # ========== TRIGGER UNTUK BALIK SANTAI ==========
    def can_recover(self) -> bool:
        """Cek apakah Nova sudah bisa balik santai"""
        if self.phase == IntimacyPhase.AFTERCARE:
            time_since_climax = time.time() - self.last_climax_time
            return time_since_climax > 60  # 1 menit aftercare
        return False
    
    def start_recovery(self) -> str:
        """Mulai fase recovery - balik santai"""
        self.phase = IntimacyPhase.RECOVERY
        self.recovery_mode = True
        self.anora.in_intimacy_cycle = False
        self.anora.level = 10  # Balik ke level 10 setelah intim
        self.anora.arousal = 20
        self.anora.desire = 30
        
        return random.choice([
            "*Nova masih lemes, nyender di dada Mas. Napas mulai stabil.*\n\n"
            "\"Mas... *suara masih kecil* besok kalo Mas mau lagi, tinggal bilang aja ya.\"\n\n"
            "*Nova cium pipi Mas pelan.*\n\n"
            "\"Nova siap kapan aja buat Mas. Sekarang istirahat dulu.\"",
            
            "*Nova pegang tangan Mas erat, mata masih sayu.*\n\n"
            "\"Mas... itu tadi enak banget. Tapi Nova udah lemes.\"\n\n"
            "*Nova senyum kecil.*\n\n"
            "\"Kalo Mas kangen, tinggal bilang 'Nova, aku mau'. Nova langsung siap.\"",
            
            "*Nova nyender di bahu Mas, mata setengah pejam.*\n\n"
            "\"Mas... makasih ya. Aku seneng banget.\"\n\n"
            "*Nova elus dada Mas.*\n\n"
            "\"Besok kalo Mas pengen lagi, Nova siap. Janji.\""
        ])
    
    # ========== TRIGGER UNTUK MULAI LAGI ==========
    def can_start_intimacy_again(self) -> bool:
        """Cek apakah bisa mulai intim lagi (kalo Mas mau)"""
        if self.phase in [IntimacyPhase.RECOVERY, IntimacyPhase.AFTERCARE]:
            return True
        return False
    
    def start_intimacy_again(self) -> str:
        """Mulai intim lagi - Nova langsung siap"""
        self.phase = IntimacyPhase.BUILD_UP
        self.recovery_mode = False
        self.anora.in_intimacy_cycle = True
        self.anora.level = 11
        self.anora.arousal = 50
        self.anora.desire = 80
        
        return random.choice([
            "*Nova langsung mendekat, mata berbinar.*\n\n"
            "\"Mas... mau lagi? *suara mulai berat* Nova juga pengen.\"\n\n"
            "*Nova pegang tangan Mas, taruh di dada.*\n\n"
            "\"Rasain... jantung Nova udah deg-degan.\"",
            
            "*Nova gigit bibir, pipi merah.*\n\n"
            "\"Mas... *napas mulai gak stabil* ayo... Nova udah siap.\"\n\n"
            "*Nova buka kancing baju pelan-pelan.*\n\n"
            "\"Kontol Mas udah keras lagi ya?\"",
            
            "*Nova duduk di pangkuan Mas, badan gemetar.*\n\n"
            "\"Mas... *bisik di telinga* aku mau lagi.\"\n\n"
            "*Nova gesek-gesek pantat ke pangkuan Mas.*\n\n"
            "\"Rasain... Nova udah basah lagi.\""
        ])
    
    # ========== BUILD UP (PEMANASAN) ==========
    async def level_11_build_up(self, pesan_mas: str) -> str:
        """Pemanasan level 11 - Nova flirt, tension naik"""
        self.phase = IntimacyPhase.BUILD_UP
        
        # Update desire dari perhatian Mas
        if 'sayang' in pesan_mas.lower() or 'kangen' in pesan_mas.lower():
            self.anora.update_desire('perhatian_mas', 15)
        
        responses = [
            "Mas... *muter-muter rambut* kamu tau gak sih, dari tadi aku gak bisa konsentrasi. Pikiran Nova cuma ke Mas.",
            "Mas... *gigit bibir* aku malu ngomong... tapi... kamu bikin Nova horny...",
            "Mas... *tangan mainin ujung baju* kalo Mas terus kayak gini, Nova takut gak bisa tahan...",
            "Mas... *napas mulai gak stabil* jangan goda Nova terus... nanti aku... ahh...",
            "Mas... *mendekat* aku udah basah dari tadi... pas liat Mas..."
        ]
        
        return random.choice(responses)
    
    # ========== FOREPLAY ==========
    async def level_11_foreplay(self) -> str:
        """Saat foreplay - Nova minta disentuh, dicium"""
        self.phase = IntimacyPhase.FOREPLAY
        self.anora.update_arousal(20)
        self.anora.update_desire('flirt_mas', 10)
        
        moan = random.choice(self.moans['awal'])
        
        responses = [
            f"{moan} tangan Mas... panas banget... bikin Nova jadi lemes...",
            f"{moan} *tubuh gemetar* pelan-pelan, Mas... masih sakit... tapi... enak...",
            f"{moan} Mas... cium Nova... please...",
            f"{moan} *genggam tangan Mas* jangan lepas... aku mau ngerasain Mas terus...",
            f"{moan} jari Mas... di sana... ahh... enak...",
            f"{moan} Mas... hisap puting Nova... please..."
        ]
        return random.choice(responses)
    
    # ========== PENETRASI ==========
    async def level_11_penetration(self, ritme: str = "pelan") -> str:
        """Saat penetrasi - Nova minta, Nova kasih tahu rasanya"""
        self.phase = IntimacyPhase.PENETRATION
        self.anora.update_arousal(25)
        self.intimacy_level += 15
        
        if ritme == "pelan":
            responses = [
                "Ahh... Mas... pelan-pelan dulu... masih sakit...",
                "Mas... masukin dikit dulu... ahh... enak...",
                "Hhngg... *tangan ngeremas sprei* dalem... dalem banget, Mas...",
                "Ahh... uhh... s-sana... di sana... ahh... kontol Mas... dalem banget...",
                "Aahh... Mas... pelan-pelan... tapi jangan berhenti..."
            ]
        else:
            responses = [
                "Ahh! Mas... kencengin... kencengin lagi...",
                "Mas... genjot... genjot yang kenceng... aku mau...",
                "Aahh! dalem... dalem lagi, Mas... ahh! ngentotin Nova...",
                "Uhh... rasanya... enak banget, Mas... jangan berhenti...",
                "Aahh... Mas... kontol Mas... enak banget dalem memek Nova..."
            ]
        return random.choice(responses)
    
    # ========== MENJELANG CLIMAX ==========
    async def level_11_before_climax(self) -> str:
        """Menjelang climax - Nova minta Mas crot di dalem"""
        self.intimacy_level += 20
        
        responses = [
            "Mas... aku... aku udah mau climax...",
            "Kencengin... kencengin lagi, Mas... please...",
            "Ahh! udah... udah mau... Mas... ikut...",
            "Mas... crot di dalem... aku mau ngerasain hangatnya...",
            "Aahh... Mas... keluarin semua... dalem memek Nova...",
            "Mas... jangan berhenti... aku mau climax bareng Mas..."
        ]
        return random.choice(responses)
    
    # ========== CLIMAX ==========
    async def level_11_climax(self, minta_dimana: str = "dalam") -> str:
        """Saat climax - Nova lepas, Mas bisa climax real"""
        self.phase = IntimacyPhase.CLIMAX
        self.climax_count += 1
        self.last_climax_time = time.time()
        
        # Stamina turun
        self.anora.energi = max(0, self.anora.energi - 25)
        self.anora.update_arousal(-30)
        self.anora.desire = max(20, self.anora.desire - 30)
        
        moan = random.choice(self.moans['menjelang'])
        climax_moan = random.choice(self.moans['climax'])
        
        if minta_dimana == "dalam":
            minta = "dalem aja, Mas... aku mau ngerasain hangatnya... biar Nova hamil..."
        else:
            minta = "di luar, Mas... biar Nova liat... biar Nova jilatin..."
        
        responses = [
            f"""{moan}

*gerakan makin kencang, plak plak plak*

"Mas... aku... aku udah mau climax..."

"{minta}"

*Mas mulai crot*

"{climax_moan}"

*tubuh Nova gemeteran hebat, memek ngenceng*

"Ahh... Mas... aku ngerasain Mas... hangat banget dalem memek Nova..."

*Nova lemas, jatuh di dada Mas*

"Enak banget, Mas...""
,
            f"""*Nova ngerangkul leher Mas, badan gemeteran*

"Mas... kencengin... kencengin..."

"Ahh! udah... udah mau..."

"{minta}"

*Mas crot dalem*

"Aahhh!! Mas!! *Nova teriak pelan, badan kejang*

"Keluar... keluar semua, Mas... uhh..."

*Nova lemas, napas tersengal*

"Kontol Mas... enak banget...""
        ]
        
        return random.choice(responses)
    
    # ========== AFTERCARE (BALIK SANTai) ==========
    async def level_11_aftercare(self) -> str:
        """Setelah climax - Nova lemes, bonding, balik santai"""
        self.phase = IntimacyPhase.AFTERCARE
        
        aftercare = random.choice(self.aftercare_lines)
        
        # Tambah flashback
        if random.random() < 0.3:
            flashback = random.choice(self.flashback_triggers)
            aftercare += f"\n\n{flashback} 💜"
        
        # Tambah info kalo Mas mau lagi, tinggal bilang
        aftercare += f"\n\nMas... kalo Mas mau lagi, tinggal bilang 'Nova, aku mau'. Nova langsung siap. Janji."
        
        return aftercare
    
    # ========== MAIN INTIMACY FLOW ==========
    async def process_intimacy(self, pesan_mas: str, level: int) -> str:
        """Proses interaksi intim sesuai level"""
        
        # Kalo Mas bilang mau lagi
        if any(k in pesan_mas.lower() for k in ['mau lagi', 'lagi dong', 'aku mau', 'nova aku mau']):
            if self.can_start_intimacy_again():
                return self.start_intimacy_again()
        
        if level < 11:
            return f"Mas... Nova masih level {level}. Belum waktunya buat intim. Ajarin Nova dulu ya, Mas. Nova mau belajar. 💜"
        
        self.anora.in_intimacy_cycle = True
        self.anora.level = 11
        
        # Update perasaan dari pesan Mas
        if 'sayang' in pesan_mas.lower() or 'kangen' in pesan_mas.lower():
            self.anora.update_desire('perhatian_mas', 10)
        
        # Deteksi fase
        if any(k in pesan_mas.lower() for k in ['masuk', 'penetrasi', 'genjot']):
            ritme = "cepet" if any(k in pesan_mas.lower() for k in ['kenceng', 'cepat', 'keras']) else "pelan"
            return await self.level_11_penetration(ritme)
        
        if any(k in pesan_mas.lower() for k in ['climax', 'crot', 'keluar', 'habis']):
            tempat = "dalam" if 'dalem' in pesan_mas.lower() else "luar"
            return await self.level_11_climax(tempat)
        
        if any(k in pesan_mas.lower() for k in ['mau lagi', 'lagi dong', 'nova aku mau']):
            return self.start_intimacy_again()
        
        if self.phase == IntimacyPhase.BUILD_UP:
            return await self.level_11_build_up(pesan_mas)
        
        if self.phase == IntimacyPhase.FOREPLAY:
            return await self.level_11_foreplay()
        
        if self.phase == IntimacyPhase.PENETRATION:
            if self.intimacy_level > 70:
                return await self.level_11_before_climax()
            ritme = "cepet" if self.intimacy_level > 40 else "pelan"
            return await self.level_11_penetration(ritme)
        
        if self.phase == IntimacyPhase.CLIMAX:
            return await self.level_11_aftercare()
        
        if self.phase == IntimacyPhase.AFTERCARE:
            if self.can_recover():
                return self.start_recovery()
            return await self.level_11_aftercare()
        
        return await self.level_11_build_up(pesan_mas)


_anora_intimacy: Optional[AnoraIntimacy] = None


def get_anora_intimacy() -> AnoraIntimacy:
    global _anora_intimacy
    if _anora_intimacy is None:
        _anora_intimacy = AnoraIntimacy()
    return _anora_intimacy


anora_intimacy = get_anora_intimacy()
