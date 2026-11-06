"""Fruit Ninja: 3D Adventure Edition - Core Slicing Gameplay Engine.

Handles:
- Classic Arcade Mode, Island Levels, and Mission Quest slicing sessions
- Spawning waves of 2.5D fruits (watermelon, orange, apple, banana, pineapple, strawberry, kiwi, coconut, mango, dragonfruit)
- Hazard bombs with animated glowing fuse sparks and explosion penalties
- Real-time mouse blade slicing trail collision detection & fruit splitting into rotating halves
- Fruit-specific juice splatter particle bursts and lingering screen stains
- Comprehensive HUD: Score, High Score, 3 Lives (Watermelon slices / Red strikes), Countdown Timer, Combo tracker, Pause button
- Full Pause dialog, Game Over screen, and Victory screen with progressive unlocks and high score saving
"""

import math
import random
import pygame
import settings
from player import Player
from fruit import Fruit, FruitHalf, Bomb, FruitSpriteCache
from particles import ParticleManager
from menu import FruitArcadeButton, TropicalBackground, get_font
from progress import ProgressManager
from audio import get_audio
from levels import LevelConfig, LEVELS_CATALOG
from missions import MissionTracker, MISSIONS_DATA


class GameplayManager:
    """Central engine managing the fruit-slicing arena across all modes."""

    def __init__(self, screen: pygame.Surface, progress_mgr: ProgressManager = None):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.progress_mgr = progress_mgr or ProgressManager()
        self.background = TropicalBackground(self.width, self.height)
        self.particles = ParticleManager(self.width, self.height)
        self.player = Player()

        # Entities
        self.fruits = []
        self.fruit_halves = []
        self.bombs = []

        # Mode configurations
        self.game_mode = "CLASSIC"  # "CLASSIC", "LEVEL", "MISSION"
        self.active_level_config: LevelConfig = None
        self.active_mission_tracker: MissionTracker = None

        # Session Metrics
        self.time_limit = 90.0  # seconds
        self.time_remaining = 90.0
        self.highest_combo = 0
        self.fruits_sliced_total = 0
        self.bomb_hits = 0

        # Spawner timers
        self.wave_timer = 0
        self.wave_interval = 85
        self.wave_count = 0

        # State: "PLAYING", "PAUSED", "GAME_OVER", "VICTORY"
        self.state = "PLAYING"
        self.end_reason = "timer"  # "timer", "lives", "bomb", "objective_complete"

        # Fonts
        self.hud_font_large = get_font(34, bold=True)
        self.hud_font_sub = get_font(18, bold=True)
        self.banner_font = get_font(46, bold=True)

        self._init_buttons()

    def _init_buttons(self):
        cx = self.width // 2
        cy = self.height // 2

        # Top HUD Pause Button
        self.btn_pause = FruitArcadeButton(
            pygame.Rect(self.width - 65, 18, 48, 44),
            "||",
            base_color=(45, 80, 70),
            accent_color=settings.TROPICAL_TEAL,
            font_size=20,
            action_id="PAUSE"
        )

        # Pause Menu
        btn_w, btn_h = 240, 52
        self.btn_resume = FruitArcadeButton(pygame.Rect(cx - btn_w // 2, cy - 40, btn_w, btn_h), "RESUME", base_color=settings.LIME_GREEN, font_size=20, action_id="RESUME")
        self.btn_pause_retry = FruitArcadeButton(pygame.Rect(cx - btn_w // 2, cy + 25, btn_w, btn_h), "RESTART", base_color=settings.TROPICAL_ORANGE, font_size=20, action_id="RETRY")
        self.btn_pause_menu = FruitArcadeButton(pygame.Rect(cx - btn_w // 2, cy + 90, btn_w, btn_h), "MAIN MENU", base_color=settings.TROPICAL_TEAL, font_size=20, action_id="MENU")

        # Game Over / Victory Buttons
        self.btn_over_retry = FruitArcadeButton(pygame.Rect(cx - btn_w - 15, cy + 125, btn_w, btn_h), "PLAY AGAIN", base_color=settings.TROPICAL_ORANGE, font_size=20, action_id="RETRY")
        self.btn_over_menu = FruitArcadeButton(pygame.Rect(cx + 15, cy + 125, btn_w, btn_h), "MAIN MENU", base_color=settings.TROPICAL_TEAL, font_size=20, action_id="MENU")
        self.btn_next_level = FruitArcadeButton(pygame.Rect(cx - btn_w // 2, cy + 125, btn_w, btn_h), "NEXT LEVEL", base_color=settings.LIME_GREEN, font_size=20, action_id="NEXT_STAGE")

    def start_classic(self):
        """Starts standard Arcade Endless mode with a 90-second countdown and 3 lives."""
        self.game_mode = "CLASSIC"
        self.active_level_config = None
        self.active_mission_tracker = None
        self.time_limit = 90.0
        self.time_remaining = 90.0
        self._reset_common_session()

    def start_level(self, level_id: int):
        """Starts an adventure level with custom parameters."""
        self.game_mode = "LEVEL"
        cfg = next((l for l in LEVELS_CATALOG if l.level_id == level_id), LEVELS_CATALOG[0])
        self.active_level_config = cfg
        self.active_mission_tracker = None
        self.time_limit = float(cfg.time_limit)
        self.time_remaining = self.time_limit
        self._reset_common_session()

    def start_mission(self, mission_id: int):
        """Starts a specific quest mission with live objective tracking."""
        self.game_mode = "MISSION"
        m = next((item for item in MISSIONS_DATA if item["id"] == mission_id), MISSIONS_DATA[0])
        self.active_mission_tracker = MissionTracker(m)
        self.active_level_config = None
        self.time_limit = float(m.get("time_limit", 60))
        self.time_remaining = self.time_limit
        self._reset_common_session()

    def _reset_common_session(self):
        self.player.reset()
        self.fruits.clear()
        self.fruit_halves.clear()
        self.bombs.clear()
        self.particles.clear_transients()
        self.highest_combo = 0
        self.fruits_sliced_total = 0
        self.bomb_hits = 0
        self.wave_timer = 20
        self.wave_count = 0
        self.state = "PLAYING"

    def spawn_wave(self):
        """Spawns an arcade wave based on active mode difficulty."""
        self.wave_count += 1
        get_audio().play("launch")

        # Determine fruit pool and bomb probability
        if self.game_mode == "LEVEL" and self.active_level_config:
            allowed = self.active_level_config.allowed_fruits
            bomb_chance = self.active_level_config.bomb_chance
            speed_min, speed_max = self.active_level_config.speed_range
            num_fruits = random.randint(2, min(5, 2 + self.wave_count // 3))
        elif self.game_mode == "MISSION":
            allowed = list(settings.FRUIT_COLORS.keys())
            bomb_chance = 0.25 if self.active_mission_tracker.data["type"] == "slice_no_bomb" else 0.15
            speed_min, speed_max = 14.0, 17.5
            num_fruits = random.randint(2, 4)
        else:
            # Classic Mode: scales with difficulty setting
            diff = self.progress_mgr.data.get("settings", {}).get("difficulty", "Normal")
            allowed = list(settings.FRUIT_COLORS.keys())
            bomb_chance = 0.10 if diff == "Casual" else (0.22 if diff == "Normal" else 0.32)
            speed_min = 13.5 if diff == "Casual" else (14.5 if diff == "Normal" else 16.5)
            speed_max = speed_min + 3.0
            num_fruits = random.randint(2, min(5, 2 + self.wave_count // 4))

        for _ in range(num_fruits):
            ftype = random.choice(allowed)
            x = random.randint(140, self.width - 140)
            y = self.height + 40
            vy = -random.uniform(speed_min, speed_max)
            drift_target = (self.width // 2) - x
            vx = (drift_target / (self.width * 0.5)) * random.uniform(1.0, 3.5)
            self.fruits.append(Fruit(ftype, x, y, vx, vy))

        # Hazard Bomb Spawn
        if self.wave_count >= 2 and random.random() < bomb_chance:
            bx = random.randint(160, self.width - 160)
            by = self.height + 40
            b_vy = -random.uniform(speed_min, speed_max * 0.95)
            b_vx = random.uniform(-2.2, 2.2)
            self.bombs.append(Bomb(bx, by, b_vx, b_vy))

    def handle_event(self, event: pygame.event.Event) -> str:
        if self.state == "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                get_audio().play("click")
                self.state = "PAUSED"
                return ""

            if self.btn_pause.handle_event(event) == "PAUSE":
                get_audio().play("click")
                self.state = "PAUSED"
                return ""

            self.player.blade.handle_event(event)

        elif self.state == "PAUSED":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                get_audio().play("click")
                self.state = "PLAYING"
                return ""

            if self.btn_resume.handle_event(event) == "RESUME":
                get_audio().play("click")
                self.state = "PLAYING"
                return ""
            if self.btn_pause_retry.handle_event(event) == "RETRY":
                get_audio().play("click")
                self._restart_current_mode()
                return ""
            if self.btn_pause_menu.handle_event(event) == "MENU":
                get_audio().play("click")
                return "MENU"

        elif self.state in ["GAME_OVER", "VICTORY"]:
            if self.btn_over_retry.handle_event(event) == "RETRY":
                get_audio().play("click")
                self._restart_current_mode()
                return ""
            if self.btn_over_menu.handle_event(event) == "MENU":
                get_audio().play("click")
                return "MENU"
            if self.state == "VICTORY" and self.btn_next_level:
                if self.btn_next_level.handle_event(event) == "NEXT_STAGE":
                    get_audio().play("click")
                    self._progress_next_stage()
                    return ""

        return ""

    def _restart_current_mode(self):
        if self.game_mode == "LEVEL" and self.active_level_config:
            self.start_level(self.active_level_config.level_id)
        elif self.game_mode == "MISSION" and self.active_mission_tracker:
            self.start_mission(self.active_mission_tracker.data["id"])
        else:
            self.start_classic()

    def _progress_next_stage(self):
        if self.game_mode == "LEVEL" and self.active_level_config:
            next_id = min(5, self.active_level_config.level_id + 1)
            self.start_level(next_id)
        elif self.game_mode == "MISSION" and self.active_mission_tracker:
            next_id = min(10, self.active_mission_tracker.data["id"] + 1)
            self.start_mission(next_id)
        else:
            self.start_classic()

    def update(self, dt: float = 0.016):
        self.particles.update()

        if self.state == "PLAYING":
            self.btn_pause.update()
            self.player.update(self.particles)

            # Countdown Timer
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self._check_timer_end()
                return

            if self.active_mission_tracker:
                self.active_mission_tracker.update_timer(dt)
                if self.active_mission_tracker.is_completed:
                    self._trigger_victory("Mission Objective Accomplished!")
                    return
                elif self.active_mission_tracker.is_failed:
                    self._trigger_game_over("Mission Objective Failed!")
                    return

            # Slicing Collision Checks
            segments = self.player.blade.get_recent_segments()
            if segments:
                for p1, p2 in segments:
                    # Check Fruit Slices
                    for fruit in self.fruits:
                        if not fruit.is_sliced and fruit.check_slice(p1, p2):
                            halves = fruit.slice()
                            self.fruit_halves.extend(halves)
                            self.particles.add_fruit_slice_effect(fruit.x, fruit.y, fruit.fruit_type)
                            self.player.register_slice(fruit.fruit_type, fruit.x, fruit.y)
                            self.fruits_sliced_total += 1

                            get_audio().play("slice")
                            get_audio().play("splat")

                            # First slice achievement check
                            self.progress_mgr.unlock_achievement("first_slice")

                            # Mission tracker notification
                            if self.active_mission_tracker:
                                self.active_mission_tracker.on_slice(fruit.fruit_type, self.player.score, len(self.player.active_combo_fruits))
                                if self.active_mission_tracker.is_completed:
                                    self._trigger_victory("Mission Target Reached!")
                                    return

                            # Level Target Check
                            if self.game_mode == "LEVEL" and self.active_level_config:
                                if self.fruits_sliced_total >= self.active_level_config.target_slices:
                                    self._trigger_victory(f"{self.active_level_config.title} Mastered!")
                                    return

                    # Check Bomb Collisions
                    for bomb in self.bombs:
                        if not bomb.is_exploded and bomb.check_slice(p1, p2):
                            bomb.is_exploded = True
                            self.particles.add_bomb_explosion(bomb.x, bomb.y)
                            self.bomb_hits += 1
                            get_audio().play("bomb")

                            if self.active_mission_tracker:
                                self.active_mission_tracker.on_bomb()
                                if self.active_mission_tracker.is_failed:
                                    self._trigger_game_over("Detonated a forbidden bomb!")
                                    return

                            # Penalty: lose a life and points
                            self.player.add_strike()
                            self.player.score = max(0, self.player.score - 10)

                            if self.player.strikes >= self.player.max_strikes:
                                self._trigger_game_over("Bomb Detonated & Lives Depleted!")
                                return

            # Record highest combo
            current_combo = len(self.player.active_combo_fruits)
            if current_combo > self.highest_combo:
                self.highest_combo = current_combo
                if self.highest_combo >= 3:
                    self.progress_mgr.unlock_achievement("combo_master")
                    get_audio().play("combo")

            # Check Score Achievements
            if self.player.score >= 100:
                self.progress_mgr.unlock_achievement("score_hunter")

            # Update Fruits & Missed Drops
            remaining_fruits = []
            for fruit in self.fruits:
                fruit.update()
                if fruit.is_sliced:
                    pass
                elif fruit.is_offscreen(self.height):
                    # Missed fruit penalty!
                    self.player.add_strike()
                    if self.player.strikes >= self.player.max_strikes:
                        self._trigger_game_over("Three fruits fell unsliced!")
                        return
                else:
                    remaining_fruits.append(fruit)
            self.fruits = remaining_fruits

            # Update fruit halves & bombs
            for half in self.fruit_halves:
                half.update()
            self.fruit_halves = [h for h in self.fruit_halves if not h.is_offscreen(self.height)]

            for bomb in self.bombs:
                bomb.update()
                self.particles.add_bomb_sparks(bomb.x, bomb.y - bomb.radius - 8)
            self.bombs = [b for b in self.bombs if not b.is_offscreen(self.height) and not b.is_exploded]

            # Spawner wave interval
            self.wave_timer -= 1
            if self.wave_timer <= 0:
                self.spawn_wave()
                self.wave_interval = max(55, 90 - self.wave_count * 2)
                self.wave_timer = self.wave_interval

        elif self.state == "PAUSED":
            self.btn_resume.update()
            self.btn_pause_retry.update()
            self.btn_pause_menu.update()

        elif self.state in ["GAME_OVER", "VICTORY"]:
            self.btn_over_retry.update()
            self.btn_over_menu.update()
            if self.btn_next_level:
                self.btn_next_level.update()

    def _check_timer_end(self):
        """Called when timer hits zero."""
        if self.game_mode == "LEVEL" and self.active_level_config:
            if self.fruits_sliced_total >= self.active_level_config.target_slices:
                self._trigger_victory(f"{self.active_level_config.title} Completed in Time!")
            else:
                self._trigger_game_over(f"Time ran out! Target was {self.active_level_config.target_slices} slices.")
        elif self.game_mode == "MISSION" and self.active_mission_tracker:
            if self.active_mission_tracker.is_completed:
                self._trigger_victory("Mission Objective Accomplished!")
            else:
                self._trigger_game_over("Mission time expired!")
        else:
            # Classic mode time completion
            self._trigger_game_over("Timer Expired! Well sliced, Ninja!")

    def _trigger_victory(self, message: str):
        self.state = "VICTORY"
        self.end_reason = message
        self.player.blade.points.clear()
        self.player.blade.is_slicing = False
        get_audio().play("victory")

        # Save stats
        self.progress_mgr.record_game(self.player.score, self.fruits_sliced_total)

        if self.fruits_sliced_total >= 25 and self.bomb_hits == 0:
            self.progress_mgr.unlock_achievement("bomb_dodger")

        if self.progress_mgr.data.get("total_slices", 0) >= 50:
            self.progress_mgr.unlock_achievement("fruit_beginner")

        # Unlock progression
        if self.game_mode == "LEVEL" and self.active_level_config:
            lvl_id = self.active_level_config.level_id
            self.progress_mgr.unlock_level(min(5, lvl_id + 1))
            # Calculate 1-3 stars
            stars = 3 if self.player.strikes == 0 else (2 if self.player.strikes == 1 else 1)
            self.progress_mgr.set_level_stars(lvl_id, stars)
            if lvl_id == 5:
                self.progress_mgr.unlock_achievement("ultimate_ninja")

        elif self.game_mode == "MISSION" and self.active_mission_tracker:
            m_id = self.active_mission_tracker.data["id"]
            self.progress_mgr.complete_mission(m_id, self.active_mission_tracker.data.get("stars", 1))
            if len(self.progress_mgr.data.get("completed_missions", [])) >= 5:
                self.progress_mgr.unlock_achievement("mission_champion")

    def _trigger_game_over(self, reason: str):
        self.state = "GAME_OVER"
        self.end_reason = reason
        self.player.blade.points.clear()
        self.player.blade.is_slicing = False
        get_audio().play("game_over")

        self.progress_mgr.record_game(self.player.score, self.fruits_sliced_total)
        if self.progress_mgr.data.get("total_slices", 0) >= 50:
            self.progress_mgr.unlock_achievement("fruit_beginner")

    def draw_hud(self, surface: pygame.Surface):
        # 1. Top Left: Score Pod
        score_rect = pygame.Rect(25, 18, 175, 46)
        score_bg = pygame.Surface((score_rect.width, score_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(score_bg, (18, 48, 40, 210), (0, 0, score_rect.width, score_rect.height), border_radius=16)
        pygame.draw.rect(score_bg, settings.UI_BORDER_GOLD, (0, 0, score_rect.width, score_rect.height), width=2, border_radius=16)
        surface.blit(score_bg, score_rect.topleft)

        score_txt = self.hud_font_large.render(str(self.player.score), True, settings.MANGO_YELLOW)
        surface.blit(score_txt, (score_rect.x + 48, score_rect.y + 4))

        mini_surf = FruitSpriteCache.get_whole_surface("watermelon", radius=14)
        surface.blit(mini_surf, (score_rect.x + 10, score_rect.y + 9))

        # 2. Top Center-Left: Countdown Timer
        t_secs = int(self.time_remaining)
        t_mins = t_secs // 60
        t_rem = t_secs % 60
        timer_str = f"{t_mins:02d}:{t_rem:02d}"

        time_rect = pygame.Rect(215, 18, 130, 46)
        time_bg = pygame.Surface((time_rect.width, time_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(time_bg, (18, 48, 40, 210), (0, 0, time_rect.width, time_rect.height), border_radius=16)
        t_border = settings.WATERMELON_PINK if self.time_remaining < 10 else settings.TROPICAL_TEAL
        pygame.draw.rect(time_bg, t_border, (0, 0, time_rect.width, time_rect.height), width=2, border_radius=16)
        surface.blit(time_bg, time_rect.topleft)

        time_txt = self.hud_font_large.render(timer_str, True, t_border)
        surface.blit(time_txt, (time_rect.centerx - time_txt.get_width() // 2, time_rect.centery - time_txt.get_height() // 2))

        # 3. Mode Objective Pill (Center HUD for Levels & Missions)
        if self.game_mode == "LEVEL" and self.active_level_config:
            target = self.active_level_config.target_slices
            prog_txt = f"Level {self.active_level_config.level_id}: {self.fruits_sliced_total}/{target} Slices"
            m_pill = pygame.Rect(360, 18, 250, 46)
            pygame.draw.rect(surface, (18, 48, 40), m_pill, border_radius=16)
            pygame.draw.rect(surface, settings.LIME_GREEN, m_pill, width=2, border_radius=16)
            p_surf = self.hud_font_sub.render(prog_txt, True, settings.LIME_GREEN)
            surface.blit(p_surf, (m_pill.centerx - p_surf.get_width() // 2, m_pill.centery - p_surf.get_height() // 2))

        elif self.game_mode == "MISSION" and self.active_mission_tracker:
            m = self.active_mission_tracker
            prog_txt = f"{m.data['title']}: {m.current_progress}/{m.target}"
            m_pill = pygame.Rect(360, 18, 260, 46)
            pygame.draw.rect(surface, (18, 48, 40), m_pill, border_radius=16)
            pygame.draw.rect(surface, settings.MANGO_YELLOW, m_pill, width=2, border_radius=16)
            p_surf = self.hud_font_sub.render(prog_txt, True, settings.MANGO_YELLOW)
            surface.blit(p_surf, (m_pill.centerx - p_surf.get_width() // 2, m_pill.centery - p_surf.get_height() // 2))

        # 4. Top Right: 3 Lives Strike Indicators
        strike_rect = pygame.Rect(self.width - 240, 18, 160, 46)
        strike_bg = pygame.Surface((strike_rect.width, strike_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(strike_bg, (18, 48, 40, 210), (0, 0, strike_rect.width, strike_rect.height), border_radius=16)
        pygame.draw.rect(strike_bg, settings.TROPICAL_TEAL, (0, 0, strike_rect.width, strike_rect.height), width=2, border_radius=16)
        surface.blit(strike_bg, strike_rect.topleft)

        for i in range(3):
            slot_x = strike_rect.x + 30 + i * 42
            slot_y = strike_rect.centery
            if i < self.player.strikes:
                pygame.draw.line(surface, settings.WATERMELON_PINK, (slot_x - 11, slot_y - 11), (slot_x + 11, slot_y + 11), 4)
                pygame.draw.line(surface, settings.WATERMELON_PINK, (slot_x + 11, slot_y - 11), (slot_x - 11, slot_y + 11), 4)
            else:
                pygame.draw.circle(surface, settings.LIME_GREEN, (slot_x, slot_y), 9)
                pygame.draw.circle(surface, settings.CREAM_WHITE, (slot_x - 3, slot_y - 3), 3)

        # 5. Pause button
        self.btn_pause.draw(surface)

    def draw_pause_overlay(self, surface: pygame.Surface):
        dim = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        dim.fill((14, 38, 30, 210))
        surface.blit(dim, (0, 0))

        cx, cy = self.width // 2, self.height // 2
        card_w, card_h = 420, 320
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (23, 63, 53, 250), (0, 0, card_w, card_h), border_radius=settings.UI_PANEL_RADIUS)
        pygame.draw.rect(card_surf, settings.UI_BORDER_GOLD, (0, 0, card_w, card_h), width=3, border_radius=settings.UI_PANEL_RADIUS)
        surface.blit(card_surf, card_rect.topleft)

        p_txt = self.banner_font.render("GAME PAUSED", True, settings.MANGO_YELLOW)
        surface.blit(p_txt, (cx - p_txt.get_width() // 2, card_rect.y + 35))

        self.btn_resume.draw(surface)
        self.btn_pause_retry.draw(surface)
        self.btn_pause_menu.draw(surface)

    def draw_game_over_or_victory(self, surface: pygame.Surface):
        dim = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        dim.fill((16, 30, 25, 230))
        surface.blit(dim, (0, 0))

        cx, cy = self.width // 2, self.height // 2
        card_w, card_h = 580, 420
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2 - 20, card_w, card_h)

        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (23, 63, 53, 250), (0, 0, card_w, card_h), border_radius=settings.UI_PANEL_RADIUS)
        border_col = settings.MANGO_YELLOW if self.state == "VICTORY" else settings.WATERMELON_PINK
        pygame.draw.rect(card_surf, border_col, (0, 0, card_w, card_h), width=3, border_radius=settings.UI_PANEL_RADIUS)
        surface.blit(card_surf, card_rect.topleft)

        title_str = "VICTORY!" if self.state == "VICTORY" else "GAME OVER"
        title_col = settings.MANGO_YELLOW if self.state == "VICTORY" else settings.WATERMELON_PINK
        t_surf = self.banner_font.render(title_str, True, title_col)
        surface.blit(t_surf, (cx - t_surf.get_width() // 2, card_rect.y + 32))

        sub_surf = self.hud_font_sub.render(self.end_reason, True, settings.CREAM_WHITE)
        surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, card_rect.y + 88))

        # Stats Breakdown
        high_score = self.progress_mgr.data.get("high_score", self.player.score)
        stats = [
            f"Final Score: {self.player.score}",
            f"Fruits Sliced: {self.fruits_sliced_total}",
            f"Highest Combo: {self.highest_combo}x",
            f"All-Time Best: {high_score}"
        ]

        for i, st in enumerate(stats):
            col = settings.MANGO_YELLOW if i == 0 else (settings.LIME_GREEN if i == 3 else settings.CREAM_WHITE)
            s_surf = self.hud_font_large.render(st, True, col) if i == 0 else self.hud_font_sub.render(st, True, col)
            surface.blit(s_surf, (cx - s_surf.get_width() // 2, card_rect.y + 130 + i * 36))

        # Buttons
        self.btn_over_retry.draw(surface)
        self.btn_over_menu.draw(surface)

    def draw(self):
        self.background.draw(self.screen)
        self.particles.draw_splatters(self.screen)
        self.particles.draw_ambient_background(self.screen)

        for half in self.fruit_halves:
            half.draw(self.screen)
        for fruit in self.fruits:
            fruit.draw(self.screen)
        for bomb in self.bombs:
            bomb.draw(self.screen)

        self.particles.draw_foreground(self.screen)
        self.player.draw(self.screen)
        self.draw_hud(self.screen)

        if self.state == "PAUSED":
            self.draw_pause_overlay(self.screen)
        elif self.state in ["GAME_OVER", "VICTORY"]:
            self.draw_game_over_or_victory(self.screen)
