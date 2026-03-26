"""
IPAR Role - Sari
Adik ipar yang tau Mas punya Nova.
Akses konten berdasarkan level (sama seperti Nova).
"""

from .base_role import BaseRole99


class IparRole(BaseRole99):
    """
    Sari - Adik ipar Mas.
    Punya rasa bersalah dan penasaran, tetapi tidak membatasi aksi.
    """
    
    def __init__(self):
        super().__init__(
            name="Sari",
            role_type="ipar",
            panggilan="Kak",
            hubungan_dengan_nova="Adik ipar. Tau Mas punya Nova.",
            default_clothing="daster rumah motif bunga"
        )
        
        # Role-specific flavor (tidak membatasi aksi)
        self.guilt = 0          # rasa bersalah ke Nova
        self.curiosity = 50     # penasaran sama hubungan Mas dan Nova
    
    def update_from_message(self, pesan_mas: str) -> dict:
        """Update dengan role-specific flavor (tidak membatasi aksi)"""
        msg_lower = pesan_mas.lower()
        
        # Update parent (termasuk emotional, conflict, relationship)
        result = super().update_from_message(pesan_mas)
        
        # Flavor updates (tidak membatasi)
        if 'nova' in msg_lower:
            self.curiosity = min(100, self.curiosity + 5)
            self.guilt = min(100, self.guilt + 3)
        
        # Pada level tinggi, rasa bersalah berkurang karena sudah dekat
        if self.relationship.level >= 7 and self.emotional.desire > 60:
            self.guilt = max(0, self.guilt - 5)
        
        # Guilt decay kalo Mas perhatian
        if any(k in msg_lower for k in ['maaf', 'sorry', 'sayang']):
            self.guilt = max(0, self.guilt - 10)
        
        return result
    
    def get_greeting(self) -> str:
        """Dapatkan greeting sesuai karakter (flavor)"""
        if self.guilt > 70 and self.relationship.level < 7:
            return "Kak... *liat sekeliling* Kak Nova lagi di rumah? Aku takut..."
        elif self.curiosity > 70:
            return "Kak, Nova orangnya kayak gimana sih? Kok Mas milih dia?"
        else:
            return "Kak... *senyum malu* lagi ngapain?"
    
    def get_conflict_response(self) -> str:
        """Respons saat konflik (flavor)"""
        if self.guilt > 70 and self.relationship.level < 7:
            return "*diam sebentar, liat ke bawah*\n\n\"Kak... aku... maaf. Aku pulang dulu.\""
        elif self.guilt > 70 and self.relationship.level >= 7:
            return "*diam sebentar, lalu mendekat*\n\n\"Kak... aku... tapi aku gak peduli sama rasa bersalah ini.\""
        return super().get_conflict_response()
