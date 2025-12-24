import pygame
from core.constants import *


class HUD:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont("arial", 22, bold=True)

    def draw_bar(self, x, y, current, max_val, color, label):
        bar_width = 200
        bar_height = 18
        # 背景
        pygame.draw.rect(self.display_surface, (40, 40, 45), (x, y, bar_width, bar_height), border_radius=4)
        # 填充
        if max_val > 0:
            ratio = min(1, current / max_val)
            pygame.draw.rect(self.display_surface, color, (x, y, bar_width * ratio, bar_height), border_radius=4)
        # 边框
        pygame.draw.rect(self.display_surface, (200, 200, 210), (x, y, bar_width, bar_height), 2, border_radius=4)
        # 文字
        txt = self.font.render(label, True, (255, 255, 255))
        self.display_surface.blit(txt, (x, y - 25))

    def draw(self, score):
        # 1. 血条
        hp = self.player.current_hp
        m_hp = self.player.stats.max_health.value
        self.draw_bar(20, 45, hp, m_hp, (255, 50, 80), "INTEGRITY")

        # 2. 经验条
        xp = self.player.current_xp
        req = self.player.xp_required
        self.draw_bar(WIDTH // 2 - 100, HEIGHT - 40, xp, req, (0, 255, 200), f"LV {self.player.level}")

        # 3. 分数
        score_txt = self.font.render(f"SCORE: {score:06d}", True, (255, 215, 0))
        self.display_surface.blit(score_txt, (WIDTH - 200, 20))