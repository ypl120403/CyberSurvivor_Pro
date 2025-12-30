# src/ui/screens/upgrade_panel.py
import pygame
import random
from src.core.constants import *
from src.core.registry import registry
from src.core.event_bus import bus


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
        """核心修复点：智能识别【全局武器】与【专属武器】"""
        pool = []

        # 1. 属性池
        for item in registry.upgrades:
            pool.append({"type": "stat", "name": item['name'], "desc": item['desc'], "raw_data": item})

        # 2. 武器池
        scene = self.player.engine.scene
        if hasattr(scene, 'weapon_manager'):
            wm = scene.weapon_manager
            weapon_cands = wm.get_upgrade_candidates()

            for cand in weapon_cands:
                # --- 重点修复逻辑 ---
                if cand['type'] == 'weapon_upgrade':
                    # 升级已有武器：直接从武器实例的 config 里拿名字（解决 tesla_bolt 缺失问题）
                    weapon_inst = wm.weapons.get(cand['id'])
                    w_name = weapon_inst.config.get('name', '未知武器')
                    w_desc = f"强化至 LV.{cand['level']}"
                else:
                    # 新武器：从注册表拿名字
                    w_config = registry.weapons.get(cand['id'])
                    if not w_config: continue  # 容错
                    w_name = w_config.get('name', '新武器')
                    w_desc = "点击获得新武装"

                pool.append({"type": cand['type'], "name": w_name, "desc": w_desc, "raw_data": cand})

        # 随机抽取 3 个
        count = min(3, len(pool))
        self.options = random.sample(pool, count)

    def reroll(self):
        # 维度 5: 检测玩家特权标签
        has_infinite = "infinite_reroll" in getattr(self.player, 'privilege_tags', set())

        if has_infinite:
            # 特权逻辑：不消耗 reroll_count
            print("💎 特权生效：无限刷新！")
            self._generate_options()
        elif self.reroll_count > 0:
            self.reroll_count -= 1
            self._generate_options()

    def draw(self):
        if not self.visible: return
        now = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0]

        # 蒙版
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
            pygame.draw.rect(self.display_surface, (0, 255, 240) if is_hover else (80, 80, 100), rect, 3,
                             border_radius=15)

            # 绘制文字
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
        raw = opt['raw_data']
        if opt['type'] == 'stat':
            self.player.stats.add_modifier(raw['stat'], raw['value'])
            # 补血逻辑：如果是加生命上限，顺便把当前血量也加上去
            if raw['stat'] == "max_health":
                add_hp = self.player.stats.max_health.base_value * raw['value']
                self.player.current_hp += add_hp
        else:
            scene = self.player.engine.scene
            if hasattr(scene, 'weapon_manager'):
                scene.weapon_manager.add_or_upgrade_weapon(raw['id'])

        self.visible = False
        bus.emit("RESUME_GAME")