"""Fruit Ninja: 3D Adventure Edition - Player State & Blade Controller.

Implements:
- Smooth blade swipe trail with tapered width and tropical glow
- Real-time mouse/touch swipe tracking and collision segment generation
- Player score, strike count (3 strikes rule), and multi-slice combo detection
- Blade spark emitters on rapid slices
"""

import math
import time
import pygame
import settings
from particles import SparkParticle


class Blade:
    """Manages swipe detection, tapered ribbon trail rendering, and slicing segments."""

    def __init__(self, blade_style: str = "classic_blade"):
        self.blade_style = blade_style
        self.points = []  # List of dict: {'pos': (x, y), 'time': float}
        self.max_age = 0.14  # Trail duration in seconds
        self.min_distance = 6  # Minimum distance between recorded points
        self.is_slicing = False

        # Blade style colors: (Outer glow, Mid aura, Core)
        self.style_palettes = {
            "classic_blade": (settings.TROPICAL_TEAL, settings.LIME_GREEN, settings.CREAM_WHITE),
            "flame_blade": (settings.TROPICAL_ORANGE, settings.WATERMELON_PINK, settings.MANGO_YELLOW),
            "rainbow_blade": (settings.MANGO_YELLOW, settings.TROPICAL_TEAL, settings.WHITE),
            "jungle_blade": (settings.LIME_GREEN, settings.DEEP_JUNGLE_GREEN, settings.CREAM_WHITE)
        }

    def set_style(self, style_name: str):
        if style_name in self.style_palettes:
            self.blade_style = style_name

    def handle_event(self, event: pygame.event.Event):
        """Processes mouse press, release, and drag movements."""
        now = time.time()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_slicing = True
            self.points.clear()
            self.points.append({"pos": event.pos, "time": now})
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_slicing = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_slicing:
                if not self.points:
                    self.points.append({"pos": event.pos, "time": now})
                else:
                    last_pos = self.points[-1]["pos"]
                    dist = math.hypot(event.pos[0] - last_pos[0], event.pos[1] - last_pos[1])
                    if dist >= self.min_distance:
                        self.points.append({"pos": event.pos, "time": now})

    def update(self, particles=None):
        """Prunes expired trail points and emits blade sparks on swift swipes."""
        now = time.time()
        self.points = [p for p in self.points if (now - p["time"]) <= self.max_age]

        # If swift swipe and particles provided, emit sparks from the leading tip
        if particles and len(self.points) >= 2:
            p1 = self.points[-2]["pos"]
            p2 = self.points[-1]["pos"]
            speed = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            if speed > 18:
                palette = self.style_palettes.get(self.blade_style, self.style_palettes["classic_blade"])
                particles.sparks.append(SparkParticle(p2[0], p2[1], palette[0]))

    def get_recent_segments(self) -> list:
        """Returns list of line segments ((x1, y1), (x2, y2)) from the active swipe."""
        segments = []
        if len(self.points) < 2:
            return segments

        for i in range(len(self.points) - 1):
            segments.append((self.points[i]["pos"], self.points[i + 1]["pos"]))
        return segments

    def draw(self, surface: pygame.Surface):
        """Renders glowing tapered blade ribbon trail."""
        if len(self.points) < 2:
            return

        now = time.time()
        n = len(self.points)
        outer_col, mid_col, core_col = self.style_palettes.get(
            self.blade_style, self.style_palettes["classic_blade"]
        )

        # Draw glowing layered line segments from tail to head
        for i in range(n - 1):
            p1 = self.points[i]["pos"]
            p2 = self.points[i + 1]["pos"]

            age = now - self.points[i]["time"]
            t = 1.0 - (age / self.max_age)
            if t <= 0:
                continue

            progress = i / float(n)  # 0.0 at tail, 1.0 at tip

            # Tapered widths
            outer_w = max(1, int(11 * t * progress))
            mid_w = max(1, int(6 * t * progress))
            core_w = max(1, int(3 * t * progress))

            # Outer glow aura
            pygame.draw.line(surface, outer_col, p1, p2, outer_w)
            # Mid radiance
            pygame.draw.line(surface, mid_col, p1, p2, mid_w)
            # Inner white-hot core
            pygame.draw.line(surface, core_col, p1, p2, core_w)

        # Draw sharp leading glint at tip
        tip_pos = self.points[-1]["pos"]
        pygame.draw.circle(surface, core_col, tip_pos, 4)
        pygame.draw.circle(surface, outer_col, tip_pos, 7, width=1)


class ComboPopup:
    """Floating animated text popup announcing combos (e.g., '+3 COMBO!')."""

    def __init__(self, x: float, y: float, text: str, color=settings.MANGO_YELLOW):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 45
        self.age = 0
        self.vy = -1.6
        self.font = pygame.font.SysFont("arialblack", 24, bold=True)

    def update(self) -> bool:
        self.y += self.vy
        self.age += 1
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (1.0 - (self.age / self.lifetime) ** 2))
        if alpha <= 0:
            return

        text_surf = self.font.render(self.text, True, self.color)
        shadow_surf = self.font.render(self.text, True, (15, 35, 25))

        # Alpha container
        container = pygame.Surface((text_surf.get_width() + 10, text_surf.get_height() + 10), pygame.SRCALPHA)
        container.blit(shadow_surf, (4, 4))
        container.blit(text_surf, (2, 2))
        container.set_alpha(alpha)

        surface.blit(container, (self.x - container.get_width() // 2, self.y))


class Player:
    """Manages player score, strikes, multi-slice combo detection, and active blade."""

    def __init__(self):
        self.score = 0
        self.strikes = 0
        self.max_strikes = 3
        self.blade = Blade("classic_blade")
        self.active_combo_fruits = []  # Fruits sliced in current continuous swipe
        self.combo_popups = []

    def reset(self):
        """Resets gameplay counters for a fresh round."""
        self.score = 0
        self.strikes = 0
        self.active_combo_fruits.clear()
        self.combo_popups.clear()
        self.blade.points.clear()
        self.blade.is_slicing = False

    def add_strike(self):
        """Increments strike counter when a fruit drops unsliced."""
        self.strikes = min(self.max_strikes, self.strikes + 1)

    def register_slice(self, fruit_type: str, x: float, y: float) -> int:
        """Records sliced fruit, scores points, and tracks combos."""
        self.score += 1
        self.active_combo_fruits.append({"type": fruit_type, "pos": (x, y)})
        return 1

    def evaluate_combo(self) -> int:
        """Called when swipe completes; awards bonus points if 3+ fruits were sliced."""
        bonus = 0
        count = len(self.active_combo_fruits)
        if count >= 3:
            bonus = count
            self.score += bonus

            # Calculate average position for popup
            avg_x = sum(f["pos"][0] for f in self.active_combo_fruits) / count
            avg_y = sum(f["pos"][1] for f in self.active_combo_fruits) / count

            msg = f"{count}x COMBO! +{bonus}"
            if count >= 5:
                msg = f"★ BLITZ {count}x! +{bonus * 2} ★"
                self.score += bonus  # extra blitz bonus

            self.combo_popups.append(ComboPopup(avg_x, avg_y, msg))

        self.active_combo_fruits.clear()
        return bonus

    def update(self, particles=None):
        self.blade.update(particles)
        self.combo_popups = [cp for cp in self.combo_popups if cp.update()]

        # If user stopped slicing, evaluate whatever was gathered in this swipe
        if not self.blade.is_slicing and self.active_combo_fruits:
            self.evaluate_combo()

    def draw(self, surface: pygame.Surface):
        self.blade.draw(surface)
        for cp in self.combo_popups:
            cp.draw(surface)
