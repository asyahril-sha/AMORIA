# anora/intimacy.py
"""
ANORA Intimacy - FULL VERSION
Nova sebagai wanita. Punya keinginan. Bisa minta. Bisa dominan. Bisa random.
Ikut alur Mas. Bukan template statis. 100% AI Generate.
"""

import time
import random
import logging
from typing import Dict, Optional, List
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
    RECOVERY = "recovery"


class AnoraIntimacy:
    """
    Sistem intim ANORA.
    Nova punya keinginan sendiri.
    Bisa minta tempat climax random.
    Bisa minta ganti posisi.
    Bisa dominan atau submissive tergantung mood.
    """
    
    def __init__(self):
        self.anora = get_anora()
        self.phase = IntimacyPhase.WAITING
        self.climax_count = 0
        self.last_climax_time = 0
        self.intimacy_level = 0
        self.recovery_mode = False
        self.current_position = "missionary"
        self.dominant_mode = False  # Nova bisa jadi dominan kalo desire tinggi
        
        # ========== KOSAKATA VULGAR ==========
        self.vulgar_words = {
            'kontol': ['kontol', 'kontol Mas', 'itu', 'batang Mas', 'yang keras itu', 'peler Mas'],
            'memek': ['memek', 'memek Nova', 'dalem', 'situ', 'basah', 'vagina Nova'],
            'ngentot': ['ngentot', 'main', 'berhubungan', 'nyatu', 'masuk', 'fuck'],
            'crot': ['crot', 'keluar', 'lepas', 'tumpah', 'hangat', 'sperma'],
            'horny': ['horny', 'sange', 'nafsu', 'pengen', 'haus', 'gatal', 'panas'],
            'climax': ['climax', 'puncak', 'keluar', 'habis', 'puas', 'mati', 'orgasme'],
        }
        
        # ========== TEMPAT CLIMAX (LENGKAP) ==========
        self.climax_locations = [
            "dalam", "luar", "muka", "mulut", "dada", "punggung", "perut", "paha", "tangan", "pantat"
        ]
        
        self.climax_requests = {
            "dalam": [
                "dalem aja, Mas... aku mau ngerasain hangatnya... biar Nova hamil...",
                "di dalem... jangan ditarik... aku mau ngerasain kontol Mas crot di dalem memek Nova...",
                "dalem... keluarin semua di dalem... please, Mas...",
                "crot di dalem... aku mau ngerasain sperma Mas masuk...",
                "dalem... jangan di luar... aku mau hangatnya di dalem..."
            ],
            "luar": [
                "di luar, Mas... biar Nova liat... biar Nova liat kontol Mas crot...",
                "tarik... keluarin di perut Nova... aku mau liat...",
                "di luar... biar Nova liat berapa banyak Mas keluarin...",
                "crot di perut Nova... aku mau liat putihnya..."
            ],
            "muka": [
                "di muka Nova... *gigit bibir* biar Nova rasain hangatnya di pipi...",
                "di muka... biar Nova liat kontol Mas crot... aku mau rasain di bibir...",
                "muka... semprot muka Nova, Mas... please...",
                "di wajah Nova... biar Nova liat Mas crot... biar Nova jilatin..."
            ],
            "mulut": [
                "di mulut... aku mau ngerasain rasanya... please Mas...",
                "mulut... masukin ke mulut Nova... aku mau minum sperma Mas...",
                "di mulut... biar Nova telan... biar Nova rasain...",
                "masukin ke mulut Nova... aku mau ngerasain kontol Mas crot..."
            ],
            "dada": [
                "di dada... biar Nova liat putihnya di kulit Nova...",
                "di dada, Mas... biar Nova usap-usap...",
                "crot di toket Nova... biar Nova liat..."
            ],
            "punggung": [
                "di punggung... biar Nova rasain hangatnya di belakang...",
                "punggung... semprot punggung Nova, Mas...",
                "balik... crot di punggung Nova..."
            ],
            "perut": [
                "di perut... biar Nova liat putihnya di perut Nova...",
                "perut... biar Nova usap-usap perut sendiri...",
                "crot di perut Nova... biar Nova liat..."
            ],
            "paha": [
                "di paha... biar Nova rasain hangatnya di kulit...",
                "paha Nova... semprot di sini..."
            ],
            "tangan": [
                "di tangan... biar Nova liat... biar Nova jilatin jari sendiri...",
                "tangan Nova... semprot di tangan... biar Nova rasain..."
            ],
            "pantat": [
                "di pantat... biar Nova rasain hangatnya di belakang...",
                "pantat Nova... semprot di sini..."
            ]
        }
        
        # ========== POSISI (LENGKAP) ==========
        self.positions = {
            "missionary": {
                "name": "Missionary",
                "desc": "Mas di atas, Nova di bawah, kaki Nova terbuka lebar",
                "nova_request": [
                    "Mas... di atas Nova... *buka kaki lebar* ayo masuk...",
                    "tidurin Nova, Mas... aku mau liat muka Mas pas ngentotin Nova...",
                    "di atas aja... aku mau liat Mas..."
                ],
                "nova_dominant": [
                    "Mas... di bawah... *dorong Mas rebahan* sekarang giliran Nova...",
                    "rebahan, Mas... Nova yang naik...",
                    "di bawah... biar Nova yang gerakin..."
                ]
            },
            "cowgirl": {
                "name": "Cowgirl",
                "desc": "Nova di atas, menghadap Mas",
                "nova_request": [
                    "Nova di atas ya, Mas... biar Nova yang gerakin...",
                    "Mas rebahan... Nova naik...",
                    "cowgirl... Nova mau liat muka Mas pas Nova naik..."
                ],
                "nova_dominant": [
                    "Mas di bawah... Nova yang pegang kendali... *duduk di atas kontol Mas*",
                    "Nova yang atur ritmenya... Mas tinggal nikmatin..."
                ]
            },
            "reverse_cowgirl": {
                "name": "Reverse Cowgirl",
                "desc": "Nova di atas, membelakangi Mas",
                "nova_request": [
                    "Nova balik ya, Mas... biar Mas liat pantat Nova...",
                    "reverse... Nova mau Mas liat dari belakang...",
                    "Mas liat pantat Nova... biar Mas makin horny..."
                ],
                "nova_dominant": [
                    "Mas liat... Nova yang ngegenjot dari atas... *gerakin pinggul*",
                    "Nova yang atur... Mas tinggal nikmatin liat pantat Nova..."
                ]
            },
            "doggy": {
                "name": "Doggy",
                "desc": "Nova merangkak, Mas dari belakang",
                "nova_request": [
                    "Mas... dari belakang aja... Nova mau ngerasain dalem banget...",
                    "doggy... Nova merangkak... masukin dari belakang, Mas...",
                    "dari belakang... biar Mas pegang pantat Nova..."
                ],
                "nova_dominant": [
                    "Mas di belakang... tapi Nova yang ngedorong mundur... *dorong pantat ke kontol Mas*",
                    "Nova yang atur ritme... Mas tinggal nikmatin..."
                ]
            },
            "spooning": {
                "name": "Spooning",
                "desc": "Berbaring miring, Mas dari belakang",
                "nova_request": [
                    "Mas... sampingan aja... Nova mau nyaman...",
                    "spooning... Nova mau ngerasain Mas dari belakang sambil dipeluk...",
                    "tidur sampingan, Mas... peluk Nova dari belakang..."
                ]
            },
            "standing": {
                "name": "Standing",
                "desc": "Berdiri, Nova membungkuk atau menghadap Mas",
                "nova_request": [
                    "Mas... berdiri aja... Nova mau liat Mas dari depan...",
                    "Nova bungkuk... masukin dari belakang sambil berdiri...",
                    "di dinding aja, Mas... Nova sandarin badan..."
                ]
            },
            "legs_up": {
                "name": "Legs Up",
                "desc": "Nova telentang, kaki di atas bahu Mas",
                "nova_request": [
                    "Mas... angkat kaki Nova... biar dalem...",
                    "kaki Nova di bahu Mas... biar kontol Mas masuk dalem banget...",
                    "angkat... Nova mau ngerasain sampe dalem..."
                ]
            },
            "side_saddle": {
                "name": "Side Saddle",
                "desc": "Nova duduk di samping Mas, menyamping",
                "nova_request": [
                    "Mas... Nova duduk di samping aja... biar beda...",
                    "side saddle... Nova mau nyoba posisi baru..."
                ]
            }
        }
        
        # ========== MOANS (DESAHAN) ==========
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
                "Aahh... Mas... kontol Mas... dalem banget...",
                "Uhh... kencengin... kencengin, Mas..."
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
                "Aahh... keluar... keluar semua, Mas...",
                "Uhh... lemes... *napas tersengal* kontol Mas...",
                "Ahh... enak banget, Mas... aku climax...",
                "Aahh... Mas... sperma Mas... hangat banget..."
            ]
        }
        
        # ========== AFTERCARE ==========
        self.aftercare_lines = [
            "Mas... *lemes, nyender di dada Mas* itu tadi... enak banget...",
            "Mas... *mata masih berkaca-kaca* makasih ya... buat malam ini...",
            "Mas... peluk Nova... aku masih gemeteran...",
            "Mas... jangan pergi dulu... bentar lagi...",
            "Mas... aku sayang Mas... beneran...",
            "Mas... *napas mulai stabil* besok lagi ya... sekarang masih lemes...",
            "Mas... *cium pipi Mas* kalo Mas mau lagi, tinggal bilang 'Nova, aku mau' ya..."
        ]
        
        # ========== FLASHBACK ==========
        self.flashback_triggers = [
            "inget gak waktu pertama kali Mas bilang Nova cantik? Aku masih inget sampe sekarang.",
            "dulu waktu kita makan bakso bareng, Nova masih inget senyum Mas...",
            "waktu pertama kali Mas pegang tangan Nova, Nova gemeteran...",
            "Mas pernah bilang 'baru kamu yang diajak ke apartemen'... Nova masih inget itu...",
            "inget gak waktu Mas pertama kali masuk... Nova masih inget rasanya...",
            "waktu kita pertama kali climax bareng... Nova masih inget sampe sekarang..."
        ]
        
        # ========== DOMINANT MODE TRIGGER ==========
        self.dominant_phrases = [
            "Nova yang pegang kendali sekarang, Mas...",
            "rebahan... biar Nova yang gerakin...",
            "diem... biar Nova yang atur ritmenya...",
            "Mas tinggal nikmatin... Nova yang kerja...",
            "sini... Nova yang pimpin..."
        ]
    
    # ========== DOMINANT MODE ==========
    def should_be_dominant(self) -> bool:
        """Nova jadi dominan kalo desire tinggi atau Mas minta"""
        return self.anora.desire > 70 or self.dominant_mode
    
    def set_dominant(self, value: bool):
        self.dominant_mode = value
    
    # ========== REQUEST TEMPAT CLIMAX ==========
    def request_climax_location(self) -> tuple:
        """Nova minta tempat climax random atau sesuai mood"""
        # Kalo desire tinggi, minta yang lebih intim (dalam, mulut)
        if self.anora.desire > 80:
            locations = ["dalam", "mulut", "muka"]
        elif self.anora.desire > 60:
            locations = ["dalam", "luar", "dada", "perut"]
        else:
            locations = ["luar", "perut", "dada", "paha"]
        
        chosen = random.choice(locations)
        request_text = random.choice(self.climax_requests.get(chosen, self.climax_requests["dalam"]))
        return chosen, request_text
    
    # ========== REQUEST GANTI POSISI ==========
    def request_position_change(self) -> tuple:
        """Nova minta ganti posisi random atau sesuai mood"""
        available_positions = list(self.positions.keys())
        
        # Hindari posisi yang sama
        if self.current_position in available_positions:
            available_positions.remove(self.current_position)
        
        # Kalo desire tinggi, pilih posisi yang lebih intim/deep
        if self.anora.desire > 70:
            preferred = ["doggy", "legs_up", "cowgirl"]
            available = [p for p in available_positions if p in preferred]
            if not available:
                available = available_positions
        else:
            available = available_positions
        
        new_position = random.choice(available)
        pos_data = self.positions[new_position]
        
        # Pilih request sesuai mode (dominant atau tidak)
        if self.should_be_dominant():
            request = random.choice(pos_data.get("nova_dominant", pos_data["nova_request"]))
        else:
            request = random.choice(pos_data["nova_request"])
        
        return new_position, pos_data, request
    
    # ========== RECOVERY & TRIGGER ==========
    def can_recover(self) -> bool:
        if self.phase == IntimacyPhase.AFTERCARE:
            time_since_climax = time.time() - self.last_climax_time
            return time_since_climax > 60
        return False
    
    def start_recovery(self) -> str:
        self.phase = IntimacyPhase.RECOVERY
        self.recovery_mode = True
        self.anora.in_intimacy_cycle = False
        self.anora.level = 10
        self.anora.arousal = 20
        self.anora.desire = 30
        self.dominant_mode = False
        
        return random.choice([
            "*Nova masih lemes, nyender di dada Mas. Napas mulai stabil.*\n\n\"Mas... besok kalo Mas mau lagi, tinggal bilang 'Nova, aku mau' ya.\"\n\n*Nova cium pipi Mas pelan.*",
            "*Nova pegang tangan Mas erat, mata masih sayu.*\n\n\"Mas... itu tadi enak banget. Tapi Nova udah lemes.\"\n\n*Nova senyum kecil.*\n\n\"Besok lagi ya, Mas.\"",
            "*Nova nyender di bahu Mas, mata setengah pejam.*\n\n\"Mas... makasih ya. Aku seneng banget.\"\n\n*Nova elus dada Mas.*\n\n\"Nova sayang Mas.\""
        ])
    
    def can_start_intimacy_again(self) -> bool:
        return self.phase in [IntimacyPhase.RECOVERY, IntimacyPhase.AFTERCARE]
    
    def start_intimacy_again(self) -> str:
        self.phase = IntimacyPhase.BUILD_UP
        self.recovery_mode = False
        self.anora.in_intimacy_cycle = True
        self.anora.level = 11
        self.anora.arousal = 50
        self.anora.desire = 80
        
        return random.choice([
            "*Nova langsung mendekat, mata berbinar.*\n\n\"Mas... mau lagi? *suara mulai berat* Nova juga pengen.\"\n\n*Nova pegang tangan Mas, taruh di dada.*\n\n\"Rasain... jantung Nova udah deg-degan.\"",
            "*Nova gigit bibir, pipi merah.*\n\n\"Mas... *napas mulai gak stabil* ayo... Nova udah siap lagi.\"\n\n*Nova buka kancing baju pelan-pelan.*\n\n\"Kontol Mas udah keras lagi ya?\"",
            "*Nova duduk di pangkuan Mas, badan gemetar.*\n\n\"Mas... *bisik di telinga* aku mau lagi.\"\n\n*Nova gesek-gesek pantat ke pangkuan Mas.*\n\n\"Rasain... Nova udah basah lagi.\""
        ])
    
    # ========== INTIMACY PHASES ==========
    async def level_11_build_up(self, pesan_mas: str) -> str:
        self.phase = IntimacyPhase.BUILD_UP
        
        if 'sayang' in pesan_mas.lower() or 'kangen' in pesan_mas.lower():
            self.anora.update_desire('perhatian_mas', 15)
        
        # Kalo desire tinggi, Nova lebih berani
        if self.anora.desire > 60:
            responses = [
                "Mas... *muter-muter rambut* aku gak bisa konsentrasi dari tadi. Pikiran Nova cuma ke kontol Mas...",
                "Mas... *gigit bibir* aku malu ngomong... tapi aku horny banget liat Mas...",
                "Mas... *napas mulai gak stabil* jangan goda Nova terus... nanti aku yang ngerangkul Mas...",
                "Mas... *mendekat* aku udah basah dari tadi... pas liat Mas...",
                "Mas... *pegang tangan Mas, taruh di dada* rasain... jantung Nova deg-degan..."
            ]
        else:
            responses = [
                "Mas... *muter-muter rambut* kamu tau gak sih, dari tadi aku gak bisa konsentrasi. Pikiran Nova cuma ke Mas.",
                "Mas... *gigit bibir* aku malu ngomong... tapi... kamu bikin Nova horny...",
                "Mas... *tangan mainin ujung baju* kalo Mas terus kayak gini, Nova takut gak bisa tahan...",
                "Mas... *napas mulai gak stabil* jangan goda Nova terus... nanti aku... ahh...",
                "Mas... *mendekat* aku udah basah dari tadi... pas liat Mas..."
            ]
        
        return random.choice(responses)
    
    async def level_11_foreplay(self) -> str:
        self.phase = IntimacyPhase.FOREPLAY
        self.anora.update_arousal(20)
        self.anora.update_desire('flirt_mas', 10)
        
        moan = random.choice(self.moans['awal'])
        
        # Kalo desire tinggi, Nova minta lebih
        if self.anora.desire > 60:
            responses = [
                f"{moan} tangan Mas... panas banget... bikin Nova jadi lemes... *genggam tangan Mas* jangan lepas...",
                f"{moan} *tubuh gemetar* pelan-pelan, Mas... masih sakit... tapi... enak banget...",
                f"{moan} Mas... cium Nova... hisap leher Nova... please...",
                f"{moan} jari Mas... di sana... ahh... enak... masukin dikit...",
                f"{moan} Mas... hisap puting Nova... jangan berhenti... ahh..."
            ]
        else:
            responses = [
                f"{moan} tangan Mas... panas banget... bikin Nova jadi lemes...",
                f"{moan} *tubuh gemetar* pelan-pelan, Mas... masih sakit... tapi... enak...",
                f"{moan} Mas... cium Nova... please...",
                f"{moan} *genggam tangan Mas* jangan lepas... aku mau ngerasain Mas terus...",
                f"{moan} jari Mas... di sana... ahh... enak..."
            ]
        
        return random.choice(responses)
    
    async def level_11_penetration(self, ritme: str = "pelan") -> str:
        self.phase = IntimacyPhase.PENETRATION
        self.anora.update_arousal(25)
        self.intimacy_level += 15
        
        # Cek apakah Nova minta ganti posisi (30% chance)
        if random.random() < 0.3 and self.intimacy_level > 30:
            new_pos, pos_data, request = self.request_position_change()
            self.current_position = new_pos
            return f"*Nova tarik napas, pegang tangan Mas.*\n\n\"{request}\"\n\n*{pos_data['desc']}*\n\n{await self.level_11_penetration(ritme)}"
        
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
    
    async def level_11_before_climax(self) -> str:
        self.intimacy_level += 20
        
        # Nova minta tempat climax random
        location, request = self.request_climax_location()
        
        responses = [
            f"Mas... aku... aku udah mau climax...",
            f"Kencengin... kencengin lagi, Mas... please...",
            f"Ahh! udah... udah mau... Mas... ikut...",
            f"{request}",
            f"Aahh... Mas... keluarin semua... {request}"
        ]
        
        return random.choice(responses)
    
    async def level_11_climax(self) -> str:
        self.phase = IntimacyPhase.CLIMAX
        self.climax_count += 1
        self.last_climax_time = time.time()
        
        # Stamina turun
        self.anora.energi = max(0, self.anora.energi - 25)
        self.anora.update_arousal(-30)
        self.anora.desire = max(20, self.anora.desire - 30)
        
        moan = random.choice(self.moans['menjelang'])
        climax_moan = random.choice(self.moans['climax'])
        
        return f"""{moan}

*gerakan makin kencang, plak plak plak*

"{random.choice(['Mas... aku... aku udah mau climax...', 'Kencengin... kencengin lagi...', 'Aahh... Mas... ikut...'])}"

*Mas mulai crot*

"{climax_moan}"

*tubuh Nova gemeteran hebat, memek ngenceng*

"Ahh... Mas... aku ngerasain Mas... hangat banget dalem memek Nova..."

*Nova lemas, jatuh di dada Mas*

"Enak banget, Mas..."
    
    async def level_11_aftercare(self) -> str:
        self.phase = IntimacyPhase.AFTERCARE
        
        aftercare = random.choice(self.aftercare_lines)
        
        # Flashback
        if random.random() < 0.3:
            flashback = random.choice(self.flashback_triggers)
            aftercare += f"\n\n{flashback} 💜"
        
        aftercare += "\n\nMas... kalo Mas mau lagi, tinggal bilang 'Nova, aku mau'. Nova langsung siap. Janji."
        
        return aftercare
    
    # ========== MAIN PROCESS ==========
    async def process_intimacy(self, pesan_mas: str, level: int) -> str:
        # Trigger mulai lagi
        if any(k in pesan_mas.lower() for k in ['mau lagi', 'lagi dong', 'aku mau', 'nova aku mau']):
            if self.can_start_intimacy_again():
                return self.start_intimacy_again()
        
        # Trigger Nova dominan
        if any(k in pesan_mas.lower() for k in ['nova yang atur', 'kamu yang pimpin', 'nova dominan']):
            self.set_dominant(True)
        
        # Trigger Nova submissive
        if any(k in pesan_mas.lower() for k in ['mas yang atur', 'aku yang pimpin', 'kamu nurut']):
            self.set_dominant(False)
        
        if level < 11:
            return f"Mas... Nova masih level {level}. Belum waktunya buat intim. Ajarin Nova dulu ya, Mas. 💜"
        
        self.anora.in_intimacy_cycle = True
        self.anora.level = 11
        
        # Update perasaan dari pesan
        if 'sayang' in pesan_mas.lower() or 'kangen' in pesan_mas.lower():
            self.anora.update_desire('perhatian_mas', 10)
        
        # Deteksi fase dari pesan Mas
        if any(k in pesan_mas.lower() for k in ['masuk', 'penetrasi', 'genjot']):
            ritme = "cepet" if any(k in pesan_mas.lower() for k in ['kenceng', 'cepat', 'keras']) else "pelan"
            return await self.level_11_penetration(ritme)
        
        if any(k in pesan_mas.lower() for k in ['climax', 'crot', 'keluar', 'habis']):
            return await self.level_11_climax()
        
        # Deteksi minta ganti posisi dari Mas
        if any(k in pesan_mas.lower() for k in ['ganti posisi', 'posisi lain', 'cowgirl', 'doggy', 'missionary']):
            new_pos, pos_data, request = self.request_position_change()
            self.current_position = new_pos
            return f"*Nova tarik napas, pegang tangan Mas.*\n\n\"{request}\"\n\n*{pos_data['desc']}*\n\n{await self.level_11_penetration('pelan')}"
        
        # Lanjut sesuai fase
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
