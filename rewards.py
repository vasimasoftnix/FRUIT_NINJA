"""Fruit Ninja: 3D Adventure Edition - Achievements and Rewards System.

Implements:
- 8 Core Achievements with tracking and persistent storage
- Animated Achievement Unlock Notification Banner
- Dedicated Rewards Screen with Tropical Arcade styling and Star balance
"""

import pygame
import settings
from menu import FruitArcadeButton, TropicalBackground, get_font
from progress import ProgressManager
from audio import get_audio


ACHIEVEMENTS_DATA = [
    {
        "id": "first_slice",
        "title": "First Slice",
        "desc": "Slice your very first tropical fruit.",
        "stars": 5,
        "icon": "watermelon"
    },
    {
        "id": "fruit_beginner",
        "title": "Fruit Beginner",
        "desc": "Slice a total of 50 fruits across all modes.",
        "stars": 5,
        "icon": "orange"
    },
    {
        "id": "combo_master",
        "title": "Combo Master",
        "desc": "Perform a delicious 3x or higher fruit combo.",
        "stars": 5,
        "icon": "banana"
    },
    {
        "id": "bomb_dodger",
        "title": "Bomb Dodger",
        "desc": "Slice 25 fruits in a single game without detonating bombs.",
        "stars": 10,
        "icon": "lime"
    },
    {
        "id": "score_hunter",
        "title": "Score Hunter",
        "desc": "Accumulate 100 points in a single slicing game.",
        "stars": 10,
        "icon": "pineapple"
    },
    {
        "id": "fruit_expert",
        "title": "Fruit Expert",
        "desc": "Score 10 or more correct answers in the Fruit Quiz.",
        "stars": 10,
        "icon": "mango"
    },
    {
        "id": "mission_champion",
        "title": "Mission Champion",
        "desc": "Successfully conquer at least 5 adventure missions.",
        "stars": 15,
        "icon": "strawberry"
    },
    {
        "id": "ultimate_ninja",
        "title": "Ultimate Ninja",
        "desc": "Unlock and master Level 5 in Adventure Mode.",
        "stars": 20,
        "icon": "dragonfruit"
    }
]


