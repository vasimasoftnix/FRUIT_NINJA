"""Fruit Ninja: 3D Adventure Edition - Visual Effects & Particle Systems.

Handles:
- Dynamic glossy juice droplets & splashes
- Screen juice splatters (lingering fruit stains)
- Blade swipe ribbon trail with tropical glow
- Spark particles for bombs and combos
- Floating tropical leaf & petal particles for ambient atmosphere
"""

import math
import random
import pygame
import settings


class JuiceParticle:
    """Individual dynamic juice droplet with physics and fading."""

    def __init__(self, x: float, y: float, color, vx: float, vy: float, radius: float, lifetime: int = 40):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.initial_radius = radius
        self.lifetime = lifetime
        self.age = 0
        self.gravity = 0.28

    def update(self) -> bool:
        """Update particle physics. Returns False when expired."""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.98  # Air resistance
        self.age += 1

        # Shrink over lifetime
        progress = self.age / self.lifetime
        self.radius = max(0.5, self.initial_radius * (1.0 - progress))
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface):
        """Draw droplet with soft glossy highlight."""
        if self.radius < 0.5:
            return
        int_pos = (int(self.x), int(self.y))
        int_rad = max(1, int(self.radius))

        # Main juice droplet
        pygame.draw.circle(surface, self.color, int_pos, int_rad)

        # Specular glint on larger droplets
        if int_rad >= 3:
            highlight_pos = (int_pos[0] - int_rad // 3, int_pos[1] - int_rad // 3)
            highlight_rad = max(1, int_rad // 3)
            pygame.draw.circle(surface, settings.CREAM_WHITE, highlight_pos, highlight_rad)


class ScreenSplatter:
    """Lingering juice splat on the screen backdrop."""

    def __init__(self, x: float, y: float, color, size: float = 32.0, lifetime: int = 180):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0

        # Generate a unique irregular splatter shape
        self.blobs = []
        num_blobs = random.randint(5, 9)
        for _ in range(num_blobs):
            angle = random.uniform(0, math.tau)
            dist = random.uniform(0, size * 0.65)
            blob_r = random.uniform(size * 0.2, size * 0.45)
            self.blobs.append((math.cos(angle) * dist, math.sin(angle) * dist, blob_r))

    def update(self) -> bool:
        self.age += 1
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface):
        # Calculate alpha fade
        alpha = int(255 * (1.0 - (self.age / self.lifetime) ** 2))
        if alpha <= 0:
            return

        splat_surf = pygame.Surface((int(self.size * 2.5), int(self.size * 2.5)), pygame.SRCALPHA)
        center = (int(self.size * 1.25), int(self.size * 1.25))

        # Base color with alpha
        c = (self.color[0], self.color[1], self.color[2], min(alpha, 180))

        # Draw main center puddle
        pygame.draw.circle(splat_surf, c, center, int(self.size * 0.4))

        # Draw irregular droplets around puddle
        for bx, by, br in self.blobs:
            b_center = (int(center[0] + bx), int(center[1] + by))
            pygame.draw.circle(splat_surf, c, b_center, max(1, int(br)))

        surface.blit(splat_surf, (self.x - center[0], self.y - center[1]))


class AmbientLeaf:
    """Floating tropical leaf drifting gracefully across the screen."""

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = random.uniform(0, screen_w)
        self.y = random.uniform(-50, screen_h)
        self.vx = random.uniform(0.5, 1.8)
        self.vy = random.uniform(0.6, 1.4)
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1.5, 1.5)
        self.size = random.uniform(14, 26)
        # Deep tropical jungle green hues with varying translucency
        self.color = random.choice([
            (35, 95, 65, 130),
            (25, 75, 50, 110),
            (60, 130, 80, 120),
            (155, 207, 83, 90)  # Lime accent leaf
        ])

    def update(self):
        self.x += self.vx + math.sin(self.y * 0.02) * 0.6
        self.y += self.vy
        self.angle += self.rot_speed

        if self.y > self.screen_h + 40:
            self.y = -30
            self.x = random.uniform(0, self.screen_w)
        if self.x > self.screen_w + 40:
            self.x = -30

    def draw(self, surface: pygame.Surface):
        # Draw elongated stylized leaf
        leaf_surf = pygame.Surface((int(self.size * 2), int(self.size * 1.2)), pygame.SRCALPHA)
        center = (int(self.size), int(self.size * 0.6))

        # Oval leaf body
        rect = pygame.Rect(0, 0, int(self.size * 1.8), int(self.size * 0.8))
        rect.center = center
        pygame.draw.ellipse(leaf_surf, self.color, rect)

        # Rotate leaf
        rotated = pygame.transform.rotate(leaf_surf, self.angle)
        new_rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, new_rect)


