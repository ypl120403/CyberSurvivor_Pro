# core/engine.py
import pygame
import sys
from src.core.constants import *
from src.core.registry import registry
from src.ui.manager import UIManager
from src.ui.screens.hud import HUD
from src.ui.screens.upgrade_panel import UpgradePanel
from src.core.event_bus import bus

from src.scenes.menu_scene import MenuScene
from src.scenes.combat_scene import CombatScene


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("CyberSurvivor Pro")
        self.clock = pygame.time.Clock()
        self.running = True

        # 1. 执行一劳永逸的全量加载 (JSON + 资产)
        registry.load_all()

        # 武器逻辑自动发现
        from src.combat.weapon_factory import WeaponFactory
        WeaponFactory.auto_discover_logic()

        # 2. UI 管理器初始化
        self.ui_manager = UIManager(self)

        # 完善的 Dummy 玩家对象：模拟真正的属性结构，确保进入战斗前 HUD 不崩溃
        # 给它一个符合 StatsComponent 结构的 stats 属性
        class DummyStats:
            def __init__(self):
                self.max_health = type('val', (object,), {'value': 100})()

        self.player_dummy = type('obj', (object,), {
            'current_hp': 0,
            'current_xp': 0,
            'xp_required': 100,
            'level': 1,
            'stats': DummyStats()
        })

        self.ui_manager.add_menu('hud', HUD(self.player_dummy))
        self.ui_manager.add_menu('upgrade', UpgradePanel(self.player_dummy))

        # 3. 场景与状态控制
        self.scene = None
        self.state = "MAIN_MENU"
        self.score = 0

        # 启动即进入菜单
        self.switch_scene("MENU")

        bus.subscribe("RESUME_GAME", self.resume)

    def switch_scene(self, scene_type, char_config=None):
        """核心：增强版切换场景方法，支持角色配置注入"""
        if scene_type == "MENU":
            self.scene = MenuScene(self)
            self.state = "MAIN_MENU"

        elif scene_type == "COMBAT":
            # 规则：如果未指定角色，默认加载注册中心里的第一个角色 (兜底)
            if char_config is None:
                char_config = list(registry.characters.values())[0] if registry.characters else {}

            # 将选中的角色配置注入战斗场景
            self.scene = CombatScene(self, char_config)
            self.state = "PLAYING"

            # 核心同步：将 UI 面板的监听目标切换为战斗场景中真实的 Player 实例
            self.ui_manager.menus['hud'].player = self.scene.player
            self.ui_manager.menus['upgrade'].player = self.scene.player

    def resume(self):
        self.state = "PLAYING"

    def on_enemy_killed(self, enemy):
        """全局死亡回调"""
        self.score += enemy.config.get("score_value", 10)
        from src.entities.pickups.exp_gem import ExperienceGem
        if hasattr(self.scene, 'all_sprites'):
            ExperienceGem(enemy.rect.center, [self.scene.all_sprites, self.scene.gem_group], self.scene.player)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # 暂停逻辑拦截
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "PLAYING":
                            self.state = "PAUSED"
                        elif self.state == "PAUSED":
                            self.state = "PLAYING"

            # 逻辑分发
            if self.state == "MAIN_MENU":
                self.scene.update(dt)
            elif self.state == "PLAYING":
                self.scene.update(dt)
                self.ui_manager.update(dt)
            # PAUSED 状态下逻辑静止

            # 渲染分发
            if self.state == "MAIN_MENU":
                self.scene.draw()
            else:
                # 战斗相关场景 (PLAYING, PAUSED, UPGRADING) 均渲染场景内容 + UI
                self.scene.draw()
                self.ui_manager.draw(self.score)

            pygame.display.flip()


if __name__ == '__main__':
    GameEngine().run()