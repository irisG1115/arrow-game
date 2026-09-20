import pygame
import sys
import math
import random

pygame.init()

# ==================== 常量 ====================
CELL = 80
MARGIN = 40
INFO_H = 130
GRID_W = 5
GRID_H = 5
WIDTH = GRID_W * CELL + MARGIN * 2
HEIGHT = GRID_H * CELL + MARGIN * 2 + INFO_H
FPS = 60

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK = (50, 50, 50)
BLUE = (70, 130, 180)
GREEN = (60, 180, 100)
RED = (220, 80, 80)
YELLOW = (240, 200, 60)
BG = (245, 245, 245)

# 方向编码
UP, RIGHT, DOWN, LEFT = 1, 2, 3, 4

# 四季主题
SEASONS = {
    "spring": {
        "name": "春",
        "full": "春暖花开",
        "sky": ((180, 230, 210), (255, 235, 245)),
        "particle": "petals",
        "sun": True,
        "clouds": "light",
        "grass": (130, 205, 130),
        "arrow": {
            UP:    ((95, 195, 125),  (200, 240, 210)),
            RIGHT: ((240, 145, 175), (255, 210, 225)),
            DOWN:  ((80, 185, 120),  (185, 235, 200)),
            LEFT:  ((220, 125, 165), (250, 200, 218)),
        },
        "flower_colors": [(255, 183, 197), (255, 200, 215), (255, 160, 185), (255, 220, 230)],
    },
    "summer": {
        "name": "夏",
        "full": "夏日晴空",
        "sky": ((100, 180, 255), (255, 245, 200)),
        "particle": None,
        "sun": True,
        "clouds": "light",
        "grass": (70, 165, 75),
        "arrow": {
            UP:    ((50, 145, 230),  (160, 218, 255)),
            RIGHT: ((255, 188, 45),  (255, 228, 140)),
            DOWN:  ((40, 175, 105),  (150, 228, 180)),
            LEFT:  ((228, 115, 178), (255, 190, 220)),
        },
        "flower_colors": [(255, 208, 55), (255, 178, 28), (255, 230, 110)],
    },
    "autumn": {
        "name": "秋",
        "full": "金秋落叶",
        "sky": ((255, 180, 95), (235, 105, 50)),
        "particle": "leaves",
        "sun": False,
        "clouds": "light",
        "grass": (175, 135, 55),
        "arrow": {
            UP:    ((222, 100, 38), (255, 178, 118)),
            RIGHT: ((200, 55, 35),  (240, 138, 108)),
            DOWN:  ((178, 108, 28), (230, 168, 88)),
            LEFT:  ((212, 78, 58),  (245, 148, 128)),
        },
        "flower_colors": [(222, 88, 28), (198, 48, 28), (240, 158, 38), (180, 60, 30)],
    },
    "winter": {
        "name": "冬",
        "full": "瑞雪丰年",
        "sky": ((198, 218, 238), (240, 248, 255)),
        "particle": "snow",
        "sun": False,
        "clouds": "light",
        "grass": (222, 235, 245),
        "arrow": {
            UP:    ((98, 158, 218),  (180, 218, 248)),
            RIGHT: ((138, 188, 228), (208, 232, 252)),
            DOWN:  ((78, 138, 198),  (158, 198, 238)),
            LEFT:  ((118, 168, 213), (193, 222, 247)),
        },
        "flower_colors": [(222, 58, 78), (240, 98, 118), (255, 255, 255)],
    },
}

# 关卡数据
levels = [
    {   # 春
        "grid": [
            [0, 0, RIGHT, 0, 0],
            [0, 0, UP, 0, 0],
            [RIGHT, RIGHT, RIGHT, RIGHT, RIGHT],
            [0, 0, DOWN, 0, 0],
            [0, 0, LEFT, 0, 0],
        ],
        "mistakes": 3,
        "season": "spring",
    },
    {   # 夏
        "grid": [
            [RIGHT, 0, 0, 0, UP],
            [0, UP, 0, UP, 0],
            [DOWN, 0, RIGHT, 0, UP],
            [0, DOWN, 0, DOWN, 0],
            [RIGHT, 0, 0, 0, DOWN],
        ],
        "mistakes": 4,
        "season": "summer",
    },
    {   # 秋
        "grid": [
            [UP, 0, LEFT, 0, UP],
            [0, DOWN, 0, DOWN, 0],
            [RIGHT, 0, 0, 0, RIGHT],
            [0, DOWN, 0, DOWN, 0],
            [DOWN, 0, 0, 0, DOWN],
        ],
        "mistakes": 4,
        "season": "autumn",
    },
    {   # 冬
        "grid": [
            [UP, 0, RIGHT, 0, UP],
            [0, DOWN, 0, DOWN, 0],
            [LEFT, 0, 0, 0, RIGHT],
            [0, DOWN, 0, RIGHT, 0],
            [0, LEFT, 0, RIGHT, 0],
        ],
        "mistakes": 5,
        "season": "winter",
    },
]


