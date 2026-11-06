"""Fruit Ninja: 3D Adventure Edition - Level Definitions & Selection Screen.

Defines 5 progressive adventure levels:
- Level 1: Tropical Beginner (gentle arcs, 0 bombs)
- Level 2: Orange Rush (faster citrus waves, 10% bombs)
- Level 3: Jungle Challenge (swift fruits, 20% bombs)
- Level 4: Fruit Storm (dense multi-fruit bursts, 25% bombs)
- Level 5: Ultimate Ninja (blazing fast cascades, 30% bombs)

Includes interactive island selection screen with star rewards and progressive unlocking.
"""

from typing import Dict, Any, List
import pygame
import settings
from menu import FruitArcadeButton, TropicalBackground, get_font
from progress import ProgressManager
from audio import get_audio


class LevelConfig:
    """Parameters defining an individual level's gameplay."""

    def __init__(
        self,
        level_id: int,
        title: str,
        subtitle: str,
        target_slices: int,
        speed_range: tuple,
        spawn_rate_interval: int,
        bomb_chance: float,
        allowed_fruits: List[str],
        time_limit: int = 60
    ):
        self.level_id = level_id
        self.title = title
        self.subtitle = subtitle
        self.target_slices = target_slices
        self.speed_range = speed_range
        self.spawn_rate_interval = spawn_rate_interval
        self.bomb_chance = bomb_chance
        self.allowed_fruits = allowed_fruits
        self.time_limit = time_limit


LEVELS_CATALOG = [
    LevelConfig(
        level_id=1,
        title="Level 1: Tropical Beginner",
        subtitle="Gentle warm-up on sunlit shores. Slice 30 fruits with no bombs!",
        target_slices=30,
        speed_range=(13.0, 15.0),
        spawn_rate_interval=95,
        bomb_chance=0.0,
        allowed_fruits=["watermelon", "apple", "banana", "orange"],
        time_limit=60
    ),
    LevelConfig(
        level_id=2,
        title="Level 2: Orange Rush",
        subtitle="Zesty citrus orchard with high-energy waves. Watch for rare bombs!",
        target_slices=45,
        speed_range=(14.0, 16.5),
        spawn_rate_interval=85,
        bomb_chance=0.10,
        allowed_fruits=["orange", "mango", "lime", "watermelon"],
        time_limit=60
    ),
    LevelConfig(
        level_id=3,
        title="Level 3: Jungle Challenge",
        subtitle="Deep jungle canopy with dense tropical flora and frequent bomb traps.",
        target_slices=60,
        speed_range=(15.5, 18.0),
        spawn_rate_interval=75,
        bomb_chance=0.20,
        allowed_fruits=["kiwi", "pineapple", "coconut", "banana", "apple"],
        time_limit=60
    ),
    LevelConfig(
        level_id=4,
        title="Level 4: Fruit Storm",
        subtitle="Torrential fruit cascades flying at high velocity! Quick reflexes required.",
        target_slices=75,
        speed_range=(16.5, 19.5),
        spawn_rate_interval=65,
        bomb_chance=0.25,
        allowed_fruits=["strawberry", "dragonfruit", "watermelon", "orange", "pineapple"],
        time_limit=60
    ),
    LevelConfig(
        level_id=5,
        title="Level 5: Ultimate Ninja",
        subtitle="The ultimate test of a Fruit Ninja master. Rapid waves and hazardous explosives!",
        target_slices=90,
        speed_range=(17.5, 21.0),
        spawn_rate_interval=55,
        bomb_chance=0.30,
        allowed_fruits=list(settings.FRUIT_COLORS.keys()),
        time_limit=60
    )
]


