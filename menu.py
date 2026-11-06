"""Fruit Ninja: 3D Adventure Edition - Main Menu, Settings Screen, & UI System.

Implements:
- Main Menu with clean, emoji-free typography and 2.5D fruit icons
- Settings Screen (Music/SFX volumes, toggles, difficulty, display mode, save/reset)
- Tropical Sunset Atmosphere, floating fruit showcase, and ambient foliage
- Reusable FruitArcadeButton with glossy 2.5D specular finish, drop shadows, and hover animations
"""

import math
import random
import pygame
import settings
from particles import ParticleManager
from fruit import FruitSpriteCache
from progress import ProgressManager
from audio import get_audio


def get_font(size: int, bold: bool = True) -> pygame.font.Font:
    """Returns a bold, playful tropical arcade font with robust fallbacks."""
    font_candidates = ["segoe uiblack", "arialblack", "impact", "trebuchetms", "verdana"]
    for font_name in font_candidates:
        f = pygame.font.match_font(font_name, bold=bold)
        if f:
            try:
                return pygame.font.Font(f, size)
            except Exception:
                pass
    return pygame.font.SysFont("arial", size, bold=bold)


class FruitArcadeButton:
    """Rounded fruit-inspired button with glossy specular sheen, drop shadow, and smooth hover animation."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        base_color=settings.TROPICAL_ORANGE,
        accent_color=settings.MANGO_YELLOW,
        text_color=settings.CREAM_WHITE,
        font_size: int = 22,
        action_id: str = "",
        icon_type: str = None
    ):
        self.base_rect = pygame.Rect(rect)
        self.current_rect = pygame.Rect(rect)
        self.text = text
        self.base_color = base_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.font_size = font_size
        self.action_id = action_id
        self.icon_type = icon_type

        self.font = get_font(font_size, bold=True)
        self.hover_progress = 0.0
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> str:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.base_rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.base_rect.collidepoint(event.pos):
                get_audio().play("click")
                return self.action_id
        return ""

    def update(self):
        target = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * 0.25
        expand = int(self.hover_progress * 4)
        self.current_rect = self.base_rect.inflate(expand * 2, expand * 2)

    def draw(self, surface: pygame.Surface):
        r = self.current_rect
        radius = settings.UI_BUTTON_RADIUS

        # 1. Soft Jungle Shadow
        shadow_rect = r.copy()
        shadow_rect.y += 5
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf,
            (12, 32, 27, 130),
            (0, 0, shadow_rect.width, shadow_rect.height),
            border_radius=radius
        )
        surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))

        # 2. Main Button Body
        t = self.hover_progress
        body_color = (
            int(self.base_color[0] * (1 - t) + self.accent_color[0] * t),
            int(self.base_color[1] * (1 - t) + self.accent_color[1] * t),
            int(self.base_color[2] * (1 - t) + self.accent_color[2] * t),
        )
        pygame.draw.rect(surface, body_color, r, border_radius=radius)

        # 3. Top Specular Gloss Highlight
        gloss_height = max(8, r.height // 2 - 2)
        gloss_surf = pygame.Surface((r.width - 4, gloss_height), pygame.SRCALPHA)
        gloss_rect = pygame.Rect(0, 0, r.width - 4, gloss_height)
        pygame.draw.rect(gloss_surf, (255, 255, 255, 75), gloss_rect, border_top_left_radius=radius - 2, border_top_right_radius=radius - 2)
        surface.blit(gloss_surf, (r.x + 2, r.y + 2))

        # 4. Golden Rim Border
        border_col = settings.UI_BORDER_GOLD if self.hover_progress > 0.4 else settings.CREAM_WHITE
        border_width = 3 if self.hover_progress > 0.5 else 2
        pygame.draw.rect(surface, border_col, r, width=border_width, border_radius=radius)

        # 5. Icon if provided
        icon_offset_x = 0
        if self.icon_type:
            icon_surf = FruitSpriteCache.get_whole_surface(self.icon_type, radius=16)
            icon_rect = icon_surf.get_rect(midleft=(r.x + 16, r.centery))
            surface.blit(icon_surf, icon_rect)
            icon_offset_x = 14

        # 6. Button Text with Shadow
        text_surf = self.font.render(self.text, True, self.text_color)
        shadow_text = self.font.render(self.text, True, (20, 45, 35))

        text_pos = (r.centerx - text_surf.get_width() // 2 + icon_offset_x, r.centery - text_surf.get_height() // 2)
        surface.blit(shadow_text, (text_pos[0] + 2, text_pos[1] + 2))
        surface.blit(text_surf, text_pos)


class TropicalBackground:
    """Renders the warm sunset gradient, sun glow, and lush jungle canopy silhouette."""

    def __init__(self, width: int = settings.WINDOW_WIDTH, height: int = settings.WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.gradient_surface = self._create_gradient()
        self.canopy_surface = self._create_canopy()

    def _create_gradient(self) -> pygame.Surface:
        surf = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            t = y / self.height
            if t < 0.45:
                sub_t = t / 0.45
                c1 = settings.SUNSET_TOP
                c2 = settings.SUNSET_MID
            elif t < 0.75:
                sub_t = (t - 0.45) / 0.30
                c1 = settings.SUNSET_MID
                c2 = settings.SUNSET_GLOW
            else:
                sub_t = (t - 0.75) / 0.25
                c1 = settings.SUNSET_GLOW
                c2 = settings.DEEP_JUNGLE_GREEN

            r = int(c1[0] * (1 - sub_t) + c2[0] * sub_t)
            g = int(c1[1] * (1 - sub_t) + c2[1] * sub_t)
            b = int(c1[2] * (1 - sub_t) + c2[2] * sub_t)
            pygame.draw.line(surf, (r, g, b), (0, y), (self.width, y))

        sun_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        sun_center = (self.width // 2, int(self.height * 0.38))
        for r in range(160, 0, -10):
            alpha = int(45 * (1 - r / 160))
            pygame.draw.circle(sun_surf, (255, 220, 120, alpha), sun_center, r)
        pygame.draw.circle(sun_surf, (255, 245, 180, 80), sun_center, 65)
        surf.blit(sun_surf, (0, 0))
        return surf

    def _create_canopy(self) -> pygame.Surface:
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        canopy_color = (18, 48, 40, 230)
        canopy_front = (14, 38, 30, 255)

        pts_left = [
            (0, self.height),
            (0, self.height - 180),
            (80, self.height - 150),
            (160, self.height - 90),
            (240, self.height - 30),
            (260, self.height)
        ]
        pygame.draw.polygon(surf, canopy_color, pts_left)

        pts_right = [
            (self.width, self.height),
            (self.width, self.height - 180),
            (self.width - 80, self.height - 150),
            (self.width - 160, self.height - 90),
            (self.width - 240, self.height - 30),
            (self.width - 260, self.height)
        ]
        pygame.draw.polygon(surf, canopy_color, pts_right)
        pygame.draw.rect(surf, canopy_front, (0, self.height - 24, self.width, 24))
        return surf

    def draw(self, surface: pygame.Surface):
        surface.blit(self.gradient_surface, (0, 0))
        surface.blit(self.canopy_surface, (0, 0))


class Menu:
    """Main Menu screen with clean typography and direct gameplay links."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.background = TropicalBackground(self.width, self.height)
        self.particles = ParticleManager(self.width, self.height)

        self.showcase_fruits = [
            {"type": "watermelon", "x": 130, "base_y": 280, "rad": 42, "phase": 0.0, "speed": 0.03},
            {"type": "mango", "x": self.width - 130, "base_y": 260, "rad": 38, "phase": 1.5, "speed": 0.028},
            {"type": "pineapple", "x": 150, "base_y": 520, "rad": 40, "phase": 3.0, "speed": 0.025},
            {"type": "dragonfruit", "x": self.width - 150, "base_y": 510, "rad": 38, "phase": 4.5, "speed": 0.032},
        ]

        self.title_font_large = get_font(52, bold=True)
        self.title_font_sub = get_font(20, bold=True)
        self.badge_font = get_font(16, bold=True)

        self.buttons = []
        self._init_buttons()
        self.wave_phase = 0.0

    def _init_buttons(self):
        cx = self.width // 2

        # 1. Primary Giant PLAY Button
        play_w, play_h = 340, 76
        play_y = 295
        play_btn = FruitArcadeButton(
            pygame.Rect(cx - play_w // 2, play_y, play_w, play_h),
            "PLAY ADVENTURE",
            base_color=settings.TROPICAL_ORANGE,
            accent_color=settings.MANGO_YELLOW,
            text_color=settings.CREAM_WHITE,
            font_size=28,
            action_id=settings.MODE_CLASSIC,
            icon_type="watermelon"
        )
        self.buttons.append(play_btn)

        # 2. Secondary Row 1 (Missions, Fruit Quiz, Fruit Puzzle)
        row1_w, row1_h = 240, 56
        row1_y = 405
        gap_x = 24

        btn_missions = FruitArcadeButton(
            pygame.Rect(cx - row1_w - gap_x - row1_w // 2, row1_y, row1_w, row1_h),
            "MISSIONS",
            base_color=settings.TROPICAL_TEAL,
            accent_color=settings.LIME_GREEN,
            font_size=20,
            action_id=settings.MODE_MISSIONS,
            icon_type="apple"
        )
        btn_quiz = FruitArcadeButton(
            pygame.Rect(cx - row1_w // 2, row1_y, row1_w, row1_h),
            "FRUIT QUIZ",
            base_color=settings.WATERMELON_PINK,
            accent_color=settings.TROPICAL_ORANGE,
            font_size=20,
            action_id=settings.MODE_QUIZ,
            icon_type="orange"
        )
        btn_puzzle = FruitArcadeButton(
            pygame.Rect(cx + row1_w // 2 + gap_x, row1_y, row1_w, row1_h),
            "FRUIT PUZZLE",
            base_color=(125, 95, 200),
            accent_color=(175, 130, 240),
            font_size=20,
            action_id=settings.MODE_PUZZLE,
            icon_type="banana"
        )
        self.buttons.extend([btn_missions, btn_quiz, btn_puzzle])

        # 3. Secondary Row 2 (Level Select, Achievements, Settings)
        row2_w, row2_h = 240, 56
        row2_y = 485

        btn_levels = FruitArcadeButton(
            pygame.Rect(cx - row2_w - gap_x - row2_w // 2, row2_y, row2_w, row2_h),
            "LEVELS",
            base_color=settings.LIME_GREEN,
            accent_color=settings.MANGO_YELLOW,
            text_color=(20, 55, 30),
            font_size=20,
            action_id=settings.MODE_LEVEL_SELECT,
            icon_type="kiwi"
        )
        btn_achieve = FruitArcadeButton(
            pygame.Rect(cx - row2_w // 2, row2_y, row2_w, row2_h),
            "REWARDS",
            base_color=settings.MANGO_YELLOW,
            accent_color=settings.TROPICAL_ORANGE,
            text_color=(60, 40, 10),
            font_size=20,
            action_id=settings.MODE_ACHIEVEMENTS,
            icon_type="strawberry"
        )
        btn_settings = FruitArcadeButton(
            pygame.Rect(cx + row2_w // 2 + gap_x, row2_y, row2_w, row2_h),
            "SETTINGS",
            base_color=(50, 85, 105),
            accent_color=settings.TROPICAL_TEAL,
            font_size=20,
            action_id=settings.MODE_SETTINGS,
            icon_type="coconut"
        )
        self.buttons.extend([btn_levels, btn_achieve, btn_settings])

        # 4. Quit Button at Bottom
        quit_w, quit_h = 160, 44
        quit_y = 570
        btn_quit = FruitArcadeButton(
            pygame.Rect(cx - quit_w // 2, quit_y, quit_w, quit_h),
            "QUIT GAME",
            base_color=(160, 45, 55),
            accent_color=settings.WATERMELON_PINK,
            font_size=18,
            action_id="QUIT"
        )
        self.buttons.append(btn_quit)

    def handle_event(self, event: pygame.event.Event) -> str:
        for btn in self.buttons:
            action = btn.handle_event(event)
            if action:
                return action
        return ""

    def update(self):
        self.particles.update()
        self.wave_phase += 0.04
        for btn in self.buttons:
            btn.update()
        for item in self.showcase_fruits:
            item["phase"] += item["speed"]

    def draw_title(self, surface: pygame.Surface):
        cx = self.width // 2
        wave_y = math.sin(self.wave_phase) * 6
        title_y = 110 + int(wave_y)

        title_str = "FRUIT NINJA"
        for off_x, off_y, col in [
            (0, 6, (14, 38, 30)),
            (0, 4, (35, 75, 60)),
            (2, 2, (180, 70, 20))
        ]:
            shadow_surf = self.title_font_large.render(title_str, True, col)
            surface.blit(shadow_surf, (cx - shadow_surf.get_width() // 2 + off_x, title_y + off_y))

        main_surf = self.title_font_large.render(title_str, True, settings.MANGO_YELLOW)
        surface.blit(main_surf, (cx - main_surf.get_width() // 2, title_y))

        sub_str = "3D ADVENTURE EDITION"
        sub_w, sub_h = 360, 36
        sub_y = title_y + 70

        badge_rect = pygame.Rect(cx - sub_w // 2, sub_y, sub_w, sub_h)
        badge_surf = pygame.Surface((sub_w, sub_h), pygame.SRCALPHA)
        pygame.draw.rect(badge_surf, (15, 45, 36, 210), (0, 0, sub_w, sub_h), border_radius=18)
        pygame.draw.rect(badge_surf, settings.UI_BORDER_GOLD, (0, 0, sub_w, sub_h), width=2, border_radius=18)
        surface.blit(badge_surf, badge_rect.topleft)

        sub_surf = self.title_font_sub.render(sub_str, True, settings.CREAM_WHITE)
        surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, sub_y + (sub_h - sub_surf.get_height()) // 2))

    def draw_showcase_fruits(self, surface: pygame.Surface):
        for item in self.showcase_fruits:
            y = item["base_y"] + math.sin(item["phase"]) * 14
            fruit_surf = FruitSpriteCache.get_whole_surface(item["type"], radius=item["rad"])
            shadow_surf = pygame.Surface((item["rad"] * 2 + 10, 16), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (10, 28, 22, 90), (0, 0, item["rad"] * 2 + 10, 16))
            surface.blit(shadow_surf, (item["x"] - item["rad"] - 5, y + item["rad"] + 6))

            rect = fruit_surf.get_rect(center=(int(item["x"]), int(y)))
            surface.blit(fruit_surf, rect)

    def draw_header_badges(self, surface: pygame.Surface):
        tag_rect = pygame.Rect(25, 20, 200, 34)
        tag_surf = pygame.Surface((tag_rect.width, tag_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(tag_surf, (20, 50, 40, 190), (0, 0, tag_rect.width, tag_rect.height), border_radius=14)
        pygame.draw.rect(tag_surf, settings.TROPICAL_TEAL, (0, 0, tag_rect.width, tag_rect.height), width=2, border_radius=14)
        surface.blit(tag_surf, tag_rect.topleft)

        txt_left = self.badge_font.render("TROPICAL ARCADE", True, settings.CREAM_WHITE)
        surface.blit(txt_left, (tag_rect.centerx - txt_left.get_width() // 2, tag_rect.centery - txt_left.get_height() // 2))

        score_rect = pygame.Rect(self.width - 200, 20, 175, 34)
        score_surf = pygame.Surface((score_rect.width, score_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(score_surf, (20, 50, 40, 190), (0, 0, score_rect.width, score_rect.height), border_radius=14)
        pygame.draw.rect(score_surf, settings.MANGO_YELLOW, (0, 0, score_rect.width, score_rect.height), width=2, border_radius=14)
        surface.blit(score_surf, score_rect.topleft)

        txt_right = self.badge_font.render("FRESH CUTS", True, settings.MANGO_YELLOW)
        surface.blit(txt_right, (score_rect.centerx - txt_right.get_width() // 2, score_rect.centery - txt_right.get_height() // 2))

    def draw(self):
        self.background.draw(self.screen)
        self.particles.draw_ambient_background(self.screen)
        self.draw_showcase_fruits(self.screen)
        self.draw_header_badges(self.screen)
        self.draw_title(self.screen)
        for btn in self.buttons:
            btn.draw(self.screen)
        self.particles.draw_foreground(self.screen)


class SettingsScreen:
    """Fully functional audio, controls, display, and data reset settings screen."""

    def __init__(self, screen: pygame.Surface, progress_mgr: ProgressManager):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.progress_mgr = progress_mgr

        self.background = TropicalBackground(self.width, self.height)
        self.font_header = get_font(38, bold=True)
        self.font_label = get_font(20, bold=True)
        self.font_value = get_font(18, bold=True)

        self.btn_back = FruitArcadeButton(
            pygame.Rect(40, 25, 170, 44),
            "< BACK",
            base_color=settings.TROPICAL_TEAL,
            accent_color=settings.LIME_GREEN,
            font_size=18,
            action_id="BACK"
        )

        cx = self.width // 2

        # Sliders / Buttons for Music & SFX
        self.btn_music_down = FruitArcadeButton(pygame.Rect(cx + 80, 130, 44, 40), "-", base_color=(40, 75, 65), font_size=20, action_id="MUSIC_DOWN")
        self.btn_music_up = FruitArcadeButton(pygame.Rect(cx + 200, 130, 44, 40), "+", base_color=(40, 75, 65), font_size=20, action_id="MUSIC_UP")

        self.btn_sfx_down = FruitArcadeButton(pygame.Rect(cx + 80, 190, 44, 40), "-", base_color=(40, 75, 65), font_size=20, action_id="SFX_DOWN")
        self.btn_sfx_up = FruitArcadeButton(pygame.Rect(cx + 200, 190, 44, 40), "+", base_color=(40, 75, 65), font_size=20, action_id="SFX_UP")

        # Toggles
        self.btn_toggle_music = FruitArcadeButton(pygame.Rect(cx + 80, 250, 164, 42), "MUSIC: ON", base_color=settings.LIME_GREEN, font_size=18, action_id="TOGGLE_MUSIC")
        self.btn_toggle_sfx = FruitArcadeButton(pygame.Rect(cx + 80, 310, 164, 42), "SFX: ON", base_color=settings.LIME_GREEN, font_size=18, action_id="TOGGLE_SFX")

        # Difficulty & Display Mode
        self.btn_difficulty = FruitArcadeButton(pygame.Rect(cx + 80, 370, 164, 42), "NORMAL", base_color=settings.MANGO_YELLOW, text_color=(20, 50, 35), font_size=18, action_id="TOGGLE_DIFF")
        self.btn_display = FruitArcadeButton(pygame.Rect(cx + 80, 430, 164, 42), "WINDOWED", base_color=settings.TROPICAL_TEAL, font_size=18, action_id="TOGGLE_DISP")

        # Reset Data Button
        self.btn_reset = FruitArcadeButton(pygame.Rect(cx - 130, 530, 260, 48), "RESET PROGRESS", base_color=(150, 40, 45), accent_color=settings.WATERMELON_PINK, font_size=18, action_id="RESET_DATA")

        self.reset_confirm_timer = 0
        self._sync_buttons_to_data()

    def _sync_buttons_to_data(self):
        s = self.progress_mgr.data.get("settings", {})
        self.btn_toggle_music.text = "MUSIC: ON" if s.get("music_on", True) else "MUSIC: OFF"
        self.btn_toggle_music.base_color = settings.LIME_GREEN if s.get("music_on", True) else (60, 70, 65)

        self.btn_toggle_sfx.text = "SFX: ON" if s.get("sfx_on", True) else "SFX: OFF"
        self.btn_toggle_sfx.base_color = settings.LIME_GREEN if s.get("sfx_on", True) else (60, 70, 65)

        self.btn_difficulty.text = s.get("difficulty", "Normal").upper()
        self.btn_display.text = "FULLSCREEN" if s.get("fullscreen", False) else "WINDOWED"

    def handle_event(self, event: pygame.event.Event) -> str:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            get_audio().play("click")
            return "BACK"

        a_back = self.btn_back.handle_event(event)
        if a_back == "BACK":
            get_audio().play("click")
            return "BACK"

        s = self.progress_mgr.data.setdefault("settings", {})

        # Music Volume
        if self.btn_music_down.handle_event(event) == "MUSIC_DOWN":
            s["music_volume"] = max(0.0, round(s.get("music_volume", 0.6) - 0.1, 1))
            get_audio().set_music_volume(s["music_volume"])
            self.progress_mgr.save()
        elif self.btn_music_up.handle_event(event) == "MUSIC_UP":
            s["music_volume"] = min(1.0, round(s.get("music_volume", 0.6) + 0.1, 1))
            get_audio().set_music_volume(s["music_volume"])
            self.progress_mgr.save()

        # SFX Volume
        elif self.btn_sfx_down.handle_event(event) == "SFX_DOWN":
            s["sfx_volume"] = max(0.0, round(s.get("sfx_volume", 0.8) - 0.1, 1))
            get_audio().set_sfx_volume(s["sfx_volume"])
            self.progress_mgr.save()
        elif self.btn_sfx_up.handle_event(event) == "SFX_UP":
            s["sfx_volume"] = min(1.0, round(s.get("sfx_volume", 0.8) + 0.1, 1))
            get_audio().set_sfx_volume(s["sfx_volume"])
            self.progress_mgr.save()

        # Toggles
        elif self.btn_toggle_music.handle_event(event) == "TOGGLE_MUSIC":
            s["music_on"] = not s.get("music_on", True)
            get_audio().toggle_music(s["music_on"])
            self._sync_buttons_to_data()
            self.progress_mgr.save()

        elif self.btn_toggle_sfx.handle_event(event) == "TOGGLE_SFX":
            s["sfx_on"] = not s.get("sfx_on", True)
            get_audio().toggle_sfx(s["sfx_on"])
            self._sync_buttons_to_data()
            self.progress_mgr.save()

        elif self.btn_difficulty.handle_event(event) == "TOGGLE_DIFF":
            diffs = ["Casual", "Normal", "Ninja"]
            cur = s.get("difficulty", "Normal")
            next_idx = (diffs.index(cur) + 1) % len(diffs) if cur in diffs else 1
            s["difficulty"] = diffs[next_idx]
            self._sync_buttons_to_data()
            self.progress_mgr.save()

        elif self.btn_display.handle_event(event) == "TOGGLE_DISP":
            s["fullscreen"] = not s.get("fullscreen", False)
            if s["fullscreen"]:
                pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.FULLSCREEN)
            else:
                pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
            self._sync_buttons_to_data()
            self.progress_mgr.save()

        elif self.btn_reset.handle_event(event) == "RESET_DATA":
            if self.reset_confirm_timer <= 0:
                self.reset_confirm_timer = 180  # Ask for second click
                self.btn_reset.text = "CONFIRM RESET?"
            else:
                self.progress_mgr.reset_progress()
                self._sync_buttons_to_data()
                self.reset_confirm_timer = 0
                self.btn_reset.text = "PROGRESS RESET!"

        return ""

    def update(self):
        self.btn_back.update()
        self.btn_music_down.update()
        self.btn_music_up.update()
        self.btn_sfx_down.update()
        self.btn_sfx_up.update()
        self.btn_toggle_music.update()
        self.btn_toggle_sfx.update()
        self.btn_difficulty.update()
        self.btn_display.update()
        self.btn_reset.update()

        if self.reset_confirm_timer > 0:
            self.reset_confirm_timer -= 1
            if self.reset_confirm_timer <= 0:
                self.btn_reset.text = "RESET PROGRESS"

    def draw(self):
        self.background.draw(self.screen)

        title_surf = self.font_header.render("ARCADE SETTINGS", True, settings.MANGO_YELLOW)
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 28))

        self.btn_back.draw(self.screen)

        cx = self.width // 2
        card_w, card_h = 660, 460
        card_rect = pygame.Rect(cx - card_w // 2, 95, card_w, card_h)

        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (23, 63, 53, 240), (0, 0, card_w, card_h), border_radius=22)
        pygame.draw.rect(card_surf, settings.UI_BORDER_GOLD, (0, 0, card_w, card_h), width=2, border_radius=22)
        self.screen.blit(card_surf, card_rect.topleft)

        s = self.progress_mgr.data.get("settings", {})
        m_vol = int(s.get("music_volume", 0.6) * 100)
        s_vol = int(s.get("sfx_volume", 0.8) * 100)

        # Labels
        labels = [
            ("Music Volume:", 138),
            ("Sound Effects:", 198),
            ("Music Audio Track:", 258),
            ("SFX Audio Feedback:", 318),
            ("Gameplay Difficulty:", 378),
            ("Display Window Mode:", 438),
        ]

        for text, y in labels:
            lbl = self.font_label.render(text, True, settings.CREAM_WHITE)
            self.screen.blit(lbl, (card_rect.x + 40, y))

        # Volume value displays
        mv_txt = self.font_value.render(f"{m_vol}%", True, settings.MANGO_YELLOW)
        self.screen.blit(mv_txt, (cx + 138 - mv_txt.get_width() // 2, 138))

        sv_txt = self.font_value.render(f"{s_vol}%", True, settings.MANGO_YELLOW)
        self.screen.blit(sv_txt, (cx + 138 - sv_txt.get_width() // 2, 198))

        # Buttons
        self.btn_music_down.draw(self.screen)
        self.btn_music_up.draw(self.screen)
        self.btn_sfx_down.draw(self.screen)
        self.btn_sfx_up.draw(self.screen)
        self.btn_toggle_music.draw(self.screen)
        self.btn_toggle_sfx.draw(self.screen)
        self.btn_difficulty.draw(self.screen)
        self.btn_display.draw(self.screen)
        self.btn_reset.draw(self.screen)