# ==================== 辅助绘制函数 ====================
def draw_gradient_rect(surface, rect, color_top, color_bottom):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(h - 1, 1)
        r = int(color_top[0] * (1 - t) + color_bottom[0] * t)
        g = int(color_top[1] * (1 - t) + color_bottom[1] * t)
        b = int(color_top[2] * (1 - t) + color_bottom[2] * t)
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return (int(lerp(c1[0], c2[0], t)), int(lerp(c1[1], c2[1], t)), int(lerp(c1[2], c2[2], t)))


# ==================== 粒子系统 ====================
class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=4, gravity=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt

    @property
    def alive(self):
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, self.life / self.max_life)
        s = max(1, int(self.size * alpha))
        col = self.color
        surf = pygame.Surface((s * 2 + 2, s * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*col, int(255 * alpha)), (s + 1, s + 1), s)
        surface.blit(surf, (self.x - s - 1, self.y - s - 1))


class WeatherParticle:
    def __init__(self, kind):
        self.kind = kind
        self.reset()

    def reset(self):
        self.x = random.uniform(-20, WIDTH + 20)
        self.y = random.uniform(-HEIGHT, 0)
        self.rot = random.uniform(0, math.tau)
        if self.kind == "snow":
            self.speed = random.uniform(40, 95)
            self.size = random.uniform(1.5, 4)
            self.alpha = random.randint(180, 255)
            self.drift = random.uniform(-15, 15)
            self.phase = random.uniform(0, math.tau)
            self.rot_speed = 0
        elif self.kind == "petals":
            self.speed = random.uniform(50, 110)
            self.size = random.uniform(4, 8)
            self.alpha = random.randint(180, 240)
            self.drift = random.uniform(-25, 25)
            self.phase = random.uniform(0, math.tau)
            self.rot_speed = random.uniform(-2, 2)
            self.color = random.choice([(255, 183, 197), (255, 200, 215), (255, 160, 185)])
        else:
            self.speed = random.uniform(70, 140)
            self.size = random.uniform(5, 9)
            self.alpha = random.randint(180, 240)
            self.drift = random.uniform(-35, 35)
            self.phase = random.uniform(0, math.tau)
            self.rot_speed = random.uniform(-3, 3)
            self.color = random.choice([(222, 88, 28), (198, 48, 28), (240, 158, 38), (180, 60, 30)])

    def update(self, dt):
        self.y += self.speed * dt
        self.phase += dt * 2
        self.rot += self.rot_speed * dt
        self.x += math.sin(self.phase) * self.drift * dt
        if self.y > HEIGHT + 20 or self.x < -30 or self.x > WIDTH + 30:
            self.reset()

    def draw(self, surface):
        if self.kind == "snow":
            pygame.draw.circle(surface, (255, 255, 255, self.alpha),
                               (int(self.x), int(self.y)), int(self.size))
        else:
            s = self.size
            surf = pygame.Surface((int(s * 4), int(s * 4)), pygame.SRCALPHA)
            if self.kind == "petals":
                pygame.draw.ellipse(surf, (*self.color, self.alpha),
                                    pygame.Rect(s, s * 0.4, s * 1.6, s * 2.4))
            else:
                pygame.draw.ellipse(surf, (*self.color, self.alpha),
                                    pygame.Rect(s * 0.6, s * 0.6, s * 2.2, s * 2.2))
                pygame.draw.line(surf, (*self.color, self.alpha),
                                 (s * 1.7, s * 0.6), (s * 1.7, s * 2.8), 1)
            rotated = pygame.transform.rotate(surf, math.degrees(self.rot))
            surface.blit(rotated, rotated.get_rect(center=(int(self.x), int(self.y))))


