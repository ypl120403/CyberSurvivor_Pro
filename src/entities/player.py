import pygame
import random
from src.entities.base_entity import BaseEntity
from src.entities.components.stats import StatsComponent
from src.core.constants import *
from src.core.registry import registry


class Player(BaseEntity):
    def __init__(self, pos, groups, engine, char_config):
        super().__init__(pos, groups, LAYER_PLAYER)
        self.engine = engine

        # 1. 核心：保存整份 JSON 配置（角色的“灵魂”）
        self.char_config = char_config
        self.char_id = char_config.get('id', 'default')

        # 2. 属性初始化
        self.stats = StatsComponent(char_config.get('base_stats', {}))

        # 3. 视觉初始化
        self.flash_timer = 0  # 用于触发被动时的闪光反馈
        self._init_visuals(char_config)

        # 4. 运行时数值
        self.current_hp = self.stats.max_health.value
        self.current_xp = 0
        self.xp_required = 100
        self.level = 1

        # 5. 战斗状态
        self.vulnerable = True
        self.hurt_time = 0

        # 获取被动技能列表（一劳永逸：以后加新被动只需在这里写逻辑，JSON里调参数）
        self.passives = char_config.get('passives', [])

    def _init_visuals(self, char_config):
        """自动化视觉：根据ID匹配资产，没资产则画圆"""
        char_tex = registry.get_texture(f"characters/{self.char_id}")

        if char_tex.get_width() > 32:
            self.image = pygame.transform.scale(char_tex, (48, 48))
        else:
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            theme_color = char_config.get('theme_color', COLOR_PLAYER)
            pygame.draw.circle(self.image, theme_color, (20, 20), 20)
            pygame.draw.circle(self.image, (255, 255, 255), (20, 20), 20, 2)

        self.original_image = self.image.copy()  # 备份原图用于闪光特效
        self.rect = self.image.get_rect(center=self.pos)

    # --- 一劳永逸的被动系统 ---

    # src/entities/player.py

    def trigger_passives(self, trigger_type):
        """
        根据触发类型遍历 JSON 定义的所有被动
        """
        for p_data in self.passives:
            # JSON 中的 type 需对应触发点 (如 "on_kill")
            if p_data.get('type') == trigger_type:
                self._execute_passive_logic(p_data)

    def _execute_passive_logic(self, p_data):
        """
        具体的行为逻辑：
        这里可以根据 p_data.get('effect') 来路由不同的功能
        """
        # 获取效果类型 (在 JSON 中统一定义为 "refresh_cooldown")
        effect = p_data.get('effect')
        chance = p_data.get('chance', 1.0)  # 默认 100%

        if effect == "refresh_cooldown":
            if random.random() < chance:
                self.refresh_weapon_cooldowns()
                # 视觉反馈：调用 UI Manager 弹出提示或震屏（后续可加）

    def refresh_weapon_cooldowns(self):
        """逻辑：瞬间重置所有武器冷却时间"""
        # 获取当前场景的武器管理器
        scene = self.engine.scene
        if hasattr(scene, 'weapon_manager'):
            for weapon in scene.weapon_manager.weapons.values():
                weapon.last_shot = 0  # 暴力重置时间戳

            # 视觉反馈：触发白色闪烁
            self.flash_timer = 0.15
            print("⚡ 雷电法王：被动触发！所有武器冷却已重置！")

    # --- 基础战斗逻辑 ---

    def take_damage(self, amount):
        if self.vulnerable:
            self.current_hp -= max(1, amount)
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()
            # 预留：这里以后可以加 trigger_passives("on_hurt")

    def gain_xp(self, amount):
        self.current_xp += amount

    def perform_level_up(self):
        self.level += 1
        self.current_xp -= self.xp_required
        self.xp_required = int(self.xp_required * 1.3)
        self.current_hp = self.stats.max_health.value
        self.trigger_passives("on_level_up")  # 预留：升级触发被动

    def update(self, dt):
        # 1. 移动逻辑
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
            (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        )
        if direction.length() > 0: direction = direction.normalize()
        self.pos += direction * self.stats.move_speed.value * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # 2. 无敌恢复
        if not self.vulnerable:
            if pygame.time.get_ticks() - self.hurt_time >= 500:
                self.vulnerable = True

        # 3. 特效处理 (被动触发时的闪光)
        if self.flash_timer > 0:
            self.flash_timer -= dt
            # 将图片变白
            white_surf = self.original_image.copy()
            white_surf.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            self.image = white_surf
        else:
            self.image = self.original_image

    def on_enemy_killed(self):
        # 遍历 JSON 里的被动列表
        for p in self.char_config.get('passives', []):
            if p.get('type') == "on_kill" and p.get('effect') == "refresh_cooldown":
                if random.random() < p.get('chance', 0):
                    self.refresh_all_cooldowns()

    def refresh_all_cooldowns(self):
        # 找到武器管家，把所有武器的 last_shot 归零
        wm = getattr(self.engine.scene, 'weapon_manager', None)
        if wm:
            for w in wm.weapons.values(): w.last_shot = 0
            self.flash_timer = 0.1  # 触发个闪光反馈