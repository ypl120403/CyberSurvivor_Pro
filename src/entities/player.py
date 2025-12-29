# entities/player.py
import pygame
from src.entities.base_entity import BaseEntity
from src.entities.components.stats import StatsComponent
from src.core.constants import *
from src.core.registry import registry


class Player(BaseEntity):
    def __init__(self, pos, groups, engine, char_config):
        # 1. 初始化基类
        super().__init__(pos, groups, LAYER_PLAYER)
        self.engine = engine

        # 2. 一劳永逸：直接把 JSON 里的 base_stats 字典喂给属性组件
        # 以后你在 JSON 里加 "luck": 99，属性组件会自动生成它
        self.char_id = char_config.get('id', 'default')
        self.stats = StatsComponent(char_config.get('base_stats', {}))

        # 3. 自动化视觉逻辑
        self._init_visuals(char_config)

        # 4. 运行时状态 (通过计算属性获取)
        self.current_hp = self.stats.max_health.value
        self.current_xp = 0
        self.xp_required = 100
        self.level = 1

        # 战斗系统状态
        self.vulnerable = True
        self.hurt_time = 0

    def _init_visuals(self, char_config):
        """规则：自动寻找资产，没资产则画圆"""
        # 尝试寻找 ID 对应的贴图 (例如: characters/cypher_ghost)
        char_tex = registry.get_texture(f"characters/{self.char_id}")

        # 规则：如果图片宽度大于 32，说明加载到了真实资产
        if char_tex.get_width() > 32:
            self.image = pygame.transform.scale(char_tex, (48, 48))
        else:
            # 备选方案：画一个赛博风格的圆圈，颜色可以在 JSON 中定义，默认青色
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            theme_color = char_config.get('theme_color', COLOR_PLAYER)
            pygame.draw.circle(self.image, theme_color, (20, 20), 20)
            pygame.draw.circle(self.image, (255, 255, 255), (20, 20), 20, 2)  # 白边增强

        self.rect = self.image.get_rect(center=self.pos)

    def take_damage(self, amount):
        if self.vulnerable:
            # 可以在这里接入防御力计算：amount -= self.stats.armor.value
            self.current_hp -= max(1, amount)
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()

    def gain_xp(self, amount):
        # 应用经验加成属性：amount *= self.stats.exp_gain.value
        self.current_xp += amount

    def perform_level_up(self):
        self.level += 1
        self.current_xp -= self.xp_required
        self.xp_required = int(self.xp_required * 1.3)
        # 升级瞬间回血
        self.current_hp = self.stats.max_health.value

    def update(self, dt):
        # 1. 移动输入逻辑
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
            (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        )

        if direction.length() > 0:
            direction = direction.normalize()

        # 2. 规则：直接读取 Stats 实时计算出的 move_speed
        self.pos += direction * self.stats.move_speed.value * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # 3. 状态恢复
        if not self.vulnerable:
            if pygame.time.get_ticks() - self.hurt_time >= 500:
                self.vulnerable = True