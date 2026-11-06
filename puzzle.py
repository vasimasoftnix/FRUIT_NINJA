"""Fruit Ninja: 3D Adventure Edition - Fruit Puzzle Memory Match Mode.

Implements:
- 4x4 grid of 16 interactive fruit cards (8 matching fruit pairs)
- Robust 3D card flip animation with glossy 2.5D fruit faces
- Precise timestamp-based delay: unmatched cards stay visible for 1.5s before flipping down
- Matched cards remain permanently face up and non-clickable
- Click lockout while two unmatched cards are displayed
- Move counter, stopwatch timer, and star evaluation victory dialog
"""

import math
import random
import time
import pygame
import settings
from menu import FruitArcadeButton, TropicalBackground, get_font
from fruit import FruitSpriteCache
from progress import ProgressManager
from audio import get_audio


PUZZLE_FRUITS = [
    "watermelon", "orange", "apple", "banana",
    "pineapple", "strawberry", "kiwi", "coconut"
]


class PuzzleCard:
    """Individual memory card that flips to reveal a 2.5D fruit."""

    def __init__(self, card_id: int, fruit_type: str, rect: pygame.Rect):
        self.card_id = card_id
        self.fruit_type = fruit_type
        self.rect = rect
        self.is_flipped = False
        self.is_matched = False
        self.flip_progress = 0.0  # 0.0 (face down) to 1.0 (face up)
        self.target_flip = 0.0

    def flip_up(self):
        self.is_flipped = True
        self.target_flip = 1.0

    def flip_down(self):
        self.is_flipped = False
        self.target_flip = 0.0

    def update(self):
        """Smoothly animates card flipping."""
        self.flip_progress += (self.target_flip - self.flip_progress) * 0.22
        if abs(self.target_flip - self.flip_progress) < 0.005:
            self.flip_progress = self.target_flip

    def draw(self, surface: pygame.Surface):
        r = self.rect
        # Card width scaling for 3D flip illusion:
        # At flip_progress = 0.0: scale_x = abs(cos(0)) = 1.0 (full width back)
        # At flip_progress = 0.5: scale_x = abs(cos(pi/2)) = 0.0 (edge on)
        # At flip_progress = 1.0: scale_x = abs(cos(pi)) = 1.0 (full width face)
        scale_x = abs(math.cos(self.flip_progress * math.pi))
        draw_w = max(6, int(r.width * scale_x))
        draw_x = r.centerx - draw_w // 2

        card_rect = pygame.Rect(draw_x, r.y, draw_w, r.height)

        # Drop shadow
        s_rect = card_rect.copy()
        s_rect.y += 4
        s_surf = pygame.Surface((draw_w, r.height), pygame.SRCALPHA)
        pygame.draw.rect(s_surf, (10, 28, 22, 120), (0, 0, draw_w, r.height), border_radius=14)
        surface.blit(s_surf, s_rect.topleft)

        # Card Body: front if >= 0.5, back if < 0.5
        if self.flip_progress >= 0.5:
            # Face Up: Tropical card face with 2.5D fruit render
            card_surf = pygame.Surface((draw_w, r.height), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (245, 248, 240), (0, 0, draw_w, r.height), border_radius=14)
            border_col = settings.LIME_GREEN if self.is_matched else settings.MANGO_YELLOW
            border_w = 4 if self.is_matched else 2
            pygame.draw.rect(card_surf, border_col, (0, 0, draw_w, r.height), width=border_w, border_radius=14)
            surface.blit(card_surf, card_rect.topleft)

            # Draw Fruit if width allows
            if draw_w > 26:
                fruit_surf = FruitSpriteCache.get_whole_surface(self.fruit_type, radius=26)
                if scale_x < 0.95:
                    fw = max(1, int(fruit_surf.get_width() * scale_x))
                    scaled_fruit = pygame.transform.scale(fruit_surf, (fw, fruit_surf.get_height()))
                    f_rect = scaled_fruit.get_rect(center=card_rect.center)
                    surface.blit(scaled_fruit, f_rect)
                else:
                    f_rect = fruit_surf.get_rect(center=card_rect.center)
                    surface.blit(fruit_surf, f_rect)
        else:
            # Face Down: Tropical Jungle pattern with emblem
            card_surf = pygame.Surface((draw_w, r.height), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (30, 72, 60), (0, 0, draw_w, r.height), border_radius=14)
            pygame.draw.rect(card_surf, settings.UI_BORDER_GOLD, (0, 0, draw_w, r.height), width=2, border_radius=14)
            surface.blit(card_surf, card_rect.topleft)

            if draw_w > 25:
                # Decorative tropical palm cross emblem
                pygame.draw.circle(surface, settings.MANGO_YELLOW, card_rect.center, 12, width=2)
                pygame.draw.line(surface, settings.TROPICAL_ORANGE, (card_rect.centerx - 8, card_rect.centery), (card_rect.centerx + 8, card_rect.centery), 2)
                pygame.draw.line(surface, settings.TROPICAL_ORANGE, (card_rect.centerx, card_rect.centery - 8), (card_rect.centerx, card_rect.centery + 8), 2)