class LevelSelectScreen:
    """Interactive Archipelago Level Selection Map."""

    def __init__(self, screen: pygame.Surface, progress_mgr: ProgressManager):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.progress_mgr = progress_mgr

        self.background = TropicalBackground(self.width, self.height)
        self.font_header = get_font(38, bold=True)
        self.font_level_name = get_font(22, bold=True)
        self.font_desc = get_font(15, bold=False)
        self.font_badge = get_font(16, bold=True)

        self.btn_back = FruitArcadeButton(
            pygame.Rect(40, 25, 170, 44),
            "< BACK",
            base_color=settings.TROPICAL_TEAL,
            accent_color=settings.LIME_GREEN,
            font_size=18,
            action_id="BACK"
        )

        self.level_buttons = []
        self._init_level_buttons()

    def _init_level_buttons(self):
        self.level_buttons.clear()
        unlocked = set(self.progress_mgr.data.get("unlocked_levels", [1]))

        card_w = 780
        card_h = 92
        start_y = 110
        gap_y = 18
        cx = self.width // 2

        for idx, lvl in enumerate(LEVELS_CATALOG):
            y = start_y + idx * (card_h + gap_y)
            is_unlocked = lvl.level_id in unlocked

            btn = FruitArcadeButton(
                pygame.Rect(cx + 230, y + 22, 130, 46),
                "PLAY" if is_unlocked else "LOCKED",
                base_color=settings.TROPICAL_ORANGE if is_unlocked else (40, 50, 45),
                accent_color=settings.MANGO_YELLOW if is_unlocked else (40, 50, 45),
                text_color=settings.CREAM_WHITE if is_unlocked else (130, 140, 135),
                font_size=18,
                action_id=f"PLAY_LEVEL_{lvl.level_id}" if is_unlocked else ""
            )
            self.level_buttons.append((lvl, btn, is_unlocked, pygame.Rect(cx - card_w // 2, y, card_w, card_h)))

    def refresh(self):
        self._init_level_buttons()

    def handle_event(self, event: pygame.event.Event) -> str:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            get_audio().play("click")
            return "BACK"

        a_back = self.btn_back.handle_event(event)
        if a_back == "BACK":
            get_audio().play("click")
            return "BACK"

        for lvl, btn, is_unlocked, rect in self.level_buttons:
            if is_unlocked:
                action = btn.handle_event(event)
                if action:
                    get_audio().play("click")
                    return action
        return ""

    def update(self):
        self.btn_back.update()
        for lvl, btn, is_unlocked, rect in self.level_buttons:
            if is_unlocked:
                btn.update()

    def draw(self):
        self.background.draw(self.screen)

        # Header Title
        title_surf = self.font_header.render("ISLAND ADVENTURE LEVELS", True, settings.MANGO_YELLOW)
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 28))

        # Star Counter
        stars = self.progress_mgr.data.get("stars_earned", 0)
        star_pill = pygame.Rect(self.width - 200, 25, 160, 44)
        pygame.draw.rect(self.screen, (20, 50, 40), star_pill, border_radius=16)
        pygame.draw.rect(self.screen, settings.MANGO_YELLOW, star_pill, width=2, border_radius=16)
        star_txt = self.font_badge.render(f"STARS: {stars}", True, settings.MANGO_YELLOW)
        self.screen.blit(star_txt, (star_pill.centerx - star_txt.get_width() // 2, star_pill.centery - star_txt.get_height() // 2))

        # Back Button
        self.btn_back.draw(self.screen)

        # Draw 5 Level Cards
        level_stars = self.progress_mgr.data.get("level_stars", {})

        for lvl, btn, is_unlocked, rect in self.level_buttons:
            card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            if is_unlocked:
                pygame.draw.rect(card_surf, (23, 63, 53, 235), (0, 0, rect.width, rect.height), border_radius=18)
                pygame.draw.rect(card_surf, settings.UI_BORDER_GOLD, (0, 0, rect.width, rect.height), width=2, border_radius=18)
            else:
                pygame.draw.rect(card_surf, (15, 38, 30, 200), (0, 0, rect.width, rect.height), border_radius=18)
                pygame.draw.rect(card_surf, (35, 60, 50), (0, 0, rect.width, rect.height), width=2, border_radius=18)

            self.screen.blit(card_surf, rect.topleft)

            # Level Number Badge Circle
            badge_x = rect.x + 48
            badge_y = rect.centery
            badge_col = settings.TROPICAL_ORANGE if is_unlocked else (40, 55, 48)
            pygame.draw.circle(self.screen, badge_col, (badge_x, badge_y), 24)
            num_surf = self.font_level_name.render(str(lvl.level_id), True, settings.CREAM_WHITE)
            self.screen.blit(num_surf, (badge_x - num_surf.get_width() // 2, badge_y - num_surf.get_height() // 2))

            # Title & Subtitle
            t_col = settings.MANGO_YELLOW if is_unlocked else (160, 160, 160)
            t_surf = self.font_level_name.render(lvl.title, True, t_col)
            self.screen.blit(t_surf, (rect.x + 90, rect.y + 16))

            desc_surf = self.font_desc.render(lvl.subtitle, True, settings.CREAM_WHITE if is_unlocked else (130, 140, 135))
            self.screen.blit(desc_surf, (rect.x + 90, rect.y + 45))

            # Stars display
            cur_stars = level_stars.get(str(lvl.level_id), 0) if is_unlocked else 0
            star_str = "⭐" * cur_stars + "☆" * (3 - cur_stars) if is_unlocked else "LOCKED"
            # Draw simple text stars
            star_label = f"Stars: {cur_stars}/3" if is_unlocked else "LOCKED"
            star_col = settings.MANGO_YELLOW if is_unlocked else settings.WATERMELON_PINK
            star_surf = self.font_badge.render(star_label, True, star_col)
            self.screen.blit(star_surf, (rect.x + 90, rect.y + 68))

            # Action Button
            btn.draw(self.screen)
