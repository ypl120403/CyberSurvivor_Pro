# systems/menu_scene.py
import pygame
import sys
from systems.base_scene import BaseScene
from ui.components import CyberButton
from core.constants import *
from core.save_manager import save_manager
from core.registry import registry


class MenuScene(BaseScene):
    def __init__(self, engine):
        super().__init__(engine)
        self.state = "MAIN"  # 状态机：MAIN, COMBAT_HUB, UPGRADES, ARCHIVE, SETTINGS

        # 1. 字体初始化
        self.font_title = pygame.font.SysFont("impact", 90)
        self.font_sub = pygame.font.SysFont("microsoftyahei", 30, bold=True)
        self.font_info = pygame.font.SysFont("microsoftyahei", 18)

        # 2. 角色列表与索引 (自动同步 registry 加载的 JSON)
        self.char_list = list(registry.characters.values())
        self.char_index = 0

        # 3. 按钮定义
        self.main_btns = {
            "A": CyberButton("作战中心 (COMBAT HUB)", (100, 250), (350, 50), self.font_sub),
            "B": CyberButton("神经增强 (META-UPGRADES)", (100, 320), (350, 50), self.font_sub),
            "C": CyberButton("档案库 (ARCHIVE)", (100, 390), (350, 50), self.font_sub),
            "D": CyberButton("协议配置 (SETTINGS)", (100, 460), (350, 50), self.font_sub),
            "E": CyberButton("切断连接 (QUIT)", (100, 530), (350, 50), self.font_sub)
        }

        # 4. 子菜单专用控件
        self.prev_btn = CyberButton("<", (WIDTH // 2 - 260, 300), (50, 50), self.font_sub)
        self.next_btn = CyberButton(">", (WIDTH // 2 + 210, 300), (50, 50), self.font_sub)
        self.start_btn = CyberButton("同步意识 (START)", (WIDTH // 2 - 125, 550), (250, 60), self.font_sub,
                                     color=(0, 255, 150))
        self.back_btn = CyberButton("返回主协议", (WIDTH - 250, HEIGHT - 100), (200, 50), self.font_sub)

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0]

        # 主菜单逻辑
        if self.state == "MAIN":
            for btn in self.main_btns.values(): btn.update(mouse_pos)
            if clicked:
                if self.main_btns["A"].is_hovered:
                    self.state = "COMBAT_HUB"
                elif self.main_btns["B"].is_hovered:
                    self.state = "UPGRADES"
                elif self.main_btns["C"].is_hovered:
                    self.state = "ARCHIVE"  # 修复点击
                elif self.main_btns["D"].is_hovered:
                    self.state = "SETTINGS"  # 修复点击
                elif self.main_btns["E"].is_hovered:
                    pygame.quit(); sys.exit()
                # 统一延迟，防止点击穿透
                if any(b.is_hovered for b in self.main_btns.values()): pygame.time.delay(150)

        # 作战中心逻辑
        elif self.state == "COMBAT_HUB":
            self.prev_btn.update(mouse_pos)
            self.next_btn.update(mouse_pos)
            self.start_btn.update(mouse_pos)
            self.back_btn.update(mouse_pos)

            if clicked:
                if self.prev_btn.is_hovered:
                    self.char_index = (self.char_index - 1) % len(self.char_list)
                    pygame.time.delay(150)
                elif self.next_btn.is_hovered:
                    self.char_index = (self.char_index + 1) % len(self.char_list)
                    pygame.time.delay(150)
                elif self.start_btn.is_hovered:
                    selected_char = self.char_list[self.char_index]
                    self.engine.switch_scene("COMBAT", selected_char)
                elif self.back_btn.is_hovered:
                    self.state = "MAIN"
                    pygame.time.delay(150)

        # 其他子菜单通用逻辑 (返回按钮)
        elif self.state in ["UPGRADES", "ARCHIVE", "SETTINGS"]:
            self.back_btn.update(mouse_pos)
            if clicked and self.back_btn.is_hovered:
                self.state = "MAIN"
                pygame.time.delay(150)

    def draw(self):
        self.screen.fill((5, 5, 10))
        self._draw_background_fx()

        if self.state == "MAIN":
            self._draw_main_menu()
        elif self.state == "COMBAT_HUB":
            self._draw_combat_hub()
        elif self.state == "UPGRADES":
            self._draw_meta_upgrades()
        elif self.state == "ARCHIVE":
            self._draw_placeholder("--- 档案库: 历史数据重构中 ---")
        elif self.state == "SETTINGS":
            self._draw_placeholder("--- 协议配置: 神经连接调整中 ---")

        if self.state != "MAIN":
            self.back_btn.draw(self.screen)

    def _draw_background_fx(self):
        for x in range(0, WIDTH, 50): pygame.draw.line(self.screen, (15, 15, 30), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 50): pygame.draw.line(self.screen, (15, 15, 30), (0, y), (WIDTH, y))

    def _draw_main_menu(self):
        title = self.font_title.render("CYBER SURVIVOR", True, (0, 255, 240))
        self.screen.blit(title, (100, 100))
        pygame.draw.line(self.screen, (255, 0, 255), (100, 200), (600, 200), 3)
        for btn in self.main_btns.values(): btn.draw(self.screen)

    def _draw_combat_hub(self):
        if not self.char_list: return
        char = self.char_list[self.char_index]

        # 标题
        txt = self.font_sub.render(f"--- 逻辑体部署: {char['name']} ---", True, (0, 255, 240))
        self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 80))

        # 预览区
        preview_rect = pygame.Rect(WIDTH // 2 - 150, 150, 300, 300)
        pygame.draw.rect(self.screen, (20, 20, 40), preview_rect, border_radius=15)

        # 尝试使用规则获取贴图，否则画圆占位
        char_tex = registry.get_texture(f"characters/{char['id']}")
        if char_tex.get_width() > 32:  # 不是默认生成的紫色方块
            self.screen.blit(char_tex, char_tex.get_rect(center=preview_rect.center))
        else:
            placeholder_color = (0, 255, 240) if "ghost" in char['id'] else (255, 50, 80)
            pygame.draw.circle(self.screen, placeholder_color, preview_rect.center, 60)

        # 描述与提示
        desc_txt = self.font_info.render(char['desc'], True, (200, 200, 200))
        self.screen.blit(desc_txt, (WIDTH // 2 - desc_txt.get_width() // 2, 470))

        weapon_hint = self.font_info.render(f"初始协议: {char.get('starting_weapon', 'N/A')}", True, (255, 255, 0))
        self.screen.blit(weapon_hint, (WIDTH // 2 - weapon_hint.get_width() // 2, 500))

        # 按钮
        self.prev_btn.draw(self.screen)
        self.next_btn.draw(self.screen)
        self.start_btn.draw(self.screen)

    def _draw_placeholder(self, text):
        """一劳永逸：绘制开发中界面的通用方法"""
        txt = self.font_sub.render(text, True, (100, 100, 100))
        self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2))

    def _draw_meta_upgrades(self):
        txt = self.font_sub.render("--- 神经回路增强 ---", True, (255, 0, 255))
        self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 100))
        y_offset = 200
        for stat, val in save_manager.data.get("meta_upgrades", {}).items():
            stat_txt = self.font_info.render(f"{stat.upper()} 加成层级: {val}", True, (200, 200, 200))
            self.screen.blit(stat_txt, (WIDTH // 2 - 100, y_offset))
            y_offset += 50