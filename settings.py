"""Fruit Ninja: 3D Adventure Edition - Global Settings and Theme Configuration.

Theme: TROPICAL FRUIT ARCADE
Freshness, energy, fun, excitement, and vibrant fruit slicing aesthetics.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
FRUITS_DIR = ASSETS_DIR / "fruits"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts"
DATA_DIR = BASE_DIR / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"

# Display Configuration
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
TITLE = "Fruit Ninja: 3D Adventure Edition"

# ==========================================
# TROPICAL FRUIT ARCADE COLOR PALETTE
# ==========================================
# Primary Theme Colors
TROPICAL_ORANGE   = (255, 140, 50)   # #FF8C32 - Energy, slicing bursts, highlights
MANGO_YELLOW      = (255, 212, 71)   # #FFD447 - Sunshine, gold medals, active highlights
LIME_GREEN        = (155, 207, 83)   # #9BCF53 - Freshness, success badges, nature accents
WATERMELON_PINK   = (255, 85, 119)   # #FF5577 - Punchy accents, alerts, vibrant fruits
TROPICAL_TEAL     = (37, 184, 165)   # #25B8A5 - Cool ocean breeze, secondary buttons, water
CREAM_WHITE       = (255, 245, 223)  # #FFF5DF - Warm soft text, readable UI containers
DEEP_JUNGLE_GREEN = (23, 63, 53)     # #173F35 - Premium depth, backdrop contrast (no black!)

# Atmospheric Sunset & Jungle Gradient Stops
SUNSET_TOP        = (44, 24, 56)     # Warm dusk purple-red
SUNSET_MID        = (198, 76, 58)    # Golden twilight orange
SUNSET_GLOW       = (242, 161, 84)   # Warm horizon haze
JUNGLE_MIST       = (32, 74, 63)     # Subtle canopy depth
JUNGLE_CANOPY     = (18, 48, 40)     # Natural shadow depth

# UI Accents & Shadows
SHADOW_COLOR      = (12, 32, 27, 110)  # Soft natural jungle shadow with alpha
GLOSS_WHITE       = (255, 255, 255, 80) # Button top gloss highlight
UI_BORDER_GOLD    = (255, 225, 120)    # Premium arcade border accent

# Standard Utility Colors
WHITE = (255, 255, 255)
OFF_WHITE = (245, 240, 230)
DARK_GREY = (40, 40, 40)

# ==========================================
# FRUIT COLOR IDENTITIES (3D & PARTICLES)
# ==========================================
FRUIT_COLORS = {
    "watermelon": {
        "rind": (46, 125, 50),
        "flesh": (255, 65, 95),
        "seeds": (30, 20, 20),
        "juice": (255, 85, 119),
        "highlight": (255, 160, 180)
    },
    "mango": {
        "skin": (255, 140, 40),
        "flesh": (255, 200, 45),
        "juice": (255, 180, 30),
        "highlight": (255, 235, 120)
    },
    "orange": {
        "skin": (255, 130, 20),
        "flesh": (255, 165, 30),
        "juice": (255, 140, 50),
        "highlight": (255, 210, 110)
    },
    "lime": {
        "skin": (110, 175, 45),
        "flesh": (160, 220, 75),
        "juice": (155, 207, 83),
        "highlight": (210, 245, 140)
    },
    "dragonfruit": {
        "skin": (230, 45, 100),
        "flesh": (250, 245, 240),
        "seeds": (35, 35, 35),
        "juice": (255, 80, 140),
        "highlight": (255, 180, 210)
    },
    "pineapple": {
        "skin": (180, 130, 30),
        "flesh": (255, 215, 60),
        "juice": (250, 205, 50),
        "highlight": (255, 240, 130)
    },
    "banana": {
        "skin": (255, 215, 60),
        "flesh": (255, 245, 200),
        "juice": (250, 220, 110),
        "highlight": (255, 255, 230)
    },
    "apple": {
        "skin": (225, 45, 45),
        "flesh": (255, 250, 225),
        "seeds": (50, 25, 20),
        "juice": (255, 95, 95),
        "highlight": (255, 175, 175)
    },
    "strawberry": {
        "skin": (235, 40, 65),
        "flesh": (255, 90, 110),
        "seeds": (255, 220, 80),
        "juice": (255, 60, 90),
        "highlight": (255, 160, 180)
    },
    "kiwi": {
        "skin": (115, 80, 45),
        "flesh": (145, 205, 50),
        "seeds": (30, 30, 30),
        "juice": (145, 205, 50),
        "highlight": (210, 245, 130)
    },
    "coconut": {
        "shell": (110, 70, 45),
        "flesh": (250, 248, 245),
        "juice": (240, 245, 250),
        "highlight": (255, 255, 255)
    }
}

# ==========================================
# SCREEN MODES
# ==========================================
MODE_MAIN_MENU     = "MAIN_MENU"
MODE_CLASSIC       = "CLASSIC_GAMEPLAY"
MODE_MISSIONS      = "MISSION_MODE"
MODE_QUIZ          = "FRUIT_QUIZ"
MODE_PUZZLE        = "FRUIT_PUZZLE"
MODE_LEVEL_SELECT  = "LEVEL_SELECTION"
MODE_ACHIEVEMENTS  = "ACHIEVEMENTS"
MODE_SETTINGS      = "SETTINGS"
MODE_GAME_OVER     = "GAME_OVER"
MODE_VICTORY       = "VICTORY"

# ==========================================
# UI DESIGN SYSTEM CONSTANTS
# ==========================================
UI_BUTTON_RADIUS = 18
UI_PANEL_RADIUS = 24
UI_BORDER_WIDTH = 3
UI_FONT_TITLE_SIZE = 48
UI_FONT_SUBTITLE_SIZE = 32
UI_FONT_BODY_SIZE = 22
UI_FONT_SMALL_SIZE = 16

# Game Physics
GRAVITY = 0.38
SWIPE_TRAIL_LENGTH = 12
SWIPE_TIMEOUT = 120  # milliseconds