class FloatingFruitDecoration:
    """Decorative ambient background fruit drifting slowly in distance with soft blur."""

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = random.uniform(40, screen_w - 40)
        self.y = random.uniform(40, screen_h - 40)
        self.base_y = self.y
        self.color = random.choice([
            settings.TROPICAL_ORANGE,
            settings.MANGO_YELLOW,
            settings.LIME_GREEN,
            settings.WATERMELON_PINK
        ])
        self.radius = random.uniform(18, 32)
        self.float_offset = random.uniform(0, math.tau)
        self.speed = random.uniform(0.015, 0.035)

    def update(self):
        self.float_offset += self.speed
        self.y = self.base_y + math.sin(self.float_offset) * 14

    def draw(self, surface: pygame.Surface):
        # Soft blurred circular glow
        surf = pygame.Surface((int(self.radius * 3), int(self.radius * 3)), pygame.SRCALPHA)
        center = (int(self.radius * 1.5), int(self.radius * 1.5))

        # Outer soft aura
        c_outer = (self.color[0], self.color[1], self.color[2], 25)
        pygame.draw.circle(surf, c_outer, center, int(self.radius * 1.4))

        # Inner ambient silhouette
        c_inner = (self.color[0], self.color[1], self.color[2], 55)
        pygame.draw.circle(surf, c_inner, center, int(self.radius))

        # Warm highlight glint
        c_glint = (255, 255, 255, 45)
        pygame.draw.circle(surf, c_glint, (center[0] - int(self.radius * 0.3), center[1] - int(self.radius * 0.3)), int(self.radius * 0.4))

        surface.blit(surf, (self.x - center[0], self.y - center[1]))


class SparkParticle:
    """Bright spark from blade collisions or bomb fuses."""

    def __init__(self, x: float, y: float, color=(255, 240, 120)):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2.0, 6.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(12, 24)
        self.age = 0

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.age += 1
        return self.age < self.lifetime

    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (1.0 - self.age / self.lifetime))
        if alpha <= 0:
            return
        spark_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        c = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(spark_surf, c, (3, 3), max(1, 3 - (self.age // 8)))
        surface.blit(spark_surf, (int(self.x) - 3, int(self.y) - 3))


class ParticleManager:
    """Central particle manager for the game."""

    def __init__(self, screen_w: int = settings.WINDOW_WIDTH, screen_h: int = settings.WINDOW_HEIGHT):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.juice_particles = []
        self.screen_splatters = []
        self.sparks = []
        self.ambient_leaves = [AmbientLeaf(screen_w, screen_h) for _ in range(16)]
        self.floating_fruits = [FloatingFruitDecoration(screen_w, screen_h) for _ in range(6)]

    def add_fruit_slice_effect(self, x: float, y: float, fruit_key: str):
        """Create juicy explosion and splatter when a fruit is sliced."""
        color_info = settings.FRUIT_COLORS.get(fruit_key, settings.FRUIT_COLORS["watermelon"])
        juice_color = color_info["juice"]
        highlight_color = color_info["highlight"]

        # Add background splatter stamp
        self.screen_splatters.append(
            ScreenSplatter(x, y, juice_color, size=random.uniform(28, 48))
        )
        if len(self.screen_splatters) > 18:
            self.screen_splatters.pop(0)

        # Dynamic flying droplets
        num_droplets = random.randint(22, 35)
        for _ in range(num_droplets):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(3.0, 11.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(1.0, 4.0)
            rad = random.uniform(2.5, 6.0)
            col = juice_color if random.random() > 0.3 else highlight_color
            lifetime = random.randint(30, 55)
            self.juice_particles.append(JuiceParticle(x, y, col, vx, vy, rad, lifetime))

        # Golden sparkle accents
        for _ in range(8):
            self.sparks.append(SparkParticle(x, y, settings.MANGO_YELLOW))

    def add_bomb_sparks(self, x: float, y: float):
        """Sparks emitted from bomb fuse."""
        for _ in range(4):
            self.sparks.append(SparkParticle(x, y, (255, random.randint(150, 220), 50)))

    def add_bomb_explosion(self, x: float, y: float):
        """Vibrant explosion effect."""
        for _ in range(40):
            self.sparks.append(SparkParticle(x, y, random.choice([
                settings.TROPICAL_ORANGE,
                settings.WATERMELON_PINK,
                settings.MANGO_YELLOW
            ])))
        self.screen_splatters.append(ScreenSplatter(x, y, (40, 20, 25), size=60, lifetime=220))

    def update(self):
        """Update physics and lifecycles of all particles."""
        self.juice_particles = [p for p in self.juice_particles if p.update()]
        self.screen_splatters = [s for s in self.screen_splatters if s.update()]
        self.sparks = [sp for sp in self.sparks if sp.update()]

        for leaf in self.ambient_leaves:
            leaf.update()
        for fruit in self.floating_fruits:
            fruit.update()

    def draw_ambient_background(self, surface: pygame.Surface):
        """Draw ambient floating fruits and drifting leaves in background."""
        for fruit in self.floating_fruits:
            fruit.draw(surface)
        for leaf in self.ambient_leaves:
            leaf.draw(surface)

    def draw_splatters(self, surface: pygame.Surface):
        """Draw screen splatters beneath the fruits and UI."""
        for splatter in self.screen_splatters:
            splatter.draw(surface)

    def draw_foreground(self, surface: pygame.Surface):
        """Draw flying juice droplets and sparks above fruits."""
        for droplet in self.juice_particles:
            droplet.draw(surface)
        for spark in self.sparks:
            spark.draw(surface)

    def clear_transients(self):
        """Clear dynamic particles when transitioning screens."""
        self.juice_particles.clear()
        self.sparks.clear()
