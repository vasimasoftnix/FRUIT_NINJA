"""Fruit Ninja: 3D Adventure Edition - Mission Mode & Quest Objectives.

Defines 10 playable missions with live objective trackers, progress bars,
timers, star rewards, and sequential quest unlocking.
"""

from typing import List, Dict, Any
import pygame
import settings
from menu import FruitArcadeButton, TropicalBackground, get_font
from progress import ProgressManager
from audio import get_audio


MISSIONS_DATA = [
    {
        "id": 1,
        "title": "Mission 1: First Harvest",
        "desc": "Warm up your slicing blade by slicing 10 tropical fruits.",
        "type": "slice_any",
        "target": 10,
        "time_limit": 60,
        "stars": 1
    },
    {
        "id": 2,
        "title": "Mission 2: Century Slicer",
        "desc": "Accumulate 100 points in standard arcade slicing.",
        "type": "score",
        "target": 100,
        "time_limit": 75,
        "stars": 1
    },
    {
        "id": 3,
        "title": "Mission 3: Citrus Specialist",
        "desc": "Hunt and slice 5 juicy oranges out of the fruit waves.",
        "type": "slice_type",
        "target_fruit": "orange",
        "target": 5,
        "time_limit": 60,
        "stars": 1
    },
    {
        "id": 4,
        "title": "Mission 4: Combo Apprentice",
        "desc": "Slice at least 3 fruits in a single swift swipe stroke.",
        "type": "combo",
        "target": 3,
        "time_limit": 60,
        "stars": 2
    },
    {
        "id": 5,
        "title": "Mission 5: Speed Rush",
        "desc": "Speed challenge! Slice 20 fruits before the 45-second timer expires.",
        "type": "slice_any",
        "target": 20,
        "time_limit": 45,
        "stars": 2
    },
    {
        "id": 6,
        "title": "Mission 6: Minefield Ninja",
        "desc": "Slice 25 fruits while navigating around hazardous bombs.",
        "type": "slice_no_bomb",
        "target": 25,
        "time_limit": 60,
        "stars": 2
    },
    {
        "id": 7,
        "title": "Mission 7: High Roller",
        "desc": "Achieve an arcade score of 250 points in a single round.",
        "type": "score",
        "target": 250,
        "time_limit": 80,
        "stars": 2
    },
    {
        "id": 8,
        "title": "Mission 8: Tropical Salad",
        "desc": "Slice at least 5 different varieties of tropical fruits.",
        "type": "variety",
        "target": 5,
        "time_limit": 60,
        "stars": 3
    },
    {
        "id": 9,
        "title": "Mission 9: Master Combo",
        "desc": "Execute a monumental 5-fruit combo in one single blade cut!",
        "type": "combo",
        "target": 5,
        "time_limit": 60,
        "stars": 3
    },
    {
        "id": 10,
        "title": "Mission 10: Ultimate Fruit Ninja",
        "desc": "The grand trial: Slice 50 fruits and achieve 300 points!",
        "type": "grand_trial",
        "target_slices": 50,
        "target_score": 300,
        "time_limit": 90,
        "stars": 3
    }
]


class MissionTracker:
    """Tracks active mission progress during gameplay."""

    def __init__(self, mission_data: Dict[str, Any]):
        self.data = mission_data
        self.current_progress = 0
        self.target = mission_data.get("target", 1)
        self.time_remaining = mission_data.get("time_limit", 60)
        self.unique_fruits = set()
        self.best_combo = 0
        self.is_completed = False
        self.is_failed = False
        self.bomb_hit = False

    def on_slice(self, fruit_type: str, score: int, combo_count: int):
        mtype = self.data["type"]
        if mtype == "slice_any":
            self.current_progress += 1
        elif mtype == "score":
            self.current_progress = score
        elif mtype == "slice_type":
            if fruit_type == self.data.get("target_fruit"):
                self.current_progress += 1
        elif mtype == "combo":
            self.best_combo = max(self.best_combo, combo_count)
            self.current_progress = self.best_combo
        elif mtype == "slice_no_bomb":
            if not self.bomb_hit:
                self.current_progress += 1
        elif mtype == "variety":
            self.unique_fruits.add(fruit_type)
            self.current_progress = len(self.unique_fruits)
        elif mtype == "grand_trial":
            self.current_progress += 1

        # Check completion
        if mtype == "grand_trial":
            if self.current_progress >= self.data["target_slices"] and score >= self.data["target_score"]:
                self.is_completed = True
        else:
            if self.current_progress >= self.target:
                self.is_completed = True

    def on_bomb(self):
        self.bomb_hit = True
        if self.data["type"] == "slice_no_bomb":
            self.is_failed = True

    def update_timer(self, dt: float):
        if not self.is_completed and not self.is_failed:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.time_remaining = 0
                if not self.is_completed:
                    self.is_failed = True


