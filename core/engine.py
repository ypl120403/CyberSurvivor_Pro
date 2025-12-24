import pygame
import random
import sys
from core.constants import *
from core.registry import registry
from core.camera import CameraGroup
from entities.player import Player
from combat.weapon_manager import WeaponManager
from combat.weapon_factory import WeaponFactory
from combat.damage_system import DamageSystem
from entities.enemies.base_enemy import Enemy
from ui.menus.hud import HUD
from ui.menus.upgrade_panel import UpgradePanel
from core.event_bus import bus


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "PLAYING"

        # 1. 加载数据
        registry.load()
        WeaponFactory.auto_discover_logic()

        # 2. 初始化显示与物理组
        self.all_sprites = CameraGroup()
        self.enemy_group = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        self.gem_group = pygame.sprite.Group()


        # 3. 创建玩家 (把自己传进去，以便面板访问管理器)
        self.player = Player((WIDTH // 2, HEIGHT // 2), [self.all_sprites], self)
        self.score = 0
        self.spawn_timer = 0

        # 4. 初始化系统
        self.hud = HUD(self.player)
        self.upgrade_panel = UpgradePanel(self.player)

        # 5. 核心武器插槽管理
        # 传入 [显示组, 物理组]
        self.weapon_manager = WeaponManager(
            self.player,
            self.enemy_group,
            [self.all_sprites, self.projectile_group]
        )

        # 6. 初始装配：直接通过 ID 从 Registry 加载
        self.weapon_manager.add_or_upgrade_weapon("starter_gun")

        # 订阅事件
        bus.subscribe("RESUME_GAME", self.resume)

    def resume(self):
        self.state = "PLAYING"

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False

            if self.state == "PLAYING":
                self.update_game(dt)

            # 渲染绘制
            self.all_sprites.custom_draw(self.player)
            self.hud.draw(self.score)

            if self.state == "UPGRADING":
                self.upgrade_panel.draw()

            pygame.display.flip()

    def update_game(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= 1.5:
            self.spawn_enemy()
            self.spawn_timer = 0

        self.all_sprites.update(dt)
        self.weapon_manager.update(dt)

        # 碰撞逻辑
        hits = pygame.sprite.groupcollide(self.enemy_group, self.projectile_group, False, False)
        for enemy, bullets in hits.items():
            for bullet in bullets:
                if DamageSystem.handle_collision(bullet, enemy):
                    self.score += 10
                    from entities.pickups.exp_gem import ExperienceGem
                    ExperienceGem(enemy.rect.center, [self.all_sprites, self.gem_group], self.player)

        if pygame.sprite.spritecollide(self.player, self.enemy_group, False):
            self.player.take_damage(1)

        gems_hit = pygame.sprite.spritecollide(self.player, self.gem_group, True)
        for gem in gems_hit:
            self.player.gain_xp(gem.xp_value)
            if self.player.current_xp >= self.player.xp_required:
                self.player.perform_level_up()
                self.state = "UPGRADING"
                self.upgrade_panel.show()

    def spawn_enemy(self):
        angle = random.uniform(0, 360)
        dist = 850
        x = self.player.pos.x + pygame.math.Vector2(1, 0).rotate(angle).x * dist
        y = self.player.pos.y + pygame.math.Vector2(1, 0).rotate(angle).y * dist
        config = registry.enemies.get("basic_grunt")
        if config:
            Enemy((x, y), [self.all_sprites, self.enemy_group], config, self.player)