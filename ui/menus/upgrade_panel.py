# ui/menus/upgrade_panel.py (全量替换)
import pygame
import random
from core.constants import *
from core.registry import registry
from core.event_bus import bus

class UpgradePanel:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()

        # 加载支持中文的字体
        self.font_title = self._get_font(28)
        self.font_desc = self._get_font(18)
        self.font_button = self._get_font(22)

        self.visible = False
        self.options = []
        self.show_time = 0
        self.input_delay = 500

        self.reroll_count = 1
        self.reroll_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 100, 120, 45)

    @staticmethod
    def _get_font(size):
        for f in ['microsoftyahei', 'simhei', 'arial']:
            font = pygame.font.SysFont(f, size, bold=True)
            if font.size("测试")[0] > 0: return font
        return pygame.font.SysFont(None, size)

    def show(self):
        self._generate_options()
        self.visible = True
        self.show_time = pygame.time.get_ticks()

    def _generate_options(self):
        """核心修复点：通过当前场景获取武器管理器"""
        pool = []
        # 1. 属性池 (从 Registry 加载)
        for item in registry.upgrades:
            pool.append({"type": "stat", "name": item['name'], "desc": item['desc'], "raw_data": item})

        # 2. 武器池 (修复：去当前活跃场景 scene 找 weapon_manager)
        scene = self.player.engine.scene
        if hasattr(scene, 'weapon_manager'):
            weapon_cands = scene.weapon_manager.get_upgrade_candidates()
            for cand in weapon_cands:
                w_name = registry.weapons[cand['id']]['name']
                w_desc = "新武器获得" if cand['type'] == 'weapon_new' else f"升级至 LV.{cand['level']}"
                pool.append({"type": cand['type'], "name": w_name, "desc": w_desc, "raw_data": cand})

        # 随机抽取 3 个
        count = min(3, len(pool))
        self.options = random.sample(pool, count)

    def reroll(self):
        if self.reroll_count > 0:
            self.reroll_count -= 1
            self._generate_options()
            self.show_time = pygame.time.get_ticks()

    def draw(self):
        if not self.visible: return
        now = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0]

        # 蒙版半透明背景
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.display_surface.blit(overlay, (0, 0))

        # 绘制卡片
        card_w, card_h = 280, 380
        start_x = (WIDTH - (card_w * len(self.options) + 40 * (len(self.options) - 1))) // 2

        for i, opt in enumerate(self.options):
            rect = pygame.Rect(start_x + i * (card_w + 40), (HEIGHT - card_h) // 2, card_w, card_h)
            is_hover = rect.collidepoint(mouse_pos)

            color = (70, 75, 100) if is_hover else (45, 48, 62)
            pygame.draw.rect(self.display_surface, color, rect, border_radius=15)
            pygame.draw.rect(self.display_surface, (0, 255, 240) if is_hover else (80, 80, 100), rect, 3, border_radius=15)

            # 文字
            t_surf = self.font_title.render(opt['name'], True, (255, 255, 255))
            d_surf = self.font_desc.render(opt['desc'], True, (200, 200, 200))
            self.display_surface.blit(t_surf, (rect.x + 20, rect.y + 40))
            self.display_surface.blit(d_surf, (rect.x + 20, rect.y + 100))

            if is_hover and clicked and (now - self.show_time > self.input_delay):
                self.apply_upgrade(opt)
                break

        # 刷新按钮
        if self.reroll_count > 0:
            btn_color = (0, 200, 150) if self.reroll_rect.collidepoint(mouse_pos) else (0, 120, 100)
            pygame.draw.rect(self.display_surface, btn_color, self.reroll_rect, border_radius=10)
            btn_txt = self.font_button.render(f"刷新 ({self.reroll_count})", True, (255, 255, 255))
            self.display_surface.blit(btn_txt, (self.reroll_rect.centerx - btn_txt.get_width() // 2,
                                                self.reroll_rect.centery - btn_txt.get_height() // 2))
            if self.reroll_rect.collidepoint(mouse_pos) and clicked and (now - self.show_time > self.input_delay):
                self.reroll()

    def apply_upgrade(self, opt):
        """核心修复点：通过场景执行升级"""
        raw = opt['raw_data']
        if opt['type'] == 'stat':
            self.player.stats.add_modifier(raw['stat'], raw['value'])
            if raw['stat'] in ["health", "max_health"]:
                self.player.current_hp = self.player.stats.max_health.value
        else:
            # 升级或获取武器：同样去当前场景 scene 找 weapon_manager
            scene = self.player.engine.scene
            if hasattr(scene, 'weapon_manager'):
                scene.weapon_manager.add_or_upgrade_weapon(raw['id'])

        self.visible = False
        bus.emit("RESUME_GAME")