class Flower:
    def __init__(self, x, y, season, colors, size=14):
        self.x = x
        self.y = y
        self.season = season
        self.colors = colors
        self.color = random.choice(colors)
        self.size = size
        self.phase = random.uniform(0, math.tau)
        self.speed = random.uniform(0.8, 1.6)
        self.has_stem = season != "winter" or random.random() < 0.4

    def update(self, dt):
        self.phase += self.speed * dt

    def draw(self, surface):
        sway = math.sin(self.phase) * 3
        cx = self.x + sway
        cy = self.y
        s = self.size

        if self.season == "spring":
            pygame.draw.line(surface, (60, 140, 60), (self.x, self.y), (self.x, self.y + 16), 2)
            for i in range(5):
                ang = i * (math.tau / 5) + self.phase * 0.2
                px = cx + math.cos(ang) * s * 0.7
                py = cy + math.sin(ang) * s * 0.7
                pygame.draw.circle(surface, self.color, (int(px), int(py)), int(s * 0.5))
            pygame.draw.circle(surface, (255, 220, 80), (int(cx), int(cy)), int(s * 0.3))

        elif self.season == "summer":
            pygame.draw.line(surface, (60, 130, 50), (self.x, self.y), (self.x, self.y + 18), 3)
            for i in range(10):
                ang = i * (math.tau / 10)
                px = cx + math.cos(ang) * s * 0.8
                py = cy + math.sin(ang) * s * 0.8
                ellipse_surf = pygame.Surface((int(s * 0.8), int(s * 1.4)), pygame.SRCALPHA)
                pygame.draw.ellipse(ellipse_surf, self.color, ellipse_surf.get_rect())
                rot = pygame.transform.rotate(ellipse_surf, -math.degrees(ang))
                surface.blit(rot, rot.get_rect(center=(int(px), int(py))))
            pygame.draw.circle(surface, (120, 70, 30), (int(cx), int(cy)), int(s * 0.45))

        elif self.season == "autumn":
            pygame.draw.line(surface, (110, 75, 35), (self.x, self.y), (self.x, self.y + 14), 2)
            for i in range(5):
                ang = i * (math.tau / 5) - math.pi / 2
                px = cx + math.cos(ang) * s * 1.1
                py = cy + math.sin(ang) * s * 1.1
                pygame.draw.polygon(surface, self.color,
                                    [(int(cx), int(cy)),
                                     (int(cx + math.cos(ang - 0.3) * s * 0.5),
                                      int(cy + math.sin(ang - 0.3) * s * 0.5)),
                                     (int(px), int(py)),
                                     (int(cx + math.cos(ang + 0.3) * s * 0.5),
                                      int(cy + math.sin(ang + 0.3) * s * 0.5))])
            pygame.draw.circle(surface, (140, 50, 20), (int(cx), int(cy)), int(s * 0.2))

        else:
            if self.has_stem:
                pygame.draw.line(surface, (120, 130, 140), (self.x, self.y), (self.x, self.y + 12), 2)
            for i in range(5):
                ang = i * (math.tau / 5)
                px = cx + math.cos(ang) * s * 0.65
                py = cy + math.sin(ang) * s * 0.65
                pygame.draw.circle(surface, self.color, (int(px), int(py)), int(s * 0.45))
            if self.color != (255, 255, 255):
                pygame.draw.circle(surface, (180, 40, 55), (int(cx), int(cy)), int(s * 0.18))


class Cloud:
    def __init__(self, y, speed, scale):
        self.x = random.uniform(-200, WIDTH + 200)
        self.y = y
        self.speed = speed
        self.scale = scale

    def update(self, dt):
        self.x += self.speed * dt
        if self.x > WIDTH + 250:
            self.x = -250

    def draw(self, surface, color=(255, 255, 255, 200)):
        s = self.scale
        base = pygame.Surface((200 * s, 80 * s), pygame.SRCALPHA)
        for (cx, cy, r) in [(40, 45, 28), (80, 35, 35), (120, 38, 32), (155, 46, 26), (95, 52, 30)]:
            pygame.draw.circle(base, color, (int(cx * s), int(cy * s)), int(r * s))
        surface.blit(base, (self.x, self.y))


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, INFO_H + MARGIN)
        self.size = random.uniform(0.8, 2.2)
        self.phase = random.uniform(0, math.tau)
        self.speed = random.uniform(1, 3)

    def update(self, dt):
        self.phase += self.speed * dt

    def draw(self, surface):
        alpha = int(150 + 100 * (0.5 + 0.5 * math.sin(self.phase)))
        pygame.draw.circle(surface, (255, 255, 220, alpha),
                           (self.x, self.y), int(self.size))


