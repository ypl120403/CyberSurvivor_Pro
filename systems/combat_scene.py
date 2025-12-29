# systems/combat_scene.py
import pygame
import random
from systems.base_scene import BaseScene
from core.constants import *
from core.registry import registry
from core.camera import CameraGroup
from entities.player import Player
from combat.weapon_manager import WeaponManager
from combat.weapon_factory import WeaponFactory
from combat.damage_system import DamageSystem
from entities.enemies.base_enemy import Enemy


class CombatScene(BaseScene):
    def __init__(self, engine, char_config):  # 核心改动：接收从 engine 传来的角色配置
        super().__init__(engine)

        # 1. 初始化显示与物理组
        self.all_sprites = CameraGroup()
        self.enemy_group = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        self.gem_group = pygame.sprite.Group()

        # 2. 创建玩家：将选中的角色配置(char_config)传给 Player 类
        # 这样 Player 就能根据配置决定自己的血量、速度和样子
        self.player = Player(
            pos=(WIDTH // 2, HEIGHT // 2),
            groups=[self.all_sprites],
            engine=engine,
            char_config=char_config  # 注入规则
        )

        self.spawn_timer = 0

        # 3. 初始化武器管理器
        self.weapon_manager = WeaponManager(
            self.player,
            self.enemy_group,
            [self.all_sprites, self.projectile_group]
        )

        # 一劳永逸：根据 JSON 配置自动加载初始武器，而不是写死 "starter_gun"
        init_weapon = char_config.get("starting_weapon", "starter_gun")
        self.weapon_manager.add_or_upgrade_weapon(init_weapon)

        # 4. 获取 UI 引用
        self.hud = engine.ui_manager.menus['hud']
        self.upgrade_panel = engine.ui_manager.menus['upgrade']

    def update(self, dt):
        # 刷怪逻辑 (保持原样)
        self.spawn_timer += dt
        if self.spawn_timer >= 1.5:
            self._spawn_enemy()
            self.spawn_timer = 0

        # 系统更新
        self.all_sprites.update(dt)
        self.weapon_manager.update(dt)

        # 碰撞处理：子弹 vs 敌人 (保持原样)
        hits = pygame.sprite.groupcollide(self.enemy_group, self.projectile_group, False, False)
        for enemy, bullets in hits.items():
            for bullet in bullets:
                self.engine.ui_manager.spawn_damage_text(enemy.rect.center, bullet.damage)
                if DamageSystem.handle_collision(bullet, enemy):
                    self.engine.on_enemy_killed(enemy)

        # 全局死亡检测 (保持原样)
        for enemy in self.enemy_group:
            if enemy.hp <= 0:
                self.engine.on_enemy_killed(enemy)
                enemy.kill()

        # 玩家受击与捡宝石 (保持原样)
        if pygame.sprite.spritecollide(self.player, self.enemy_group, False):
            self.player.take_damage(1)

        gems_hit = pygame.sprite.spritecollide(self.player, self.gem_group, True)
        for gem in gems_hit:
            self.player.gain_xp(gem.xp_value)
            if self.player.current_xp >= self.player.xp_required:
                self.player.perform_level_up()
                self.engine.state = "UPGRADING"
                self.upgrade_panel.show()

    def draw(self):
        # 渲染流水线 (保持原样)
        self.all_sprites.custom_draw(self.player)
        self.weapon_manager.draw_weapons(self.screen, self.all_sprites.offset)

    def _spawn_enemy(self):
        angle = random.uniform(0, 360)
        dist = 850
        spawn_pos = self.player.pos + pygame.math.Vector2(1, 0).rotate(angle) * dist
        config = registry.enemies.get("basic_grunt")
        if config:
            Enemy(spawn_pos, [self.all_sprites, self.enemy_group], config, self.player)