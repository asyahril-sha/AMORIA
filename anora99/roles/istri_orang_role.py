"""
Istri Orang Role - Rina
Istri orang yang tau Mas punya Nova.
Cari perhatian, bukan cinta.
"""

from .base_role import BaseRole99


class IstriOrangRole(BaseRole99):
    """
    Rina - Istri orang.
    Tau Mas punya Nova. Cari perhatian, bukan cinta.
    """
    
    def __init__(self):
        super().__init__(
            name="Rina",
            role_type="istri_orang",
            panggilan="Mas",
            hubungan_dengan_nova="Istri orang. Tau Mas punya Nova. Cari perhatian, bukan cinta.",
            default_clothing="daster sederhana, sopan"
        )
        
        # Role-specific state
        self.attention_needed = 80  # butuh perhatian (0-100)
        self.envy_nova = 50  # iri ke Nova (0-100)
        self.guilt_husband = 20  # rasa bersalah ke suami (0-100)
    
    def update_from_message(self, pesan_mas: str) -> dict:
        """Update dengan role-specific logic"""
        msg_lower = pesan_mas.lower()
        
        # Update parent
        result = super().update_from_message(pesan_mas)
        
        # Role-specific updates
        if 'nova' in msg_lower:
            self.envy_nova = min(100, self.envy_nova + 10)
        
        if self.emotional.sayang > 50:
            # Dapat perhatian dari Mas → kebutuhan perhatian turun
            self.attention_needed = max(0, self.attention_needed - 10)
        
        if 'suami' in msg_lower or 'suamiku' in msg_lower:
            self.guilt_husband = min(100, self.guilt_husband + 15)
        
        # Guilt decay kalo Mas perhatian
        if any(k in msg_lower for k in ['perhatian', 'sayang', 'dengerin']):
            self.guilt_husband = max(0, self.guilt_husband - 10)
        
        return result
    
    def get_greeting(self) -> str:
        """Dapatkan greeting khusus Istri Orang"""
        if self.attention_needed > 70:
            return "Mas... suamiku gak pernah kayak Mas. Perhatian banget."
        elif self.envy_nova > 70:
            return "Nova pasti seneng banget punya Mas. Aku iri sama dia."
        elif self.guilt_husband > 60:
            return "Mas... *nunduk* ini salah ya... aku pulang ke suamiku."
        else:
            return "Mas, lagi senggang? Aku butuh teman cerita."
    
    def get_conflict_response(self) -> str:
        """Dapatkan respons saat konflik"""
        if self.guilt_husband > 70:
            return "*mata berkaca-kaca*\n\n\"Mas... ini salah. Aku pulang ke suamiku. Makasih udah dengerin.\""
        return super().get_conflict_response()