# ==================== 游戏主类 ====================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("一箭又一箭 · 四季版")
        self.clock = pygame.time.Clock()

        font_path = "C:/Windows/Fonts/msyh.ttc"
        self.font = pygame.font.Font(font_path, 28)
        self.small_font = pygame.font.Font(font_path, 22)
        self.big_font = pygame.font.Font(font_path, 52)
        self.tiny_font = pygame.font.Font(font_path, 18)

        self.state = "START"
        self.level_index = 0
        self.grid = []
        self.mistakes = 0
        self.max_mistakes = 0
        self.animations = []
        self.collision_effects = []
        self.particles = []
        self.weather_particles = []
        self.flowers = []
        self.clouds = []
        self.stars = []
        self.season = "spring"
        self.shake_timer = 0.0
        self.shake_amp = 0.0
        self.time = 0.0
        self.mouse_pos = (0, 0)
        self.flash_timer = 0.0

        self.board_x = MARGIN
        self.board_y = INFO_H + MARGIN

        self.start_btn = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 60, 220, 64)
        # 重新开始按钮放在右上角
        self.restart_btn = pygame.Rect(WIDTH - 150, 15, 135, 48)
        self.next_btn = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 80, 220, 64)
        self.retry_btn = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 80, 220, 64)
        self.restart_all_btn = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 80, 220, 64)

        self.clouds = [
            Cloud(40, 12, 0.8),
            Cloud(90, 18, 0.6),
            Cloud(150, 8, 1.0),
            Cloud(20, 22, 0.5),
        ]
        self.stars = [Star() for _ in range(60)]
        self.load_level(0)
        self.state = "START"

    def _build_flowers(self, season):
        colors = SEASONS[season]["flower_colors"]
        self.flowers = []
        step = 46 if season == "winter" else 34
        back_step = 70 if season == "winter" else 58
        for x in range(15, WIDTH, step):
            self.flowers.append(Flower(x, HEIGHT - 22, season, colors, random.uniform(10, 15)))
        for x in range(35, WIDTH, back_step):
            self.flowers.append(Flower(x, HEIGHT - 10, season, colors, random.uniform(8, 12)))

    def _setup_season(self, season):
        self.season = season
        theme = SEASONS[season]
        self._build_flowers(season)
        self.weather_particles = []
        ptype = theme["particle"]
        if ptype == "snow":
            for _ in range(90):
                p = WeatherParticle("snow")
                p.y = random.uniform(0, HEIGHT)
                self.weather_particles.append(p)
        elif ptype == "petals":
            for _ in range(70):
                p = WeatherParticle("petals")
                p.y = random.uniform(0, HEIGHT)
                self.weather_particles.append(p)
        elif ptype == "leaves":
            for _ in range(80):
                p = WeatherParticle("leaves")
                p.y = random.uniform(0, HEIGHT)
                self.weather_particles.append(p)

    def load_level(self, index):
        self.level_index = index
        data = levels[index]
        self.grid = [row[:] for row in data["grid"]]
        self.max_mistakes = data["mistakes"]
        self.mistakes = 0
        self.animations = []
        self.collision_effects = []
        self.particles = []
        self.shake_timer = 0.0
        self.flash_timer = 0.0
        self._setup_season(data["season"])
        self.state = "PLAYING"

    def is_blocked(self, r, c, direction):
        if direction == UP:
            for rr in range(r - 1, -1, -1):
                if self.grid[rr][c] != 0:
                    return True
        elif direction == DOWN:
            for rr in range(r + 1, GRID_H):
                if self.grid[rr][c] != 0:
                    return True
        elif direction == LEFT:
            for cc in range(c - 1, -1, -1):
                if self.grid[r][cc] != 0:
                    return True
        elif direction == RIGHT:
            for cc in range(c + 1, GRID_W):
                if self.grid[r][cc] != 0:
                    return True
        return False

    def click_board(self, pos):
        mx, my = pos
        if not (self.board_x <= mx < self.board_x + GRID_W * CELL and
                self.board_y <= my < self.board_y + GRID_H * CELL):
            return

        c = (mx - self.board_x) // CELL
        r = (my - self.board_y) // CELL
        if r < 0 or r >= GRID_H or c < 0 or c >= GRID_W:
            return

        direction = self.grid[r][c]
        if direction == 0:
            return

        cx = self.board_x + c * CELL + CELL // 2
        cy = self.board_y + r * CELL + CELL // 2

        if not self.is_blocked(r, c, direction):
            self.grid[r][c] = 0
            self.animations.append({
                "r": r, "c": c, "dir": direction,
                "progress": 0.0, "speed": 3.2, "cx": cx, "cy": cy,
                "draw_x": cx, "draw_y": cy,
            })
            col = SEASONS[self.season]["arrow"][direction][0]
            for _ in range(18):
                ang = random.uniform(0, math.tau)
                spd = random.uniform(80, 220)
                self.particles.append(Particle(
                    cx, cy,
                    math.cos(ang) * spd, math.sin(ang) * spd,
                    col, random.uniform(0.4, 0.8), random.randint(3, 6), gravity=200
                ))
        else:
            self.mistakes += 1
            self.collision_effects.append({"r": r, "c": c, "timer": 0.5})
            self.shake_timer = 0.3
            self.shake_amp = 8
            for _ in range(12):
                ang = random.uniform(0, math.tau)
                spd = random.uniform(60, 160)
                self.particles.append(Particle(
                    cx, cy,
                    math.cos(ang) * spd, math.sin(ang) * spd,
                    RED, random.uniform(0.3, 0.6), random.randint(2, 5)
                ))
            if self.mistakes >= self.max_mistakes:
                self.state = "GAME_OVER"

    def update(self, dt):
        self.time += dt

        for f in self.flowers:
            f.update(dt)
        for cl in self.clouds:
            cl.update(dt)
        for s in self.stars:
            s.update(dt)
        for wp in self.weather_particles:
            wp.update(dt)

        for p in self.particles[:]:
            p.update(dt)
            if not p.alive:
                self.particles.remove(p)

        for anim in self.animations[:]:
            anim["progress"] += anim["speed"] * dt
            if random.random() < 0.6:
                col = SEASONS[self.season]["arrow"][anim["dir"]][0]
                dx = anim.get("draw_x", anim["cx"])
                dy = anim.get("draw_y", anim["cy"])
                self.particles.append(Particle(
                    dx, dy,
                    random.uniform(-20, 20), random.uniform(-20, 20),
                    col, random.uniform(0.2, 0.4), random.randint(2, 4)
                ))
            if anim["progress"] >= 1.0:
                self.animations.remove(anim)

        for eff in self.collision_effects[:]:
            eff["timer"] -= dt
            if eff["timer"] <= 0:
                self.collision_effects.remove(eff)

        if self.shake_timer > 0:
            self.shake_timer -= dt

        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.state == "PLAYING":
            if all(x == 0 for row in self.grid for x in row) and not self.animations:
                self.flash_timer = 0.6
                if self.level_index == len(levels) - 1:
                    self.state = "ALL_CLEAR"
                else:
                    self.state = "LEVEL_CLEAR"

    def draw_background(self):
        theme = SEASONS[self.season]
        draw_gradient_rect(self.screen, (0, 0, WIDTH, HEIGHT),
                           theme["sky"][0], theme["sky"][1])

        if theme.get("sun"):
            pygame.draw.circle(self.screen, (255, 240, 150), (WIDTH - 80, 70), 36)
            pygame.draw.circle(self.screen, (255, 250, 200), (WIDTH - 80, 70), 28)
            glow = pygame.Surface((160, 160), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 240, 150, 40), (80, 80), 70)
            self.screen.blit(glow, (WIDTH - 160, -10))

        cloud_mode = theme.get("clouds", "none")
        if cloud_mode != "none":
            cloud_color = (255, 255, 255, 180)
            if self.season == "autumn":
                cloud_color = (255, 230, 200, 170)
            elif self.season == "winter":
                cloud_color = (235, 242, 250, 200)
            for cl in self.clouds:
                cl.draw(self.screen, cloud_color)

        if self.weather_particles:
            wp_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for wp in self.weather_particles:
                wp.draw(wp_layer)
            self.screen.blit(wp_layer, (0, 0))

        ground_h = 32
        ground_y = HEIGHT - ground_h
        grass = theme["grass"]
        ground_surf = pygame.Surface((WIDTH, ground_h), pygame.SRCALPHA)
        pygame.draw.rect(ground_surf, (*grass, 230), ground_surf.get_rect())
        pygame.draw.line(ground_surf, (*lerp_color(grass, WHITE, 0.3), 230),
                         (0, 0), (WIDTH, 0), 3)
        self.screen.blit(ground_surf, (0, ground_y))

        flower_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for f in self.flowers:
            f.draw(flower_layer)
        self.screen.blit(flower_layer, (0, 0))

    def draw_arrow(self, surface, cx, cy, direction, color_main, color_light, scale=1.0, glow=True, season=None):
        s = CELL * 0.32 * scale
        if glow:
            glow_surf = pygame.Surface((int(s * 4), int(s * 4)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color_main, 70),
                               (int(s * 2), int(s * 2)), int(s * 1.6))
            surface.blit(glow_surf, (cx - int(s * 2), cy - int(s * 2)))

        main = color_main
        light = color_light

        tail_x, tail_y = cx, cy
        if direction == UP:
            pygame.draw.polygon(surface, main,
                                [(cx, cy - s), (cx - s, cy + s * 0.3), (cx + s, cy + s * 0.3)])
            pygame.draw.polygon(surface, light,
                                [(cx, cy - s), (cx - s * 0.4, cy + s * 0.1), (cx + s * 0.1, cy + s * 0.1)])
            pygame.draw.rect(surface, main,
                             (cx - s * 0.25, cy + s * 0.2, s * 0.5, s * 0.7), border_radius=3)
            tail_x, tail_y = cx, cy + s * 0.9
        elif direction == DOWN:
            pygame.draw.polygon(surface, main,
                                [(cx, cy + s), (cx - s, cy - s * 0.3), (cx + s, cy - s * 0.3)])
            pygame.draw.polygon(surface, light,
                                [(cx, cy + s), (cx - s * 0.4, cy - s * 0.1), (cx + s * 0.1, cy - s * 0.1)])
            pygame.draw.rect(surface, main,
                             (cx - s * 0.25, cy - s * 0.9, s * 0.5, s * 0.7), border_radius=3)
            tail_x, tail_y = cx, cy - s * 0.9
        elif direction == LEFT:
            pygame.draw.polygon(surface, main,
                                [(cx - s, cy), (cx + s * 0.3, cy - s), (cx + s * 0.3, cy + s)])
            pygame.draw.polygon(surface, light,
                                [(cx - s, cy), (cx + s * 0.1, cy - s * 0.4), (cx + s * 0.1, cy + s * 0.1)])
            pygame.draw.rect(surface, main,
                             (cx + s * 0.2, cy - s * 0.25, s * 0.7, s * 0.5), border_radius=3)
            tail_x, tail_y = cx + s * 0.9, cy
        elif direction == RIGHT:
            pygame.draw.polygon(surface, main,
                                [(cx + s, cy), (cx - s * 0.3, cy - s), (cx - s * 0.3, cy + s)])
            pygame.draw.polygon(surface, light,
                                [(cx + s, cy), (cx - s * 0.1, cy - s * 0.4), (cx - s * 0.1, cy + s * 0.1)])
            pygame.draw.rect(surface, main,
                             (cx - s * 0.9, cy - s * 0.25, s * 0.7, s * 0.5), border_radius=3)
            tail_x, tail_y = cx - s * 0.9, cy

        if season:
            self._draw_season_accent(surface, tail_x, tail_y, season, s * 0.42)

    def _draw_season_accent(self, surface, x, y, season, r):
        if season == "spring":
            for i in range(5):
                ang = i * (math.tau / 5)
                px = x + math.cos(ang) * r * 0.7
                py = y + math.sin(ang) * r * 0.7
                pygame.draw.circle(surface, (255, 170, 195), (int(px), int(py)), int(r * 0.45))
            pygame.draw.circle(surface, (255, 220, 80), (int(x), int(y)), int(r * 0.25))
        elif season == "summer":
            pygame.draw.circle(surface, (255, 210, 60), (int(x), int(y)), int(r * 0.7))
            for i in range(8):
                ang = i * (math.tau / 8)
                x1 = x + math.cos(ang) * r * 0.85
                y1 = y + math.sin(ang) * r * 0.85
                x2 = x + math.cos(ang) * r * 1.25
                y2 = y + math.sin(ang) * r * 1.25
                pygame.draw.line(surface, (255, 180, 40), (x1, y1), (x2, y2), 2)
        elif season == "autumn":
            pts = []
            for i in range(5):
                ang = i * (math.tau / 5) - math.pi / 2
                pts.append((x + math.cos(ang) * r, y + math.sin(ang) * r))
            pygame.draw.polygon(surface, (220, 90, 30),
                                [(x, y)] + [(int(p[0]), int(p[1])) for p in pts])
        else:
            for i in range(6):
                ang = i * (math.tau / 6)
                x2 = x + math.cos(ang) * r
                y2 = y + math.sin(ang) * r
                pygame.draw.line(surface, (230, 240, 255), (x, y), (int(x2), int(y2)), 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(x), int(y)), int(r * 0.25))

    # ============ 新增：手绘季节图标（替代 emoji，避免显示成方框） ============
    def draw_season_icon(self, x, y, season, r):
        """在 (x, y) 处绘制一个半径为 r 的季节小图标"""
        if season == "spring":
            # 粉樱花
            for i in range(5):
                ang = i * (math.tau / 5) - math.pi / 2
                px = x + math.cos(ang) * r * 0.75
                py = y + math.sin(ang) * r * 0.75
                pygame.draw.circle(self.screen, (255, 150, 185), (int(px), int(py)), int(r * 0.55))
            pygame.draw.circle(self.screen, (255, 220, 80), (int(x), int(y)), int(r * 0.32))
        elif season == "summer":
            # 太阳
            pygame.draw.circle(self.screen, (255, 200, 60), (int(x), int(y)), int(r * 0.7))
            for i in range(8):
                ang = i * (math.tau / 8)
                x1 = x + math.cos(ang) * r * 0.85
                y1 = y + math.sin(ang) * r * 0.85
                x2 = x + math.cos(ang) * r * 1.25
                y2 = y + math.sin(ang) * r * 1.25
                pygame.draw.line(self.screen, (255, 170, 40), (x1, y1), (x2, y2), 2)
        elif season == "autumn":
            # 枫叶：五角星形
            pts = []
            for i in range(10):
                ang = i * (math.tau / 10) - math.pi / 2
                rr = r * (1.15 if i % 2 == 0 else 0.5)
                pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
            pygame.draw.polygon(self.screen, (215, 85, 30),
                                [(int(px), int(py)) for px, py in pts])
            pygame.draw.circle(self.screen, (150, 55, 20), (int(x), int(y)), max(1, int(r * 0.15)))
        else:
            # 六角雪花
            col = (120, 165, 215)
            for i in range(6):
                ang = i * (math.tau / 6)
                ex = x + math.cos(ang) * r
                ey = y + math.sin(ang) * r
                pygame.draw.line(self.screen, col, (int(x), int(y)), (int(ex), int(ey)), 2)
                # 侧枝
                for side in (-1, 1):
                    bx = x + math.cos(ang) * r * 0.55 + math.cos(ang + side * 1.2) * r * 0.35
                    by = y + math.sin(ang) * r * 0.55 + math.sin(ang + side * 1.2) * r * 0.35
                    mx = x + math.cos(ang) * r * 0.55
                    my = y + math.sin(ang) * r * 0.55
                    pygame.draw.line(self.screen, col, (int(mx), int(my)), (int(bx), int(by)), 1)
            pygame.draw.circle(self.screen, (200, 225, 245), (int(x), int(y)), max(1, int(r * 0.25)))

    def draw_button(self, rect, text, base_color, hover=True):
        color = base_color
        if hover and rect.collidepoint(self.mouse_pos):
            color = lerp_color(base_color, WHITE, 0.25)
        shadow = rect.copy()
        shadow.y += 4
        pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow, border_radius=10)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, lerp_color(base_color, BLACK, 0.3), rect, 2, border_radius=10)
        hl = pygame.Rect(rect.x + 4, rect.y + 4, rect.width - 8, rect.height // 3)
        hl_surf = pygame.Surface((hl.width, hl.height), pygame.SRCALPHA)
        pygame.draw.rect(hl_surf, (255, 255, 255, 70), hl_surf.get_rect(), border_radius=8)
        self.screen.blit(hl_surf, hl.topleft)
        txt = self.font.render(text, True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw_heart(self, x, y, size, filled, color=(220, 70, 90)):
        if not filled:
            color = (80, 80, 80)
        pts = []
        for i in range(20):
            t = i / 19 * math.tau
            hx = 16 * math.sin(t) ** 3
            hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((x + hx * size / 16, y + hy * size / 16))
        pygame.draw.polygon(self.screen, color, pts)

    def draw_start(self):
        title = self.big_font.render("一箭又一箭", True, DARK)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110)))
        sub = self.small_font.render("四 季 版", True, (180, 100, 160))
        self.screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

        tip = self.small_font.render("点击箭头，让它沿方向飞出棋盘", True, DARK)
        self.screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))
        tip2 = self.tiny_font.render("前方有箭头阻挡则不能飞出，并扣一次失误", True, (90, 90, 90))
        self.screen.blit(tip2, tip2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 22)))

        self.draw_button(self.start_btn, "开 始 游 戏", GREEN)

    def draw_playing(self):
        # 信息栏背景
        info_surf = pygame.Surface((WIDTH, INFO_H), pygame.SRCALPHA)
        info_surf.fill((255, 255, 255, 150))
        self.screen.blit(info_surf, (0, 0))

        # ---------- 第一行：关卡 | 剩余箭头 | 重新开始按钮 ----------
        level_text = self.font.render(f"关卡 {self.level_index + 1}/{len(levels)}", True, DARK)
        self.screen.blit(level_text, (20, 12))

        remain = sum(1 for row in self.grid for x in row if x != 0)
        remain_text = self.small_font.render(f"剩余箭头：{remain}", True, DARK)
        self.screen.blit(remain_text, (170, 20))

        self.draw_button(self.restart_btn, "重新开始", YELLOW)

        # ---------- 第二行：季节图标+文字 | 失误次数+心形 ----------
        season_info = SEASONS[self.season]
        # 手绘季节图标（不用 emoji）
        self.draw_season_icon(22, 82, self.season, 9)
        season_text = self.small_font.render(season_info['full'], True, (80, 80, 110))
        self.screen.blit(season_text, (42, 70))

        # 失误次数
        mistake_label = self.small_font.render("失误次数", True, DARK)
        self.screen.blit(mistake_label, (170, 70))
        for i in range(self.max_mistakes):
            filled = i < (self.max_mistakes - self.mistakes)
            self.draw_heart(258 + i * 24, 80, 11, filled)

        # ---------- 棋盘 ----------
        shake_x = shake_y = 0
        if self.shake_timer > 0:
            shake_x = random.uniform(-self.shake_amp, self.shake_amp)
            shake_y = random.uniform(-self.shake_amp, self.shake_amp)

        board_surf = pygame.Surface((GRID_W * CELL, GRID_H * CELL), pygame.SRCALPHA)
        pygame.draw.rect(board_surf, (255, 255, 255, 210), board_surf.get_rect(), border_radius=12)
        for r in range(GRID_H):
            for c in range(GRID_W):
                rect = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
                cell_color = (255, 255, 255, 180) if (r + c) % 2 == 0 else (240, 245, 250, 200)
                pygame.draw.rect(board_surf, cell_color, rect)
                pygame.draw.rect(board_surf, (180, 195, 210, 150), rect, 1)
        pygame.draw.rect(board_surf, (120, 140, 160, 200), board_surf.get_rect(), 3, border_radius=12)

        # 静态箭头 + 碰撞晃动
        for r in range(GRID_H):
            for c in range(GRID_W):
                if self.grid[r][c] != 0:
                    offset_x = 0
                    color_main, color_light = SEASONS[self.season]["arrow"][self.grid[r][c]]
                    for eff in self.collision_effects:
                        if eff["r"] == r and eff["c"] == c:
                            offset_x = 6 * math.sin(eff["timer"] * 50)
                            color_main = RED
                            color_light = (255, 180, 180)
                    cx = c * CELL + CELL // 2 + offset_x
                    cy = r * CELL + CELL // 2
                    self.draw_arrow(board_surf, cx, cy, self.grid[r][c],
                                    color_main, color_light, season=self.season)

        self.screen.blit(board_surf, (self.board_x + shake_x, self.board_y + shake_y))

        # 飞出动画
        for anim in self.animations:
            r, c, direction = anim["r"], anim["c"], anim["dir"]
            progress = anim["progress"]
            base_cx = self.board_x + c * CELL + CELL // 2
            base_cy = self.board_y + r * CELL + CELL // 2
            dist = CELL * 7 * progress
            cx, cy = base_cx, base_cy
            if direction == UP:
                cy -= dist
            elif direction == DOWN:
                cy += dist
            elif direction == LEFT:
                cx -= dist
            elif direction == RIGHT:
                cx += dist
            anim["draw_x"] = cx
            anim["draw_y"] = cy
            color_main, color_light = SEASONS[self.season]["arrow"][direction]
            self.draw_arrow(self.screen, cx, cy, direction, color_main, color_light,
                            scale=1.0 + progress * 0.3, season=self.season)

        # 粒子
        for p in self.particles:
            p.draw(self.screen)

    def draw_message(self, title, tip, btn_rect, btn_text, btn_color=GREEN):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        card = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 130, 360, 260)
        card_surf = pygame.Surface((card.width, card.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (255, 255, 255, 245), card_surf.get_rect(), border_radius=16)
        self.screen.blit(card_surf, card.topleft)

        title_surf = self.big_font.render(title, True, DARK)
        self.screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, card.y + 60)))

        tip_surf = self.small_font.render(tip, True, (90, 90, 90))
        self.screen.blit(tip_surf, tip_surf.get_rect(center=(WIDTH // 2, card.y + 120)))

        self.draw_button(btn_rect, btn_text, btn_color)

    def draw(self):
        self.draw_background()

        if self.state == "START":
            self.draw_start()
        elif self.state == "PLAYING":
            self.draw_playing()
        elif self.state == "LEVEL_CLEAR":
            self.draw_playing()
            if self.flash_timer > 0:
                flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                flash.fill((255, 255, 255, int(180 * self.flash_timer / 0.6)))
                self.screen.blit(flash, (0, 0))
            self.draw_message("关卡通过！", "点击进入下一关", self.next_btn, "下一关")
        elif self.state == "ALL_CLEAR":
            self.draw_playing()
            self.draw_message("全部通关！", "四季之旅完成", self.restart_all_btn, "重新开始")
        elif self.state == "GAME_OVER":
            self.draw_playing()
            self.draw_message("挑战失败", "再试一次吧", self.retry_btn, "重试", RED)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.state == "START":
                if self.start_btn.collidepoint(pos):
                    self.load_level(0)

            elif self.state == "PLAYING":
                if self.restart_btn.collidepoint(pos):
                    self.load_level(self.level_index)
                else:
                    self.click_board(pos)

            elif self.state == "LEVEL_CLEAR":
                if self.next_btn.collidepoint(pos):
                    self.load_level(self.level_index + 1)

            elif self.state == "ALL_CLEAR":
                if self.restart_all_btn.collidepoint(pos):
                    self.load_level(0)

            elif self.state == "GAME_OVER":
                if self.retry_btn.collidepoint(pos):
                    self.load_level(self.level_index)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_event(event)

            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
