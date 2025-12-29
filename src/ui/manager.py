# ui/ui_manager.py (全量替换)
import pygame
import random
from src.core.constants import *


class UIManager:
    def __init__(self, engine):
        self.engine = engine
        self.display_surface = pygame.display.get_surface()
        self.floating_texts = []
        self.menus = {}

    def add_menu(self, name, instance):
        self.menus[name] = instance

    def spawn_damage_text(self, pos, amount):
        font = pygame.font.SysFont("arial", 24, bold=True)
        txt_surf = font.render(str(int(amount)), True, (255, 255, 255))

        self.floating_texts.append({
            'pos': pygame.Vector2(pos),
            'surf': txt_surf,
            'life': 1.0,
            'vel': pygame.Vector2(random.uniform(-30, 30), -60)
        })

    def update(self, dt):
        for text in self.floating_texts[:]:
            text['pos'] += text['vel'] * dt
            text['life'] -= dt
            if text['life'] <= 0:
                self.floating_texts.remove(text)

    def draw(self, score):
        # 1. 只有在战斗场景时才画伤害数字
        # 通过检查当前 scene 是否有 'all_sprites' 属性来判定
        if hasattr(self.engine.scene, 'all_sprites'):
            self._draw_floating_texts()

        # 2. 渲染常驻 HUD (HUD 内部已有安全判定)
        if 'hud' in self.menus:
            self.menus['hud'].draw(score)

        # 3. 渲染升级面板
        if self.engine.state == "UPGRADING" and 'upgrade' in self.menus:
            self.menus['upgrade'].draw()

    def _draw_floating_texts(self):
        # 核心修复点：从当前 scene 获取 all_sprites 的 offset
        offset = self.engine.scene.all_sprites.offset
        for text in self.floating_texts:
            alpha = int(text['life'] * 255)
            text['surf'].set_alpha(alpha)
            render_pos = text['pos'] - offset
            self.display_surface.blit(text['surf'], render_pos)