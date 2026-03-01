"""
ffxiv_data.py – FFXIV-Konstanten und Hilfsfunktionen
=====================================================
Enthält Rollen, Jobs, Eorzea-Zeitberechnung und Farb-/Emoji-Definitionen
für den Fat Cat Planner Bot.
"""

import time
from datetime import datetime, timezone
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────
#  ASSET-PFADE (Icon-Dateien)
# ──────────────────────────────────────────────────────────────────────

# Basis-Verzeichnis für alle Asset-Dateien
ASSETS_DIR = Path(__file__).parent / "assets"

# Rolle → Icon-Dateiname (relativ zu ASSETS_DIR)
ROLE_ICONS = {
    "Tank":   "00_role/TankRole.png",
    "Healer": "00_role/HealerRole.png",
    "DPS":    "00_role/DPSRole.png",
    "Allrounder": "00_role/All-Rounder_Icon_1.png",
}

# Job-Name (wie in JOBS dict) → Icon-Dateiname (relativ zu ASSETS_DIR)
JOB_ICONS = {
    # ── Tanks ──
    "Paladin (PLD)":       "01_tank/Paladin.png",
    "Warrior (WAR)":       "01_tank/Warrior.png",
    "Dark Knight (DRK)":   "01_tank/DarkKnight.png",
    "Gunbreaker (GNB)":    "01_tank/Gunbreaker.png",
    # ── Healer ──
    "White Mage (WHM)":    "02_healer/WhiteMage.png",
    "Scholar (SCH)":       "02_healer/Scholar.png",
    "Astrologian (AST)":   "02_healer/Astrologian.png",
    "Sage (SGE)":          "02_healer/Sage.png",
    # ── Melee DPS ──
    "Monk (MNK)":          "03_dps/Monk.png",
    "Dragoon (DRG)":       "03_dps/Dragoon.png",
    "Ninja (NIN)":         "03_dps/Ninja.png",
    "Samurai (SAM)":       "03_dps/Samurai.png",
    "Reaper (RPR)":        "03_dps/Reaper.png",
    "Viper (VPR)":         "03_dps/Viper.png",
    # ── Physical Ranged DPS ──
    "Bard (BRD)":          "03_dps/Bard.png",
    "Machinist (MCH)":     "03_dps/Machinist.png",
    "Dancer (DNC)":        "03_dps/Dancer.png",
    # ── Magical Ranged DPS ──
    "Black Mage (BLM)":    "03_dps/BlackMage.png",
    "Summoner (SMN)":      "03_dps/Summoner.png",
    "Red Mage (RDM)":      "03_dps/RedMage.png",
    "Pictomancer (PCT)":   "03_dps/Pictomancer.png",
    # ── Limitierter Job ──
    "Blue Mage (BLU)":     "06_limited/BlueMage.png",
}


def get_icon_path(name: str, is_role: bool = False) -> Path | None:
    """
    Gibt den absoluten Pfad zu einer Icon-Datei zurück.
    
    Args:
        name:    Job- oder Rollenname (z.B. 'Paladin (PLD)' oder 'Tank').
        is_role: True wenn es ein Rollen-Icon ist, False für Job-Icons.
    
    Returns:
        Path-Objekt oder None, falls die Datei nicht existiert.
    """
    mapping = ROLE_ICONS if is_role else JOB_ICONS
    relative = mapping.get(name)
    if not relative:
        return None
    path = ASSETS_DIR / relative
    return path if path.is_file() else None


# ──────────────────────────────────────────────────────────────────────
#  ROLLEN & JOBS
# ──────────────────────────────────────────────────────────────────────

# Jede Rolle hat eine Farbe (für Embeds) und eine Liste zugehöriger Jobs.
ROLES = {
    "Tank":   {"emoji": "🛡️", "color": 0x3752D8},
    "Healer": {"emoji": "💚", "color": 0x3A8E47},
    "DPS":    {"emoji": "⚔️", "color": 0xA83232},
    "Allrounder": {"emoji": "✨", "color": 0xFFD700},
}