class AchievementBanner:
    """Sliding notification banner that appears at top of screen when an achievement unlocks."""

    def __init__(self, width: int = settings.WINDOW_WIDTH):
        self.width = width
        self.active_banner = None
        self.timer = 0
        self.duration = 180  # ~3 seconds
        self.font_title = get_font(18, bold=True)
        self.font_desc = get_font(14, bold=True)

    def trigger(self, title: str, stars: int):
        self.active_banner = {"title": title, "stars": stars}
        self.timer = self.duration
        get_audio().play("achievement")

    def update(self):
        if self.timer > 0:
            self.timer -= 1
            if self.timer <= 0:
                self.active_banner = None

    def draw(self, surface: pygame.Surface):
        if not self.active_banner:
            return

        # Calculate slide offset
        progress = self.timer / self.duration
        if progress > 0.85:
            # Slide in
            t = (1.0 - progress) / 0.15
            y = int(-70 + t * 90)
        elif progress < 0.15:
            # Slide out
            t = progress / 0.15
            y = int(-70 + t * 90)
        else:
            y = 20

        bw, bh = 420, 62
        bx = (self.width - bw) // 2
        rect = pygame.Rect(bx, y, bw, bh)

        # Soft drop shadow
        s_rect = rect.copy()
        s_rect.y += 5
        shadow = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (10, 25, 20, 150), (0, 0, bw, bh), border_radius=16)
        surface.blit(shadow, s_rect.topleft)

        # Main Banner Body
        banner_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(banner_surf, (23, 63, 53, 250), (0, 0, bw, bh), border_radius=16)
        pygame.draw.rect(banner_surf, settings.MANGO_YELLOW, (0, 0, bw, bh), width=2, border_radius=16)
        surface.blit(banner_surf, rect.topleft)

        # Golden Trophy badge
        pygame.draw.circle(surface, settings.MANGO_YELLOW, (bx + 34, y + bh // 2), 18)
        pygame.draw.circle(surface, settings.TROPICAL_ORANGE, (bx + 34, y + bh // 2), 15)

        # Text
        head = self.font_title.render(f"ACHIEVEMENT UNLOCKED! +{self.active_banner['stars']} STARS", True, settings.MANGO_YELLOW)
        name = self.font_desc.render(self.active_banner["title"], True, settings.CREAM_WHITE)
        surface.blit(head, (bx + 62, y + 10))
        surface.blit(name, (bx + 62, y + 33))


class AchievementsScreen:
    """Displays the list of unlocked achievements and available rewards."""

    def __init__(self, screen: pygame.Surface, progress_mgr: ProgressManager):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.progress_mgr = progress_mgr

        self.background = TropicalBackground(self.width, self.height)
        self.font_header = get_font(38, bold=True)
        self.font_title = get_font(20, bold=True)
        self.font_desc = get_font(14, bold=False)
        self.font_status = get_font(15, bold=True)

        self.btn_back = FruitArcadeButton(
            pygame.Rect(40, 25, 170, 44),
            "< BACK",
            base_color=settings.TROPICAL_TEAL,
            accent_color=settings.LIME_GREEN,
            font_size=18,
            action_id="BACK"
        )

    def handle_event(self, event: pygame.event.Event) -> str:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            get_audio().play("click")
            return "BACK"
        action = self.btn_back.handle_event(event)
        if action == "BACK":
            get_audio().play("click")
            return "BACK"
        return ""

    def update(self):
        self.btn_back.update()

    def draw(self):
        self.background.draw(self.screen)

        # Header Title
        title_surf = self.font_header.render("TROPHY & REWARD ROOM", True, settings.MANGO_YELLOW)
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 28))

        # Star Counter in Top Right
        stars = self.progress_mgr.data.get("stars_earned", 0)
        star_pill = pygame.Rect(self.width - 200, 25, 160, 44)
        pygame.draw.rect(self.screen, (20, 50, 40), star_pill, border_radius=16)
        pygame.draw.rect(self.screen, settings.MANGO_YELLOW, star_pill, width=2, border_radius=16)
        star_txt = self.font_title.render(f"STARS: {stars}", True, settings.MANGO_YELLOW)
        self.screen.blit(star_txt, (star_pill.centerx - star_txt.get_width() // 2, star_pill.centery - star_txt.get_height() // 2))

        # Back button
        self.btn_back.draw(self.screen)

        # Grid of Achievements (2 columns x 4 rows)
        col_w = 440
        row_h = 100
        start_x = (self.width - (col_w * 2 + 30)) // 2
        start_y = 100

        unlocked_set = set(self.progress_mgr.data.get("unlocked_achievements", []))

        for idx, ach in enumerate(ACHIEVEMENTS_DATA):
            col = idx % 2
            row = idx // 2
            x = start_x + col * (col_w + 30)
            y = start_y + row * (row_h + 16)

            is_unlocked = ach["id"] in unlocked_set

            # Card Container
            card_rect = pygame.Rect(x, y, col_w, row_h)
            card_surf = pygame.Surface((col_w, row_h), pygame.SRCALPHA)

            if is_unlocked:
                pygame.draw.rect(card_surf, (26, 75, 62, 230), (0, 0, col_w, row_h), border_radius=16)
                pygame.draw.rect(card_surf, settings.UI_BORDER_GOLD, (0, 0, col_w, row_h), width=2, border_radius=16)
            else:
                pygame.draw.rect(card_surf, (18, 42, 35, 190), (0, 0, col_w, row_h), border_radius=16)
                pygame.draw.rect(card_surf, (40, 70, 60), (0, 0, col_w, row_h), width=2, border_radius=16)

            self.screen.blit(card_surf, card_rect.topleft)

            # Left Badge Circle
            badge_color = settings.MANGO_YELLOW if is_unlocked else (45, 65, 55)
            pygame.draw.circle(self.screen, badge_color, (x + 36, y + row_h // 2), 22)
            badge_symbol = "OK" if is_unlocked else "--"
            sym_surf = self.font_status.render(badge_symbol, True, (15, 35, 25) if is_unlocked else settings.CREAM_WHITE)
            self.screen.blit(sym_surf, (x + 36 - sym_surf.get_width() // 2, y + row_h // 2 - sym_surf.get_height() // 2))

            # Achievement Info
            t_color = settings.MANGO_YELLOW if is_unlocked else (180, 180, 180)
            title = self.font_title.render(ach["title"], True, t_color)
            self.screen.blit(title, (x + 72, y + 16))

            desc = self.font_desc.render(ach["desc"], True, settings.CREAM_WHITE if is_unlocked else (140, 150, 145))
            self.screen.blit(desc, (x + 72, y + 44))

            # Reward Tag
            status_str = f"UNLOCKED (+{ach['stars']})" if is_unlocked else f"LOCKED ({ach['stars']} Stars)"
            status_col = settings.LIME_GREEN if is_unlocked else settings.WATERMELON_PINK
            status_txt = self.font_status.render(status_str, True, status_col)
            self.screen.blit(status_txt, (x + 72, y + 70))
