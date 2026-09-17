import pygame
import sys
import math

pygame.init()

# ==================== 常量 ====================
CELL = 80
MARGIN = 40
INFO_H = 120
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

# 关卡数据：0 表示空，1 上，2 右，3 下，4 左
levels = [
    {
        "grid": [
            [0, 0, RIGHT, 0, 0],
            [0, 0, UP, 0, 0],
            [RIGHT, RIGHT, RIGHT, RIGHT, RIGHT],
            [0, 0, DOWN, 0, 0],
            [0, 0, LEFT, 0, 0],
        ],
        "mistakes": 3
    },
    {
        "grid": [
            [0, 0, UP, 0, 0],
            [0, 0, UP, 0, 0],
            [RIGHT, RIGHT, RIGHT, RIGHT, RIGHT],
            [0, 0, DOWN, 0, 0],
            [LEFT, 0, DOWN, 0, 0],
        ],
        "mistakes": 3
    },
    {
        "grid": [
            [UP, 0, LEFT, 0, UP],
            [0, DOWN, 0, DOWN, 0],
            [RIGHT, 0, 0, 0, RIGHT],
            [0, DOWN, 0, DOWN, 0],
            [DOWN, 0, 0, 0, DOWN],
        ],
        "mistakes": 4
    },
]


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()

        # ==================== 修改了这里 ====================
        # 原来用 SysFont 会报错，现在直接读取 Windows 系统自带的微软雅黑字体文件
        font_path = "C:/Windows/Fonts/msyh.ttc"
        self.font = pygame.font.Font(font_path, 28)
        self.small_font = pygame.font.Font(font_path, 22)
        self.big_font = pygame.font.Font(font_path, 48)
        # ====================================================

        self.state = "START"
        self.level_index = 0
        self.grid = []
        self.mistakes = 0
        self.max_mistakes = 0
        self.animations = []
        self.collision_effects = []

        self.board_x = MARGIN
        self.board_y = INFO_H + MARGIN

        self.start_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 60)
        self.restart_btn = pygame.Rect(WIDTH - 170, 30, 140, 50)
        self.next_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 60)
        self.retry_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 60)
        self.restart_all_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 60)

        self.load_level(0)
        self.state = "START"

    def load_level(self, index):
        self.level_index = index
        data = levels[index]
        self.grid = [row[:] for row in data["grid"]]
        self.max_mistakes = data["mistakes"]
        self.mistakes = 0
        self.animations = []
        self.collision_effects = []
        self.state = "PLAYING"

    def is_blocked(self, r, c, direction):
        """判断 (r,c) 处箭头前方是否有其他箭头阻挡"""
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

        if not self.is_blocked(r, c, direction):
            # 前方无阻挡：飞出并消除
            self.grid[r][c] = 0
            self.animations.append({
                "r": r, "c": c, "dir": direction,
                "progress": 0.0, "speed": 4.0
            })
        else:
            # 前方有阻挡：碰撞，失误 +1
            self.mistakes += 1
            self.collision_effects.append({"r": r, "c": c, "timer": 0.4})
            if self.mistakes >= self.max_mistakes:
                self.state = "GAME_OVER"

    def update(self, dt):
        for anim in self.animations[:]:
            anim["progress"] += anim["speed"] * dt
            if anim["progress"] >= 1.0:
                self.animations.remove(anim)

        for eff in self.collision_effects[:]:
            eff["timer"] -= dt
            if eff["timer"] <= 0:
                self.collision_effects.remove(eff)

        if self.state == "PLAYING":
            if all(x == 0 for row in self.grid for x in row) and not self.animations:
                if self.level_index == len(levels) - 1:
                    self.state = "ALL_CLEAR"
                else:
                    self.state = "LEVEL_CLEAR"

    def draw_arrow(self, surface, cx, cy, direction, color):
        s = CELL * 0.3
        if direction == UP:
            pygame.draw.polygon(surface, color, [(cx, cy - s), (cx - s, cy + s * 0.3), (cx + s, cy + s * 0.3)])
            pygame.draw.rect(surface, color, (cx - s * 0.25, cy + s * 0.3, s * 0.5, s * 0.7))
        elif direction == DOWN:
            pygame.draw.polygon(surface, color, [(cx, cy + s), (cx - s, cy - s * 0.3), (cx + s, cy - s * 0.3)])
            pygame.draw.rect(surface, color, (cx - s * 0.25, cy - s, s * 0.5, s * 0.7))
        elif direction == LEFT:
            pygame.draw.polygon(surface, color, [(cx - s, cy), (cx + s * 0.3, cy - s), (cx + s * 0.3, cy + s)])
            pygame.draw.rect(surface, color, (cx + s * 0.3, cy - s * 0.25, s * 0.7, s * 0.5))
        elif direction == RIGHT:
            pygame.draw.polygon(surface, color, [(cx + s, cy), (cx - s * 0.3, cy - s), (cx - s * 0.3, cy + s)])
            pygame.draw.rect(surface, color, (cx - s, cy - s * 0.25, s * 0.7, s * 0.5))

    def draw_button(self, rect, text, color=BLUE):
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, DARK, rect, 2, border_radius=8)
        txt = self.font.render(text, True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw_start(self):
        title = self.big_font.render("一箭又一箭", True, DARK)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
        tip = self.small_font.render("点击箭头，让它飞出棋盘", True, DARK)
        self.screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        self.draw_button(self.start_btn, "开始游戏", GREEN)

    def draw_playing(self):
        level_text = self.font.render(f"关卡：{self.level_index + 1}/{len(levels)}", True, DARK)
        self.screen.blit(level_text, (MARGIN, 30))

        remain = sum(1 for row in self.grid for x in row if x != 0)
        remain_text = self.font.render(f"剩余箭头：{remain}", True, DARK)
        self.screen.blit(remain_text, (MARGIN, 70))

        mistake_text = self.font.render(f"剩余失误：{self.max_mistakes - self.mistakes}", True, RED)
        self.screen.blit(mistake_text, (MARGIN + 260, 70))

        self.draw_button(self.restart_btn, "重新开始", YELLOW)

        # 棋盘格子
        for r in range(GRID_H):
            for c in range(GRID_W):
                rect = pygame.Rect(self.board_x + c * CELL, self.board_y + r * CELL, CELL, CELL)
                pygame.draw.rect(self.screen, WHITE, rect)
                pygame.draw.rect(self.screen, GRAY, rect, 2)

        # 静态箭头 + 碰撞晃动
        for r in range(GRID_H):
            for c in range(GRID_W):
                if self.grid[r][c] != 0:
                    offset_x = 0
                    offset_y = 0
                    color = DARK
                    for eff in self.collision_effects:
                        if eff["r"] == r and eff["c"] == c:
                            offset_x = 5 * math.sin(eff["timer"] * 60)
                            color = RED
                    cx = self.board_x + c * CELL + CELL // 2 + offset_x
                    cy = self.board_y + r * CELL + CELL // 2 + offset_y
                    self.draw_arrow(self.screen, cx, cy, self.grid[r][c], color)

        # 飞出动画
        for anim in self.animations:
            r, c, direction = anim["r"], anim["c"], anim["dir"]
            progress = anim["progress"]
            cx = self.board_x + c * CELL + CELL // 2
            cy = self.board_y + r * CELL + CELL // 2
            dist = CELL * 6 * progress

            if direction == UP:
                cy -= dist
            elif direction == DOWN:
                cy += dist
            elif direction == LEFT:
                cx -= dist
            elif direction == RIGHT:
                cx += dist

            self.draw_arrow(self.screen, cx, cy, direction, BLUE)

    def draw_message(self, title, tip, btn_rect, btn_text):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        title_surf = self.big_font.render(title, True, WHITE)
        self.screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))

        tip_surf = self.small_font.render(tip, True, WHITE)
        self.screen.blit(tip_surf, tip_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))

        self.draw_button(btn_rect, btn_text, GREEN)

    def draw(self):
        self.screen.fill(BG)

        if self.state == "START":
            self.draw_start()
        elif self.state == "PLAYING":
            self.draw_playing()
        elif self.state == "LEVEL_CLEAR":
            self.draw_playing()
            self.draw_message("关卡通过！", "点击进入下一关", self.next_btn, "下一关")
        elif self.state == "ALL_CLEAR":
            self.draw_playing()
            self.draw_message("全部通关！", "点击重新开始", self.restart_all_btn, "重新开始")
        elif self.state == "GAME_OVER":
            self.draw_playing()
            self.draw_message("挑战失败", "点击重试本关", self.retry_btn, "重试")

    def handle_event(self, event):
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