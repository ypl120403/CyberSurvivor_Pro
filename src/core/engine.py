import pygame
import sys
from src.core.constants import *
from src.core.registry import registry
from src.ui.manager import UIManager
from src.ui.screens.hud import HUD
from src.ui.screens.upgrade_panel import UpgradePanel
from src.core.event_bus import bus

# 场景导入
from src.scenes.menu_scene import MenuScene
from src.scenes.combat_scene import CombatScene


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("CyberSurvivor Pro")
        self.clock = pygame.time.Clock()
        self.running = True

        # 1. 核心系统一键同步
        registry.load_all()

        # 武器工厂自动扫描
        from src.combat.weapon_factory import WeaponFactory
        WeaponFactory.auto_discover_logic()

        # 2. UI 系统
        self.ui_manager = UIManager(self)
        self._init_dummy_player()  # 封装初始化占位符逻辑

        # 3. 场景与状态
        self.scene = None
        self.state = "MAIN_MENU"
        self.score = 0
        self.switch_scene("MENU")

        # 4. 全球事件监听
        bus.subscribe("RESUME_GAME", self.resume)

    def _init_dummy_player(self):
        """规则：创建一个标准接口的假人，防止菜单界面报错"""

        class DummyStats:
            def __init__(self):
                self.max_health = type('v', (object,), {'value': 100})()

        self.player_dummy = type('obj', (object,), {
            'current_hp': 0, 'current_xp': 0, 'xp_required': 100, 'level': 1,
            'stats': DummyStats(),
            'char_config': {}  # 预留配置接口
        })
        self.ui_manager.add_menu('hud', HUD(self.player_dummy))
        self.ui_manager.add_menu('upgrade', UpgradePanel(self.player_dummy))

    def switch_scene(self, scene_type, char_config=None):
        """一劳永逸的场景切换逻辑"""
        if scene_type == "MENU":
            self.scene = MenuScene(self)
            self.state = "MAIN_MENU"
        elif scene_type == "COMBAT":
            # 兜底：如果没有选人，默认加载第一个
            if not char_config:
                char_config = list(registry.characters.values())[0] if registry.characters else {}

            # 实例化战斗场景
            self.scene = CombatScene(self, char_config)
            self.state = "PLAYING"

            # 自动重定向 UI 的监听目标
            self.ui_manager.menus['hud'].player = self.scene.player
            self.ui_manager.menus['upgrade'].player = self.scene.player

    # src/core/engine.py

    def on_enemy_killed(self, enemy):
        # 1. 基础逻辑：加分
        self.score += enemy.config.get("score_value", 10)

        # 2. 掉落经验
        if hasattr(self.scene, 'all_sprites'):
            from src.entities.pickups.exp_gem import ExperienceGem
            ExperienceGem(enemy.rect.center, [self.scene.all_sprites, self.scene.gem_group], self.scene.player)

        # 3. 【点火】通过 EventBus 发布全球信号
        # 这样被动系统、UI系统、音效系统都可以独立响应
        from src.core.event_bus import bus
        bus.emit("ENEMY_DIED", enemy=enemy, killer=self.scene.player)

        # 兼容现有调用（保持 player 内部被动触发）
        if hasattr(self.scene, 'player'):
            self.scene.player.trigger_passives("on_kill")

    def resume(self):
        self.state = "PLAYING"

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            # --- 事件分发 ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._handle_pause()

            # --- 逻辑更新 ---
            self._update_dispatch(dt)

            # --- 画面渲染 ---
            self._draw_dispatch()

            pygame.display.flip()

    def _handle_pause(self):
        """暂停切换规则"""
        if self.state == "PLAYING":
            self.state = "PAUSED"
        elif self.state == "PAUSED":
            self.state = "PLAYING"

    def _update_dispatch(self, dt):
        """一劳永逸的逻辑分发"""
        if self.state == "MAIN_MENU":
            self.scene.update(dt)
        elif self.state == "PLAYING":
            self.scene.update(dt)
            self.ui_manager.update(dt)
        # 升级中和暂停中，不更新 scene 逻辑，从而实现“画面凝固”

    def _draw_dispatch(self):
        """一劳永逸的渲染分发"""
        if self.state == "MAIN_MENU":
            self.scene.draw()
        else:
            # 战斗相关的全状态（玩、停、升）都要画背景和 UI
            self.scene.draw()
            self.ui_manager.draw(self.score)


if __name__ == '__main__':
    GameEngine().run()