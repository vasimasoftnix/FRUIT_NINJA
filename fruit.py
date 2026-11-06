"""Fruit Ninja: 3D Adventure Edition - 3D-Style Fruit & Hazard Entities.

Implements:
- Procedural 3D-style glossy fruit rendering (Watermelon, Mango, Orange, Lime, Dragonfruit, Pineapple, Banana, Coconut)
- Realistic layered textures: Rind, pulp, seeds, and glossy specular highlights
- Clean slicing into rotating halves with exposed interior cross-sections
- 3D hazard Bomb with animated glowing fuse and warning iconography
"""

import math
import random
import pygame
import settings


def create_radial_gradient_surface(radius: int, inner_color, outer_color) -> pygame.Surface:
    """Creates a smooth radial gradient surface for 3D sphere illusion."""
    diameter = radius * 2
    surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        t = r / radius
        col = (
            int(inner_color[0] * (1 - t) + outer_color[0] * t),
            int(inner_color[1] * (1 - t) + outer_color[1] * t),
            int(inner_color[2] * (1 - t) + outer_color[2] * t)
        )
        pygame.draw.circle(surf, col, (radius, radius), r)
    return surf


class FruitSpriteCache:
    """Pre-renders and caches 3D-style whole and halved fruit graphics."""
    _cache = {}

    @classmethod
    def get_whole_surface(cls, fruit_type: str, radius: int = 44) -> pygame.Surface:
        key = (fruit_type, radius, "whole")
        if key in cls._cache:
            return cls._cache[key]

        diameter = radius * 2
        surf = pygame.Surface((diameter + 16, diameter + 16), pygame.SRCALPHA)
        center = (radius + 8, radius + 8)

        info = settings.FRUIT_COLORS.get(fruit_type, settings.FRUIT_COLORS["watermelon"])
        highlight = info.get("highlight", settings.CREAM_WHITE)

        if fruit_type == "watermelon":
            # 3D Striped Green Watermelon
            dark_green = (34, 100, 42)
            light_green = (120, 195, 80)
            pygame.draw.circle(surf, dark_green, center, radius)
            # Wavy dark/light rind stripes
            for a in range(0, 360, 45):
                rad_a = math.radians(a)
                p1 = (center[0] + math.cos(rad_a) * radius * 0.9, center[1] + math.sin(rad_a) * radius * 0.9)
                p2 = (center[0] + math.cos(rad_a + 0.3) * radius * 0.5, center[1] + math.sin(rad_a + 0.3) * radius * 0.5)
                pygame.draw.line(surf, light_green, p1, p2, 5)

        elif fruit_type == "mango":
            # Plump golden-red kidney/oval
            rect = pygame.Rect(center[0] - radius, center[1] - int(radius * 1.15), radius * 2, int(radius * 2.3))
            pygame.draw.ellipse(surf, info["skin"], rect)
            blush_rect = pygame.Rect(center[0] - int(radius * 0.7), center[1] - int(radius * 0.9), int(radius * 1.4), int(radius * 1.6))
            pygame.draw.ellipse(surf, (255, 100, 35), blush_rect)

        elif fruit_type == "orange":
            # Pitted textured sphere
            pygame.draw.circle(surf, info["skin"], center, radius)
            for _ in range(25):
                px = center[0] + random.randint(-int(radius * 0.75), int(radius * 0.75))
                py = center[1] + random.randint(-int(radius * 0.75), int(radius * 0.75))
                if math.hypot(px - center[0], py - center[1]) < radius - 4:
                    pygame.draw.circle(surf, (255, 175, 45), (px, py), 2)

        elif fruit_type == "lime":
            # Zesty green sphere with citrus texture
            pygame.draw.circle(surf, info["skin"], center, radius)
            pygame.draw.circle(surf, (140, 205, 65), center, radius - 4)

        elif fruit_type == "dragonfruit":
            # Magenta egg with leafy tips
            rect = pygame.Rect(center[0] - radius, center[1] - int(radius * 1.1), radius * 2, int(radius * 2.2))
            pygame.draw.ellipse(surf, info["skin"], rect)
            # Green flame scales
            for offset_y in [-radius // 2, 0, radius // 2]:
                pts_l = [(center[0] - radius, center[1] + offset_y),
                         (center[0] - radius - 10, center[1] + offset_y - 8),
                         (center[0] - radius + 4, center[1] + offset_y + 8)]
                pts_r = [(center[0] + radius, center[1] + offset_y),
                         (center[0] + radius + 10, center[1] + offset_y - 8),
                         (center[0] + radius - 4, center[1] + offset_y + 8)]
                pygame.draw.polygon(surf, settings.LIME_GREEN, pts_l)
                pygame.draw.polygon(surf, settings.LIME_GREEN, pts_r)

        elif fruit_type == "pineapple":
            # Diamond patterned cylinder with crown
            body_rect = pygame.Rect(center[0] - int(radius * 0.85), center[1] - int(radius * 0.8), int(radius * 1.7), int(radius * 2.0))
            pygame.draw.ellipse(surf, info["skin"], body_rect)
            # Spiky green crown leaves on top
            crown_pts = [
                (center[0] - 12, center[1] - int(radius * 0.75)),
                (center[0] - 22, center[1] - radius - 18),
                (center[0], center[1] - radius - 24),
                (center[0] + 22, center[1] - radius - 18),
                (center[0] + 12, center[1] - int(radius * 0.75))
            ]
            pygame.draw.polygon(surf, settings.LIME_GREEN, crown_pts)

        elif fruit_type == "banana":
            # Yellow curved crescent
            pts = [
                (center[0] - radius, center[1] + radius // 2),
                (center[0], center[1] - radius // 2),
                (center[0] + radius, center[1] + radius // 3),
                (center[0] + radius - 6, center[1] + radius // 3 + 12),
                (center[0], center[1] - radius // 4),
                (center[0] - radius + 4, center[1] + radius // 2 + 10)
            ]
            pygame.draw.polygon(surf, info["skin"], pts)
            # Stem tip
            pygame.draw.circle(surf, (100, 80, 30), pts[0], 4)

        elif fruit_type == "apple":
            # Glossy red heart-round shape with dimple, stem, and leaf
            rect = pygame.Rect(center[0] - radius, center[1] - int(radius * 0.95), radius * 2, int(radius * 1.9))
            pygame.draw.ellipse(surf, info["skin"], rect)
            # Darker crimson bottom shading
            bot_rect = pygame.Rect(center[0] - int(radius * 0.8), center[1], int(radius * 1.6), int(radius * 0.8))
            pygame.draw.ellipse(surf, (170, 25, 25), bot_rect)
            # Brown stem
            stem_p1 = (center[0], center[1] - int(radius * 0.95))
            stem_p2 = (center[0] + 6, center[1] - radius - 10)
            pygame.draw.line(surf, (90, 50, 25), stem_p1, stem_p2, 4)
            # Green leaf
            leaf_pts = [stem_p2, (stem_p2[0] + 12, stem_p2[1] - 4), (stem_p2[0] + 6, stem_p2[1] + 6)]
            pygame.draw.polygon(surf, settings.LIME_GREEN, leaf_pts)

        elif fruit_type == "strawberry":
            # Heart/cone strawberry with yellow seed specks and leafy green calyx
            cone_pts = [
                (center[0] - int(radius * 0.85), center[1] - int(radius * 0.5)),
                (center[0], center[1] + int(radius * 1.05)),
                (center[0] + int(radius * 0.85), center[1] - int(radius * 0.5)),
                (center[0] + int(radius * 0.5), center[1] - int(radius * 0.85)),
                (center[0] - int(radius * 0.5), center[1] - int(radius * 0.85))
            ]
            pygame.draw.polygon(surf, info["skin"], cone_pts)
            # Yellow seed dots
            for sx, sy in [(-12, -10), (12, -10), (0, -5), (-16, 8), (14, 8), (0, 16), (-8, 25), (7, 25)]:
                pygame.draw.circle(surf, (255, 230, 90), (center[0] + sx, center[1] + sy), 2)
            # Green star calyx on top
            calyx_pts = [
                (center[0], center[1] - int(radius * 0.85)),
                (center[0] - 14, center[1] - int(radius * 0.95)),
                (center[0] - 6, center[1] - int(radius * 0.65)),
                (center[0] + 6, center[1] - int(radius * 0.65)),
                (center[0] + 14, center[1] - int(radius * 0.95))
            ]
            pygame.draw.polygon(surf, settings.LIME_GREEN, calyx_pts)

        elif fruit_type == "kiwi":
            # Fuzzy brown textured kiwi egg
            rect = pygame.Rect(center[0] - radius, center[1] - int(radius * 0.85), radius * 2, int(radius * 1.7))
            pygame.draw.ellipse(surf, info["skin"], rect)
            # Fuzzy texture flecks
            for _ in range(18):
                fx = center[0] + random.randint(-int(radius * 0.7), int(radius * 0.7))
                fy = center[1] + random.randint(-int(radius * 0.6), int(radius * 0.6))
                pygame.draw.circle(surf, (85, 55, 30), (fx, fy), 2)

        elif fruit_type == "coconut":
            # Textured brown shell
            pygame.draw.circle(surf, info["shell"], center, radius)
            pygame.draw.circle(surf, (85, 50, 30), center, radius - 4)

        else:
            pygame.draw.circle(surf, info.get("skin", settings.TROPICAL_ORANGE), center, radius)

        # 3D Specular Glossy Arc (Soft light from top-left)
        glint_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        glint_center = (center[0] - int(radius * 0.35), center[1] - int(radius * 0.35))
        glint_w = int(radius * 0.65)
        glint_h = int(radius * 0.38)
        glint_rect = pygame.Rect(0, 0, glint_w, glint_h)
        glint_rect.center = glint_center
        pygame.draw.ellipse(glint_surf, (255, 255, 255, 140), glint_rect)
        # Pinpoint glossy dot
        pygame.draw.circle(glint_surf, (255, 255, 255, 210), (glint_center[0] - 4, glint_center[1] - 4), max(2, radius // 12))

        surf.blit(glint_surf, (0, 0))
        cls._cache[key] = surf
        return surf

    @classmethod
    def get_half_surface(cls, fruit_type: str, is_left: bool, radius: int = 44) -> pygame.Surface:
        key = (fruit_type, radius, "half_left" if is_left else "half_right")
        if key in cls._cache:
            return cls._cache[key]

        diameter = radius * 2
        surf = pygame.Surface((diameter + 16, diameter + 16), pygame.SRCALPHA)
        center = (radius + 8, radius + 8)

        info = settings.FRUIT_COLORS.get(fruit_type, settings.FRUIT_COLORS["watermelon"])
        flesh_color = info.get("flesh", settings.TROPICAL_ORANGE)
        rind_color = info.get("skin", info.get("rind", (40, 120, 50)))

        # Outer hemisphere
        rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
        start_angle = math.pi * 0.5 if is_left else math.pi * 1.5
        end_angle = math.pi * 1.5 if is_left else math.pi * 2.5

        # Draw half outer skin
        points = [center]
        for step in range(25):
            a = start_angle + (end_angle - start_angle) * (step / 24.0)
            points.append((center[0] + math.cos(a) * radius, center[1] - math.sin(a) * radius))
        pygame.draw.polygon(surf, rind_color, points)

        # Draw juicy inner flesh
        inner_points = [center]
        inner_r = radius * 0.82
        for step in range(25):
            a = start_angle + (end_angle - start_angle) * (step / 24.0)
            inner_points.append((center[0] + math.cos(a) * inner_r, center[1] - math.sin(a) * inner_r))
        pygame.draw.polygon(surf, flesh_color, inner_points)

        # Seeds or pulp detailing
        if fruit_type == "watermelon":
            seed_color = info["seeds"]
            for s_step in [0.25, 0.5, 0.75]:
                sa = start_angle + (end_angle - start_angle) * s_step
                sr = radius * 0.5
                sx = center[0] + math.cos(sa) * sr
                sy = center[1] - math.sin(sa) * sr
                pygame.draw.circle(surf, seed_color, (int(sx), int(sy)), 3)
        elif fruit_type == "apple":
            # Core and seeds
            core_col = (230, 220, 195)
            pygame.draw.circle(surf, core_col, (int(center[0]), int(center[1])), int(radius * 0.35))
            pygame.draw.circle(surf, (60, 30, 20), (int(center[0] + (6 if is_left else -6)), int(center[1] - 4)), 3)
            pygame.draw.circle(surf, (60, 30, 20), (int(center[0] + (6 if is_left else -6)), int(center[1] + 4)), 3)
        elif fruit_type == "kiwi":
            # Cream white core and ring of black seeds
            core_col = (245, 250, 220)
            pygame.draw.ellipse(surf, core_col, (center[0] - 8, center[1] - 14, 16, 28))
            for i in range(12):
                sa = start_angle + (end_angle - start_angle) * (i / 11.0)
                sr = radius * 0.45
                sx = center[0] + math.cos(sa) * sr
                sy = center[1] - math.sin(sa) * sr
                pygame.draw.circle(surf, (30, 30, 30), (int(sx), int(sy)), 2)
        elif fruit_type == "strawberry":
            # Lighter pink inner radial lines
            for step in [0.2, 0.4, 0.6, 0.8]:
                sa = start_angle + (end_angle - start_angle) * step
                p_end = (center[0] + math.cos(sa) * radius * 0.6, center[1] - math.sin(sa) * radius * 0.6)
                pygame.draw.line(surf, (255, 180, 195), center, p_end, 2)
        elif fruit_type == "coconut":
            # Bright white coconut meat and hollow center
            pygame.draw.circle(surf, (25, 45, 38), center, int(radius * 0.55))
        elif fruit_type == "orange":
            # Citrus segments
            for step in [0.2, 0.4, 0.6, 0.8]:
                sa = start_angle + (end_angle - start_angle) * step
                p_end = (center[0] + math.cos(sa) * radius * 0.75, center[1] - math.sin(sa) * radius * 0.75)
                pygame.draw.line(surf, (255, 230, 180), center, p_end, 2)
        elif fruit_type == "dragonfruit":
            for _ in range(8):
                sa = random.uniform(start_angle, end_angle)
                sr = random.uniform(radius * 0.2, radius * 0.7)
                sx = center[0] + math.cos(sa) * sr
                sy = center[1] - math.sin(sa) * sr
                pygame.draw.circle(surf, (35, 35, 35), (int(sx), int(sy)), 2)

        # Sliced edge gloss line
        p_top = (center[0], center[1] - radius)
        p_bot = (center[0], center[1] + radius)
        pygame.draw.line(surf, (255, 255, 255, 160), p_top, p_bot, 2)

        cls._cache[key] = surf
        return surf


class FruitHalf(pygame.sprite.Sprite):
    """Halved fruit section flying apart after being sliced."""

    def __init__(self, fruit_type: str, x: float, y: float, vx: float, vy: float, is_left: bool, radius: int = 44):
        super().__init__()
        self.fruit_type = fruit_type
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.is_left = is_left
        self.radius = radius
        self.angle = 0.0
        self.rot_speed = random.uniform(-10.0, -4.0) if is_left else random.uniform(4.0, 10.0)
        self.gravity = settings.GRAVITY
        self.surface = FruitSpriteCache.get_half_surface(fruit_type, is_left, radius)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.rot_speed

    def draw(self, screen: pygame.Surface):
        rotated = pygame.transform.rotate(self.surface, self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated, rect)

    def is_offscreen(self, screen_h: int) -> bool:
        return self.y > screen_h + 80


class Fruit(pygame.sprite.Sprite):
    """Main sliceable fruit entity with 3D styling and realistic physics."""

    def __init__(self, fruit_type: str, x: float, y: float, vx: float, vy: float, radius: int = 44):
        super().__init__()
        self.fruit_type = fruit_type
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.is_sliced = False
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-4.5, 4.5)
        self.gravity = settings.GRAVITY
        self.surface = FruitSpriteCache.get_whole_surface(fruit_type, radius)

    def update(self):
        if not self.is_sliced:
            self.x += self.vx
            self.y += self.vy
            self.vy += self.gravity
            self.angle += self.rot_speed

    def draw(self, screen: pygame.Surface):
        if not self.is_sliced:
            rotated = pygame.transform.rotate(self.surface, self.angle)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect)

    def check_slice(self, p1: tuple, p2: tuple) -> bool:
        """Line segment vs fruit circle collision."""
        if self.is_sliced:
            return False

        # Segment from p1 to p2
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = self.x, self.y
        dx = x2 - x1
        dy = y2 - y1

        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq == 0:
            return math.hypot(cx - x1, cy - y1) <= self.radius

        t = max(0.0, min(1.0, ((cx - x1) * dx + (cy - y1) * dy) / seg_len_sq))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy

        dist = math.hypot(cx - proj_x, cy - proj_y)
        return dist <= self.radius

    def slice(self) -> list:
        """Splits fruit into two flying halves."""
        self.is_sliced = True
        half1 = FruitHalf(self.fruit_type, self.x - 10, self.y, self.vx - 3.5, self.vy - 1.5, True, self.radius)
        half2 = FruitHalf(self.fruit_type, self.x + 10, self.y, self.vx + 3.5, self.vy - 1.5, False, self.radius)
        return [half1, half2]

    def is_offscreen(self, screen_h: int) -> bool:
        return self.y > screen_h + 80 and self.vy > 0


class Bomb(pygame.sprite.Sprite):
    """Hazard entity - 3D metallic sphere with animated flaming fuse."""

    def __init__(self, x: float, y: float, vx: float, vy: float, radius: int = 40):
        super().__init__()
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.is_exploded = False
        self.angle = 0.0
        self.rot_speed = random.uniform(-2.5, 2.5)
        self.gravity = settings.GRAVITY
        self.fuse_frame = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.rot_speed
        self.fuse_frame = (self.fuse_frame + 1) % 60

    def draw(self, screen: pygame.Surface):
        if self.is_exploded:
            return

        cx, cy = int(self.x), int(self.y)
        r = self.radius

        # 1. 3D Metallic Slate Sphere
        bomb_surf = pygame.Surface((r * 2 + 20, r * 2 + 20), pygame.SRCALPHA)
        b_center = (r + 10, r + 10)

        # Shaded metallic dark body
        pygame.draw.circle(bomb_surf, (35, 38, 44), b_center, r)
        pygame.draw.circle(bomb_surf, (22, 24, 28), b_center, r - 3)

        # Metallic collar
        pygame.draw.rect(bomb_surf, (80, 85, 95), (b_center[0] - 8, b_center[1] - r - 6, 16, 7), border_radius=2)

        # 3D Specular Highlight
        glint_center = (b_center[0] - int(r * 0.35), b_center[1] - int(r * 0.35))
        pygame.draw.ellipse(bomb_surf, (255, 255, 255, 110), (glint_center[0] - 8, glint_center[1] - 5, 18, 10))

        # Tropical Danger Crossbones / Hazard Icon in Watermelon Pink
        warn_col = settings.WATERMELON_PINK
        pygame.draw.circle(bomb_surf, warn_col, (b_center[0], b_center[1] - 2), 6)
        pygame.draw.polygon(bomb_surf, warn_col, [
            (b_center[0] - 6, b_center[1] + 6),
            (b_center[0] + 6, b_center[1] + 6),
            (b_center[0], b_center[1] + 12)
        ])

        screen.blit(bomb_surf, (cx - b_center[0], cy - b_center[1]))

        # 2. Glowing Animated Fuse Spark
        fuse_tip_x = cx + int(math.sin(self.fuse_frame * 0.2) * 5)
        fuse_tip_y = cy - r - 12
        pygame.draw.circle(screen, settings.MANGO_YELLOW, (fuse_tip_x, fuse_tip_y), random.randint(4, 7))
        pygame.draw.circle(screen, settings.TROPICAL_ORANGE, (fuse_tip_x, fuse_tip_y), random.randint(2, 4))
        pygame.draw.circle(screen, settings.WHITE, (fuse_tip_x, fuse_tip_y), 2)

    def check_slice(self, p1: tuple, p2: tuple) -> bool:
        if self.is_exploded:
            return False
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq == 0:
            return math.hypot(self.x - x1, self.y - y1) <= self.radius
        t = max(0.0, min(1.0, ((self.x - x1) * dx + (self.y - y1) * dy) / seg_len_sq))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(self.x - proj_x, self.y - proj_y) <= self.radius

    def is_offscreen(self, screen_h: int) -> bool:
        return self.y > screen_h + 80 and self.vy > 0
