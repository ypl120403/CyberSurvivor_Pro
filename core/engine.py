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
        pygame.display.set_caption("CyberSurvivor Pro")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "PLAYING"

        # 1. 核心数据与逻辑发现
        registry.load()
        # 确保在创建武器前完成逻辑类的自动注册
        WeaponFactory.auto_discover_logic()

        # 2. 初始化渲染组与物理组
        self.all_sprites = CameraGroup()
        self.enemy_group = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        self.gem_group = pygame.sprite.Group()

        # 3. 创建实体 (将 self 传入 Player 以便 UI 访问引擎逻辑)
        self.player = Player((WIDTH // 2, HEIGHT // 2), [self.all_sprites], self)
        self.score = 0
        self.spawn_timer = 0

        # 4. 挂载管理器与 UI
        self.hud = HUD(self.player)
        self.upgrade_panel = UpgradePanel(self.player)
        self.weapon_manager = WeaponManager(
            self.player,
            self.enemy_group,
            [self.all_sprites, self.projectile_group]
        )

        # 5. 初始武器装配 (此处可根据需求切换)
        # 想要原版远程武器: "starter_gun"
        # 想要赛博光环: "cyber_aura"
        self.weapon_manager.add_or_upgrade_weapon("starter_gun")

        # 6. 订阅全局通信
        bus.subscribe("RESUME_GAME", self.resume)

    def resume(self):
        """由 UpgradePanel 通过 EventBus 触发，恢复游戏运行"""
        self.state = "PLAYING"

    def run(self):
        """主循环：严格分离事件、更新、渲染"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            # --- 事件处理 ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # --- 逻辑更新 ---
            if self.state == "PLAYING":
                self.update_game(dt)

            # --- 渲染绘制 (注意层级顺序) ---
            # 1. 绘制所有标准 Sprite (背景网格、角色、怪物、子弹)
            self.all_sprites.custom_draw(self.player)

            # 2. 【核心修复】绘制非弹道类武器效果 (如光环)
            # 必须在 custom_draw 之后调用，使用摄像机偏移量 camera.offset
            self.weapon_manager.draw_weapons(self.screen, self.all_sprites.offset)

            # 3. 绘制 HUD (常驻 UI)
            self.hud.draw(self.score)

            # 4. 绘制升级面板 (覆盖层)
            if self.state == "UPGRADING":
                self.upgrade_panel.draw()

            pygame.display.flip()

    def on_enemy_killed(self, enemy):
        """
        【工业化提取】统一的敌人死亡处理函数。
        无论是被子弹打死，还是被光环烫死，都调用此逻辑，确保不遗漏分数和经验掉落。
        """
        self.score += enemy.config.get("score_value", 10)

        # 掉落经验宝石
        from entities.pickups.exp_gem import ExperienceGem
        ExperienceGem(
            enemy.rect.center,
            [self.all_sprites, self.gem_group],
            self.player
        )

    def update_game(self, dt):
        """游戏运行状态的核心逻辑"""
        # 1. 刷怪逻辑
        self.spawn_timer += dt
        if self.spawn_timer >= 1.5:
            self.spawn_enemy()
            self.spawn_timer = 0

        # 2. 系统更新
        self.all_sprites.update(dt)
        self.weapon_manager.update(dt)

        # 3. 碰撞处理 - 弹道 vs 敌人
        hits = pygame.sprite.groupcollide(self.enemy_group, self.projectile_group, False, False)
        for enemy, bullets in hits.items():
            for bullet in bullets:
                # DamageSystem 返回 True 代表敌人死亡
                if DamageSystem.handle_collision(bullet, enemy):
                    self.on_enemy_killed(enemy)

        # 4. 【核心修复】全局死亡判定 (解决非弹道武器杀敌不触发掉落的问题)
        for enemy in self.enemy_group:
            if enemy.hp <= 0:
                self.on_enemy_killed(enemy)
                enemy.kill()  # 确保在渲染循环中移除

        # 5. 碰撞处理 - 玩家 vs 敌人 (受击)
        if pygame.sprite.spritecollide(self.player, self.enemy_group, False):
            # 这里的伤害值未来可以从敌人配置读取
            self.player.take_damage(1)

        # 6. 碰撞处理 - 玩家 vs 经验宝石 (升级逻辑)
        gems_hit = pygame.sprite.spritecollide(self.player, self.gem_group, True)
        for gem in gems_hit:
            self.player.gain_xp(gem.xp_value)
            # 检查升级
            if self.player.current_xp >= self.player.xp_required:
                self.player.perform_level_up()
                self.state = "UPGRADING"
                self.upgrade_panel.show()

    def spawn_enemy(self):
        """在屏幕外随机位置生成敌人"""
        angle = random.uniform(0, 360)
        dist = 850  # 略大于屏幕对角线距离
        spawn_pos = self.player.pos + pygame.math.Vector2(1, 0).rotate(angle) * dist

        config = registry.enemies.get("basic_grunt")
        if config:
            Enemy(spawn_pos, [self.all_sprites, self.enemy_group], config, self.player)