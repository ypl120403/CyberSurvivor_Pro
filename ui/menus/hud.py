# ui/menus/hud.py (全量替换)
import pygame
from core.constants import *


class HUD:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont("consolas", 20, bold=True)

        self.smooth_hp = player.current_hp
        self.smooth_xp = player.current_xp

    def draw(self, score):
        # 如果当前没有真正的玩家对象（比如在 dummy 阶段），直接跳过
        if not hasattr(self.player, 'stats'): return

        self.smooth_hp += (self.player.current_hp - self.smooth_hp) * 0.1
        self.smooth_xp += (self.player.current_xp - self.smooth_xp) * 0.1

        self._draw_hp_bar()
        self._draw_xp_bar()
        self._draw_stats(score)
        self._draw_weapon_icons()

    def _draw_hp_bar(self):
        x, y, w, h = 30, 40, 250, 14
        pygame.draw.rect(self.display_surface, (40, 40, 50), (x, y, w, h), border_radius=4)
        max_hp = self.player.stats.max_health.value
        if max_hp > 0:
            fill_w = w * (max(0, self.smooth_hp) / max_hp)
            pygame.draw.rect(self.display_surface, (255, 50, 80), (x, y, fill_w, h), border_radius=4)
        pygame.draw.rect(self.display_surface, (200, 200, 210), (x, y, w, h), 2, border_radius=4)

    def _draw_xp_bar(self):
        xp_ratio = self.smooth_xp / self.player.xp_required
        pygame.draw.rect(self.display_surface, (20, 20, 30), (0, HEIGHT - 10, WIDTH, 10))
        pygame.draw.rect(self.display_surface, (0, 255, 200), (0, HEIGHT - 10, WIDTH * xp_ratio, 10))

    def _draw_stats(self, score):
        info_str = f"SCORE: {score:06d} | LVL: {self.player.level}"
        info_surf = self.font.render(info_str, True, (0, 255, 240))
        self.display_surface.blit(info_surf, (WIDTH - 280, 30))

        now_ms = pygame.time.get_ticks() // 1000
        time_str = f"{now_ms // 60:02d}:{now_ms % 60:02d}"
        t_surf = self.font.render(time_str, True, (255, 255, 255))
        self.display_surface.blit(t_surf, (WIDTH // 2 - t_surf.get_width() // 2, 20))

    def _draw_weapon_icons(self):
        """核心修复点：适配场景化架构"""
        start_x, y, size = 30, 75, 30

        # 1. 先检查 engine 是否有活跃场景
        scene = getattr(self.player.engine, 'scene', None)
        # 2. 检查场景是否是战斗场景（即是否有 weapon_manager）
        weapon_manager = getattr(scene, 'weapon_manager', None)

        if not weapon_manager:
            return

        owned_weapons = list(weapon_manager.weapons.values())
        for i in range(6):
            rect = pygame.Rect(start_x + i * (size + 8), y, size, size)
            pygame.draw.rect(self.display_surface, (30, 30, 40), rect, border_radius=4)
            if i < len(owned_weapons):
                pygame.draw.rect(self.display_surface, (0, 255, 240, 100), rect, 2, border_radius=4)
                lvl_txt = self.font.render(str(owned_weapons[i].level), True, (255, 255, 255))
                self.display_surface.blit(lvl_txt, (rect.x + 8, rect.y + 4))