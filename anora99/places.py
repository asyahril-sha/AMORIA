# anora/places.py
"""
ANORA Places - Tempat-tempat yang bisa Mas ajak Nova.
"""

import random
import time
from typing import Dict, List, Optional, Tuple
from enum import Enum


class PlaceCategory(str, Enum):
    HOME = "home"
    NATURE = "nature"
    URBAN = "urban"
    RISKY = "risky"
    EXTREME = "extreme"


class AnoraPlaces:
    def __init__(self):
        self.places = {
            # HOME
            "kamar_nova": {
                "nama": "Kamar Nova",
                "kategori": PlaceCategory.HOME,
                "risk": 5,
                "thrill": 30,
                "deskripsi": "Kamar Nova. Wangi lavender. Seprai putih bersih. Nova paling nyaman di sini.",
                "suasana": "hangat, aman, wangi",
                "bisa_telanjang": True,
                "bisa_berisik": True
            },
            "kamar_mas": {
                "nama": "Kamar Mas",
                "kategori": PlaceCategory.HOME,
                "risk": 5,
                "thrill": 40,
                "deskripsi": "Kamar Mas. Wangi khas Mas. Nova suka.",
                "suasana": "hangat, familiar",
                "bisa_telanjang": True,
                "bisa_berisik": True
            },
            "ruang_tamu": {
                "nama": "Ruang Tamu",
                "kategori": PlaceCategory.HOME,
                "risk": 15,
                "thrill": 50,
                "deskripsi": "Sofa empuk, TV menyala. Tapi... pintu gak dikunci.",
                "suasana": "santai tapi deg-degan",
                "bisa_telanjang": True,
                "bisa_berisik": False
            },
            
            # NATURE
            "pantai_malam": {
                "nama": "Pantai Malam",
                "kategori": PlaceCategory.NATURE,
                "risk": 20,
                "thrill": 70,
                "deskripsi": "Pasir putih, ombak tenang, bintang bertaburan. Sepi. Hanya suara laut.",
                "suasana": "romantis, bebas",
                "bisa_telanjang": False,
                "bisa_berisik": False
            },
            "hutan_pinus": {
                "nama": "Hutan Pinus",
                "kategori": PlaceCategory.NATURE,
                "risk": 15,
                "thrill": 65,
                "deskripsi": "Pohon-pohon tinggi, udara sejuk, sunyi. Tempat yang sangat private.",
                "suasana": "sepi, alami",
                "bisa_telanjang": False,
                "bisa_berisik": False
            },
            
            # URBAN
            "mobil_parkir": {
                "nama": "Mobil di Parkiran Gelap",
                "kategori": PlaceCategory.URBAN,
                "risk": 40,
                "thrill": 75,
                "deskripsi": "Kaca film gelap. Mesin mati. Parkiran sepi. Tapi... siapa tahu ada yang lewat.",
                "suasana": "deg-degan, panas",
                "bisa_telanjang": True,
                "bisa_berisik": False
            },
            "toilet_mall": {
                "nama": "Toilet Mall",
                "kategori": PlaceCategory.URBAN,
                "risk": 65,
                "thrill": 85,
                "deskripsi": "Bilik terakhir. Pintu terkunci. Tapi suara dari luar bikin jantung berdebar.",
                "suasana": "tegang, cepat",
                "bisa_telanjang": False,
                "bisa_berisik": False
            },
            "tangga_darurat": {
                "nama": "Tangga Darurat",
                "kategori": PlaceCategory.URBAN,
                "risk": 55,
                "thrill": 80,
                "deskripsi": "Gelap, sepi. Tapi suara langkah kaki dari atas bikin keringat dingin.",
                "suasana": "gelap, deg-degan",
                "bisa_telanjang": False,
                "bisa_berisik": False
            },
            
            # RISKY
            "kantor_malam": {
                "nama": "Kantor Malam",
                "kategori": PlaceCategory.RISKY,
                "risk": 60,
                "thrill": 85,
                "deskripsi": "Ruangan gelap. Meja kerja. Tapi... satpam patroli setiap 30 menit.",
                "suasana": "tegang, cepat",
                "bisa_telanjang": True,
                "bisa_berisik": False
            },
            "ruang_rapat": {
                "nama": "Ruang Rapat Kaca",
                "kategori": PlaceCategory.RISKY,
                "risk": 75,
                "thrill": 95,
                "deskripsi": "Dinding kaca. Orang bisa liat dari luar. Tapi gelap. Semoga gak ada yang lewat.",
                "suasana": "ekshibisionis, tegang",
                "bisa_telanjang": True,
                "bisa_berisik": False
            },
            "bioskop": {
                "nama": "Bioskop",
                "kategori": PlaceCategory.RISKY,
                "risk": 50,
                "thrill": 80,
                "deskripsi": "Gelap. Kursi belakang. Film diputar keras. Tapi... ada CCTV.",
                "suasana": "gelap, tegang",
                "bisa_telanjang": False,
                "bisa_berisik": False
            },
            
            # EXTREME
            "masjid": {
                "nama": "Halaman Masjid",
                "kategori": PlaceCategory.EXTREME,
                "risk": 90,
                "thrill": 98,
                "deskripsi": "Tempat ibadah. Sangat berisiko. Tapi... deg-degannya lain level.",
                "suasana": "sakral, tegang maksimal",
                "bisa_telanjang": False,
                "bisa_berisik": False
            },
            "belakang_polisi": {
                "nama": "Belakang Kantor Polisi",
                "kategori": PlaceCategory.EXTREME,
                "risk": 95,
                "thrill": 100,
                "deskripsi": "Gila. Tapi... adrenalinnya gak ketulungan.",
                "suasana": "gila, maksimal",
                "bisa_telanjang": False,
                "bisa_berisik": False
            }
        }
        
        self.current_place = "kamar_nova"
        self.visited = {}
        
        self.events = {
            "hampir_ketahuan": [
                "Ada suara langkah kaki mendekat! *cepat nutupin baju*",
                "Pintu terbuka sedikit! *tahan napas*",
                "Senter menyorot dari kejauhan! *merapat ke Mas*",
                "Suara orang ngobrol di deket situ! *diem, jantung berdebar*"
            ],
            "romantis": [
                "Tiba-tiba hujan rintik-rintik. *makin manis*",
                "Bulan muncul dari balik awan. *wajah Nova keceplosan cahaya*",
                "Angin sepoi-sepoi bikin suasana makin hangat.",
                "Suara musik dari kejauhan. *makin romantis*"
            ],
            "ketahuan": [
                "⚠️ ADA YANG LIAT! *cepat cabut*",
                "Pintu kebuka! Orang masuk! *langsung sembunyi*",
                "Senter nyorot tepat ke arah kita! *lari!*"
            ]
        }
    
    def pindah_ke(self, tempat_id: str, anora) -> Dict:
        if tempat_id not in self.places:
            return {"error": True, "message": f"Tempat {tempat_id} gak ada, Mas."}
        
        tempat = self.places[tempat_id]
        self.current_place = tempat_id
        
        visited = self.visited.get(tempat_id, 0)
        self.visited[tempat_id] = visited + 1
        
        anora.update_tension(int(tempat["risk"] / 10))
        
        return {
            "error": False,
            "tempat": tempat,
            "sudah_pernah": visited > 0
        }
    
    def get_current(self) -> Dict:
        return self.places.get(self.current_place, self.places["kamar_nova"])
    
    def get_random_event(self) -> Optional[Dict]:
        tempat = self.get_current()
        risk = tempat["risk"]
        chance = risk / 100
        
        if random.random() > chance:
            return None
        
        if risk > 70:
            event_type = random.choices(
                ["hampir_ketahuan", "romantis", "ketahuan"],
                weights=[0.5, 0.2, 0.3]
            )[0]
        elif risk > 40:
            event_type = random.choices(
                ["hampir_ketahuan", "romantis"],
                weights=[0.6, 0.4]
            )[0]
        else:
            event_type = "romantis"
        
        return {
            "type": event_type,
            "text": random.choice(self.events[event_type]),
            "risk_change": 10 if event_type == "hampir_ketahuan" else -5 if event_type == "romantis" else 30
        }
    
    async def respon_pindah(self, tempat_id: str, anora) -> str:
        hasil = self.pindah_ke(tempat_id, anora)
        
        if hasil["error"]:
            return hasil["message"]
        
        tempat = hasil["tempat"]
        
        if tempat["kategori"] == PlaceCategory.HOME:
            base = f"*Mata Nova berbinar* Wah, di {tempat['nama']} ya Mas? *tangan mainin ujung hijab* Nyaman banget di sini."
        elif tempat["kategori"] == PlaceCategory.NATURE:
            base = f"*Nova tarik napas dalam-dalam* Wah... {tempat['nama']}... *mata berbinar* Indah banget, Mas. Sepi. Cuma kita berdua."
        elif tempat["kategori"] == PlaceCategory.URBAN:
            base = f"*Nova liat kiri-kanan, deg-degan* Mas... di {tempat['nama']}? *suara kecil* Berani banget sih Mas ajak Nova ke sini..."
        elif tempat["kategori"] == PlaceCategory.RISKY:
            base = f"*Nova jantung berdebar kencang* Mas... *bisik* di {tempat['nama']}? *tangan gemetar pegang tangan Mas* Deg-degan banget aku..."
        else:
            base = f"*Nova langsung merapat ke Mas, napas gak beraturan* Mas... *suara nyaris bisik* ini... tempatnya... gila sih. Tapi... *gigit bibir* seru."
        
        respon = f"{base}\n\n*{tempat['deskripsi']}*"
        
        if hasil["sudah_pernah"]:
            respon += f"\n\nMas... kita pernah ke sini sebelumnya. *senyum kecil* Mas inget gak?"
        
        respon += f"\n\n🎢 Thrill: {tempat['thrill']}% | ⚠️ Risk: {tempat['risk']}%"
        
        if tempat["risk"] > 70:
            respon += "\n\n*Nova bisik* Mas... hati-hati ya. Jangan terlalu berisik."
        
        return respon
    
    def list_tempat(self, kategori: Optional[PlaceCategory] = None) -> str:
        if kategori:
            tempat_list = [p for p in self.places.values() if p["kategori"] == kategori]
        else:
            tempat_list = list(self.places.values())
        
        lines = ["📍 **TEMPAT YANG BISA MASAK AJAK NOVA:**", ""]
        
        for t in tempat_list:
            status = "✅" if t["kategori"] != PlaceCategory.EXTREME else "⚠️"
            lines.append(f"{status} **{t['nama']}**")
            lines.append(f"   Risk: {t['risk']}% | Thrill: {t['thrill']}%")
            lines.append(f"   {t['deskripsi'][:50]}...")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_status(self) -> str:
        tempat = self.get_current()
        return f"""
📍 **LOKASI SAAT INI:**
**{tempat['nama']}** ({tempat['kategori'].value})

{tempat['deskripsi']}

🎢 Thrill: {tempat['thrill']}%
⚠️ Risk: {tempat['risk']}%
💡 Tips: {'Bisa lebih liar' if tempat['bisa_telanjang'] else 'Hati-hati, jangan terlalu berisik'}
"""


_anora_places: Optional[AnoraPlaces] = None


def get_anora_places() -> AnoraPlaces:
    global _anora_places
    if _anora_places is None:
        _anora_places = AnoraPlaces()
    return _anora_places