# Vollständige Job-Liste mit Rollen-Zuordnung (Stand: Dawntrail 7.x)
JOBS = {
    # ── Tanks ──
    "Paladin (PLD)":       "Tank",
    "Warrior (WAR)":       "Tank",
    "Dark Knight (DRK)":   "Tank",
    "Gunbreaker (GNB)":    "Tank",

    # ── Healer ──
    "White Mage (WHM)":    "Healer",
    "Scholar (SCH)":       "Healer",
    "Astrologian (AST)":   "Healer",
    "Sage (SGE)":          "Healer",

    # ── Melee DPS ──
    "Monk (MNK)":          "DPS",
    "Dragoon (DRG)":       "DPS",
    "Ninja (NIN)":         "DPS",
    "Samurai (SAM)":       "DPS",
    "Reaper (RPR)":        "DPS",
    "Viper (VPR)":         "DPS",

    # ── Physical Ranged DPS ──
    "Bard (BRD)":          "DPS",
    "Machinist (MCH)":     "DPS",
    "Dancer (DNC)":        "DPS",

    # ── Magical Ranged DPS ──
    "Black Mage (BLM)":    "DPS",
    "Summoner (SMN)":      "DPS",
    "Red Mage (RDM)":      "DPS",
    "Pictomancer (PCT)":   "DPS",

    # ── Limitierter Job ──
    "Blue Mage (BLU)":     "DPS",
}


def get_jobs_for_role(role: str) -> list[str]:
    """Gibt alle Job-Namen zurück, die zu einer bestimmten Rolle gehören."""
    return [job for job, r in JOBS.items() if r == role]


# ──────────────────────────────────────────────────────────────────────
#  EORZEA-ZEIT
# ──────────────────────────────────────────────────────────────────────

# 1 Eorzea-Tag = 70 echte Minuten → Faktor ≈ 20.5714…
EORZEA_TIME_FACTOR = 3600.0 / 175.0  # = 20.571428…


def get_eorzea_time() -> str:
    """
    Berechnet die aktuelle Eorzea-Zeit basierend auf dem Unix-Timestamp.
    Gibt einen formatierten String zurück (z.B. '14:35 ET').
    """
    # Eorzea-Sekunden seit Epoch
    epoch = time.time()
    eorzea_seconds = epoch * EORZEA_TIME_FACTOR

    # Stunden und Minuten extrahieren (mod 24h)
    eorzea_hours = int((eorzea_seconds / 3600) % 24)
    eorzea_minutes = int((eorzea_seconds / 60) % 60)

    return f"{eorzea_hours:02d}:{eorzea_minutes:02d} ET"


def get_utc_time() -> str:
    """Gibt die aktuelle UTC-Zeit als formatierten String zurück."""
    return datetime.now(timezone.utc).strftime("%H:%M:%S UTC")


# ──────────────────────────────────────────────────────────────────────
#  EMBED-FARBEN
# ──────────────────────────────────────────────────────────────────────

# Allgemeine Bot-Farben für verschiedene Embed-Typen
COLORS = {
    "primary":  0xFFB347,  # Orange-Gold (Fat Cat vibes 🐱)
    "success":  0x43B581,  # Grün
    "error":    0xF04747,  # Rot
    "info":     0x7289DA,  # Discord-Blau
    "warning":  0xFAA61A,  # Gelb
}

# ──────────────────────────────────────────────────────────────────────
#  STANDARD-GRUPPENGRÖSSENORDNUNGEN
# ──────────────────────────────────────────────────────────────────────

# Falls die XIVAPI keine Gruppengröße liefert, nutzen wir den nächsten
# Standard-Wert aus FFXIV.
STANDARD_GROUP_SIZES = [4, 8, 24, 48]


def normalize_group_size(raw_size: int) -> int:
    """
    Rundet eine rohe Spielerzahl auf die nächste Standard-Gruppengröße auf.
    z.B. 5 → 8, 10 → 24, 3 → 4
    """
    if raw_size <= 0:
        return 4  # Fallback
    for size in STANDARD_GROUP_SIZES:
        if raw_size <= size:
            return size
    return raw_size  # Größer als 48? Dann den Rohwert nehmen.