class FruitPuzzleScreen:
    """Complete 4x4 card matching memory puzzle."""

    def __init__(self, screen: pygame.Surface, progress_mgr: ProgressManager):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.progress_mgr = progress_mgr

        self.background = TropicalBackground(self.width, self.height)
        self.font_header = get_font(38, bold=True)
        self.font_stats = get_font(20, bold=True)
        self.font_badge = get_font(16, bold=True)

        self.btn_back = FruitArcadeButton(
            pygame.Rect(40, 25, 170, 44),
            "< BACK",
            base_color=settings.TROPICAL_TEAL,
            accent_color=settings.LIME_GREEN,
            font_size=18,
            action_id="BACK"
        )

        self.cards = []
        self.first_selected = None
        self.second_selected = None
        self.mismatch_deadline = 0.0  # Timestamp in seconds when cards should flip back

        self.moves_count = 0
        self.start_time = time.time()
        self.elapsed_seconds = 0
        self.is_completed = False

        self.btn_retry = None
        self.btn_menu = None

        self.reset_puzzle()

    def reset_puzzle(self):
        """Builds and shuffles a fresh 4x4 puzzle board."""
        self.cards.clear()
        self.first_selected = None
        self.second_selected = None
        self.mismatch_deadline = 0.0
        self.moves_count = 0
        self.start_time = time.time()
        self.elapsed_seconds = 0
        self.is_completed = False

        # 8 fruits x 2 = 16 cards
        deck = PUZZLE_FRUITS * 2
        random.shuffle(deck)

        grid_cols = 4
        grid_rows = 4
        card_w, card_h = 110, 110
        gap_x, gap_y = 18, 18

        total_w = grid_cols * card_w + (grid_cols - 1) * gap_x
        total_h = grid_rows * card_h + (grid_rows - 1) * gap_y

        start_x = (self.width - total_w) // 2
        start_y = 135

        for i, fruit in enumerate(deck):
            r = i // grid_cols
            c = i % grid_cols
            x = start_x + c * (card_w + gap_x)
            y = start_y + r * (card_h + gap_y)
            rect = pygame.Rect(x, y, card_w, card_h)
            self.cards.append(PuzzleCard(i, fruit, rect))

    def handle_event(self, event: pygame.event.Event) -> str:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            get_audio().play("click")
            return "BACK"

        a_back = self.btn_back.handle_event(event)
        if a_back == "BACK":
            get_audio().play("click")
            return "BACK"

        if self.is_completed:
            if self.btn_retry and self.btn_retry.handle_event(event) == "RETRY":
                get_audio().play("click")
                self.reset_puzzle()
                return ""
            if self.btn_menu and self.btn_menu.handle_event(event) == "MENU":
                get_audio().play("click")
                return "BACK"
            return ""

        # Lock input while two unmatched cards are waiting to flip back
        if self.mismatch_deadline > 0:
            return ""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for card in self.cards:
                # Only click unrevealed and unmatched cards
                if not card.is_matched and not card.is_flipped and card.rect.collidepoint(event.pos):
                    get_audio().play("click")
                    card.flip_up()

                    if self.first_selected is None:
                        # 1. First card clicked: reveal and keep visible
                        self.first_selected = card
                    elif self.second_selected is None and card != self.first_selected:
                        # 2. Second card clicked: reveal and check match
                        self.second_selected = card
                        self.moves_count += 1

                        if self.first_selected.fruit_type == self.second_selected.fruit_type:
                            # 3. Match found: keep both permanently face up
                            self.first_selected.is_matched = True
                            self.second_selected.is_matched = True
                            get_audio().play("combo")
                            self.first_selected = None
                            self.second_selected = None
                            self._check_victory()
                        else:
                            # 4. Mismatch: keep both visible for 1.5 seconds using timestamp
                            self.mismatch_deadline = time.time() + 1.5
                            get_audio().play("quiz_wrong")
                    break

        return ""

    def _check_victory(self):
        if all(c.is_matched for c in self.cards):
            self.is_completed = True
            get_audio().play("victory")
            stars_awarded = 3 if self.moves_count <= 16 else (2 if self.moves_count <= 24 else 1)
            self.progress_mgr.data["stars_earned"] = self.progress_mgr.data.get("stars_earned", 0) + stars_awarded
            self.progress_mgr.save()

            cx = self.width // 2
            cy = self.height // 2
            btn_w, btn_h = 220, 52
            self.btn_retry = FruitArcadeButton(
                pygame.Rect(cx - btn_w - 15, cy + 110, btn_w, btn_h),
                "PLAY AGAIN",
                base_color=settings.TROPICAL_ORANGE,
                accent_color=settings.MANGO_YELLOW,
                font_size=20,
                action_id="RETRY"
            )
            self.btn_menu = FruitArcadeButton(
                pygame.Rect(cx + 15, cy + 110, btn_w, btn_h),
                "MAIN MENU",
                base_color=settings.TROPICAL_TEAL,
                accent_color=settings.LIME_GREEN,
                font_size=20,
                action_id="MENU"
            )

    def update(self):
        self.btn_back.update()

        if not self.is_completed:
            self.elapsed_seconds = int(time.time() - self.start_time)

        for card in self.cards:
            card.update()

        # Handle 1.5s mismatch flip-back timer
        if self.mismatch_deadline > 0:
            if time.time() >= self.mismatch_deadline:
                self.mismatch_deadline = 0.0
                if self.first_selected and self.second_selected:
                    self.first_selected.flip_down()
                    self.second_selected.flip_down()
                    self.first_selected = None
                    self.second_selected = None

        if self.is_completed:
            if self.btn_retry:
                self.btn_retry.update()
            if self.btn_menu:
                self.btn_menu.update()

    def draw(self):
        self.background.draw(self.screen)

        # Header Title
        title_surf = self.font_header.render("FRUIT MEMORY PUZZLE", True, settings.MANGO_YELLOW)
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 26))

        # Back Button
        self.btn_back.draw(self.screen)

        # Stats Header Bar (Moves and Time)
        mins = self.elapsed_seconds // 60
        secs = self.elapsed_seconds % 60
        time_str = f"Time: {mins:02d}:{secs:02d}"
        moves_str = f"Moves: {self.moves_count}"

        stats_rect = pygame.Rect(self.width - 290, 25, 250, 44)
        pygame.draw.rect(self.screen, (20, 50, 40), stats_rect, border_radius=16)
        pygame.draw.rect(self.screen, settings.MANGO_YELLOW, stats_rect, width=2, border_radius=16)
        st_txt = self.font_stats.render(f"{moves_str}  |  {time_str}", True, settings.CREAM_WHITE)
        self.screen.blit(st_txt, (stats_rect.centerx - st_txt.get_width() // 2, stats_rect.centery - st_txt.get_height() // 2))

        # Draw Grid of 16 Cards
        for card in self.cards:
            card.draw(self.screen)

        # Victory Dialog Overlay
        if self.is_completed:
            cx, cy = self.width // 2, self.height // 2
            dim = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            dim.fill((14, 38, 30, 210))
            self.screen.blit(dim, (0, 0))

            card_w, card_h = 560, 380
            card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (23, 63, 53, 250), (0, 0, card_w, card_h), border_radius=22)
            pygame.draw.rect(card_surf, settings.UI_BORDER_GOLD, (0, 0, card_w, card_h), width=3, border_radius=22)
            self.screen.blit(card_surf, card_rect.topleft)

            # Victory Header
            v_title = self.font_header.render("PUZZLE SOLVED!", True, settings.MANGO_YELLOW)
            self.screen.blit(v_title, (cx - v_title.get_width() // 2, card_rect.y + 35))

            v_sub = self.font_stats.render("All 8 Fruit Pairs Matched Perfectly!", True, settings.CREAM_WHITE)
            self.screen.blit(v_sub, (cx - v_sub.get_width() // 2, card_rect.y + 90))

            v_time = self.font_stats.render(f"Finished in {self.moves_count} moves ({mins:02d}:{secs:02d})", True, settings.LIME_GREEN)
            self.screen.blit(v_time, (cx - v_time.get_width() // 2, card_rect.y + 135))

            stars = 3 if self.moves_count <= 16 else (2 if self.moves_count <= 24 else 1)
            star_label = f"Rating: {'★' * stars}{'☆' * (3 - stars)} (+{stars} Stars!)"
            s_surf = self.font_header.render(star_label, True, settings.MANGO_YELLOW)
            self.screen.blit(s_surf, (cx - s_surf.get_width() // 2, card_rect.y + 180))

            if self.btn_retry:
                self.btn_retry.draw(self.screen)
            if self.btn_menu:
                self.btn_menu.draw(self.screen)