class MissionsScreen:
    """Missions selection menu with progress bars and star rewards."""

    def __init__(self, screen: pygame.Surface, progress_mgr: ProgressManager):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.progress_mgr = progress_mgr

        self.background = TropicalBackground(self.width, self.height)
        self.font_header = get_font(38, bold=True)
        self.font_title = get_font(20, bold=True)
        self.font_desc = get_font(14, bold=False)
        self.font_badge = get_font(15, bold=True)

        self.btn_back = FruitArcadeButton(
            pygame.Rect(40, 25, 170, 44),
            "< BACK",
            base_color=settings.TROPICAL_TEAL,
            accent_color=settings.LIME_GREEN,
            font_size=18,
            action_id="BACK"
        )

        self.page = 0  # 2 pages of 5 missions
        self.btn_prev = FruitArcadeButton(
            pygame.Rect(self.width // 2 - 140, self.height - 65, 120, 42),
            "◀ PREV",
            base_color=settings.TROPICAL_TEAL,
            accent_color=settings.LIME_GREEN,
            font_size=16,
            action_id="PREV"
        )
        self.btn_next = FruitArcadeButton(
            pygame.Rect(self.width // 2 + 20, self.height - 65, 120, 42),
            "NEXT ▶",
            base_color=settings.TROPICAL_TEAL,
            accent_color=settings.LIME_GREEN,
            font_size=16,
            action_id="NEXT"
        )

        self.mission_buttons = []
        self._init_mission_buttons()

    def _init_mission_buttons(self):
        self.mission_buttons.clear()
        completed = set(self.progress_mgr.data.get("completed_missions", []))

        # First incomplete mission or max completed + 1 is unlocked
        unlocked_max = 1
        for m in MISSIONS_DATA:
            if m["id"] in completed:
                unlocked_max = max(unlocked_max, m["id"] + 1)
        unlocked_max = min(10, unlocked_max)

        start_idx = self.page * 5
        page_missions = MISSIONS_DATA[start_idx:start_idx + 5]

        card_w = 780
        card_h = 88
        start_y = 95
        gap_y = 16
        cx = self.width // 2

        for idx, m in enumerate(page_missions):
            y = start_y + idx * (card_h + gap_y)
            is_done = m["id"] in completed
            is_unlocked = m["id"] <= unlocked_max

            btn_label = "REPLAY" if is_done else ("START" if is_unlocked else "LOCKED")
            btn_col = settings.LIME_GREEN if is_done else (settings.TROPICAL_ORANGE if is_unlocked else (40, 50, 45))

            btn = FruitArcadeButton(
                pygame.Rect(cx + 240, y + 20, 125, 46),
                btn_label,
                base_color=btn_col,
                accent_color=settings.MANGO_YELLOW if is_unlocked else (40, 50, 45),
                text_color=settings.CREAM_WHITE if is_unlocked else (130, 140, 135),
                font_size=18,
                action_id=f"PLAY_MISSION_{m['id']}" if is_unlocked else ""
            )
            self.mission_buttons.append((m, btn, is_unlocked, is_done, pygame.Rect(cx - card_w // 2, y, card_w, card_h)))

    def refresh(self):
        self._init_mission_buttons()

    def handle_event(self, event: pygame.event.Event) -> str:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            get_audio().play("click")
            return "BACK"

        a_back = self.btn_back.handle_event(event)
        if a_back == "BACK":
            get_audio().play("click")
            return "BACK"

        if self.page > 0:
            if self.btn_prev.handle_event(event) == "PREV":
                get_audio().play("click")
                self.page = 0
                self._init_mission_buttons()
                return ""
        if self.page == 0:
            if self.btn_next.handle_event(event) == "NEXT":
                get_audio().play("click")
                self.page = 1
                self._init_mission_buttons()
                return ""

        for m, btn, is_unlocked, is_done, rect in self.mission_buttons:
            if is_unlocked:
                action = btn.handle_event(event)
                if action:
                    get_audio().play("click")
                    return action

        return ""

    def update(self):
        self.btn_back.update()
        if self.page > 0:
            self.btn_prev.update()
        if self.page == 0:
            self.btn_next.update()
        for m, btn, is_unlocked, is_done, rect in self.mission_buttons:
            if is_unlocked:
                btn.update()

    def draw(self):
        self.background.draw(self.screen)

        # Header Title
        title_surf = self.font_header.render("ADVENTURE MISSIONS", True, settings.MANGO_YELLOW)
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 26))

        # Star counter
        stars = self.progress_mgr.data.get("stars_earned", 0)
        star_pill = pygame.Rect(self.width - 200, 25, 160, 44)
        pygame.draw.rect(self.screen, (20, 50, 40), star_pill, border_radius=16)
        pygame.draw.rect(self.screen, settings.MANGO_YELLOW, star_pill, width=2, border_radius=16)
        star_txt = self.font_badge.render(f"STARS: {stars}", True, settings.MANGO_YELLOW)
        self.screen.blit(star_txt, (star_pill.centerx - star_txt.get_width() // 2, star_pill.centery - star_txt.get_height() // 2))

        # Back button
        self.btn_back.draw(self.screen)

        # Draw page buttons
        if self.page > 0:
            self.btn_prev.draw(self.screen)
        if self.page == 0:
            self.btn_next.draw(self.screen)

        # Page Indicator
        page_txt = self.font_badge.render(f"Page {self.page + 1} of 2", True, settings.CREAM_WHITE)
        self.screen.blit(page_txt, (self.width // 2 - page_txt.get_width() // 2, self.height - 40))

        # Draw Mission Cards
        for m, btn, is_unlocked, is_done, rect in self.mission_buttons:
            card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            if is_done:
                pygame.draw.rect(card_surf, (26, 75, 55, 240), (0, 0, rect.width, rect.height), border_radius=18)
                pygame.draw.rect(card_surf, settings.LIME_GREEN, (0, 0, rect.width, rect.height), width=2, border_radius=18)
            elif is_unlocked:
                pygame.draw.rect(card_surf, (23, 63, 53, 235), (0, 0, rect.width, rect.height), border_radius=18)
                pygame.draw.rect(card_surf, settings.UI_BORDER_GOLD, (0, 0, rect.width, rect.height), width=2, border_radius=18)
            else:
                pygame.draw.rect(card_surf, (15, 38, 30, 200), (0, 0, rect.width, rect.height), border_radius=18)
                pygame.draw.rect(card_surf, (35, 60, 50), (0, 0, rect.width, rect.height), width=2, border_radius=18)

            self.screen.blit(card_surf, rect.topleft)

            # Left Badge
            badge_x = rect.x + 44
            badge_y = rect.centery
            b_col = settings.LIME_GREEN if is_done else (settings.TROPICAL_ORANGE if is_unlocked else (40, 55, 48))
            pygame.draw.circle(self.screen, b_col, (badge_x, badge_y), 22)
            num_surf = self.font_title.render(str(m["id"]), True, settings.CREAM_WHITE)
            self.screen.blit(num_surf, (badge_x - num_surf.get_width() // 2, badge_y - num_surf.get_height() // 2))

            # Title
            t_col = settings.LIME_GREEN if is_done else (settings.MANGO_YELLOW if is_unlocked else (160, 160, 160))
            t_surf = self.font_title.render(m["title"], True, t_col)
            self.screen.blit(t_surf, (rect.x + 85, rect.y + 14))

            # Description
            d_surf = self.font_desc.render(m["desc"], True, settings.CREAM_WHITE if is_unlocked else (130, 140, 135))
            self.screen.blit(d_surf, (rect.x + 85, rect.y + 40))

            # Status Tag
            status_label = f"COMPLETED (+{m['stars']} Stars)" if is_done else (f"Reward: {m['stars']} Stars" if is_unlocked else "LOCKED")
            status_col = settings.LIME_GREEN if is_done else (settings.MANGO_YELLOW if is_unlocked else settings.WATERMELON_PINK)
            st_surf = self.font_badge.render(status_label, True, status_col)
            self.screen.blit(st_surf, (rect.x + 85, rect.y + 64))

            # Action Button
            btn.draw(self.screen)
