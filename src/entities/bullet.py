import pygame
from src.entities.base_entity import BaseEntity
from src.core.constants import *
from src.core.registry import registry


class Bullet(BaseEntity):
    """
    一劳永逸型子弹：
    支持：1. 自动贴图加载 2. 形状自定义(长条/圆) 3. 动态属性注入
    """

    def __init__(self, pos, direction, groups, damage, weapon_config):
        # 初始图层
        super().__init__(pos, groups, LAYER_PROJECTILE)

        # 1. 核心属性注入 (从武器 JSON 里的 config 字典抓取)
        self.config = weapon_config
        self.speed = weapon_config.get("bullet_speed", 1000)
        self.damage = damage  # 基础伤害 * 角色倍率
        self.life_time = weapon_config.get("life_time", 1500)  # 飞行时长
        self.pierce = weapon_config.get("pierce", 1)  # 穿透力

        # 2. 视觉自动化逻辑
        self._init_visuals(direction)

        # 3. 物理数据
        self.pos = pygame.math.Vector2(pos)
        self.direction = direction
        self.spawn_time = pygame.time.get_ticks()

    def _init_visuals(self, direction):
        """规则：有图贴图，没图按配置画形状"""
        asset_id = self.config.get("texture_id")
        size = self.config.get("bullet_size", (12, 6))
        color = self.config.get("bullet_color", (0, 255, 255))

        # A. 尝试加载贴图
        if asset_id:
            raw_image = registry.get_texture(asset_id)
            if raw_image.get_width() > 32:  # 找到了贴图
                self.image = pygame.transform.scale(raw_image, size)
            else:
                self.image = self._draw_fallback_shape(size, color)
        else:
            # B. 没贴图，画基础形状 (雷电法王目前走这里)
            self.image = self._draw_fallback_shape(size, color)

        # C. 自动根据飞行方向旋转
        angle = direction.angle_to(pygame.math.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()

    def _draw_fallback_shape(self, size, color):
        """规则：根据 JSON 里的 shape 字段画图"""
        surf = pygame.Surface(size, pygame.SRCALPHA)
        shape_type = self.config.get("shape", "rect")

        if shape_type == "circle":
            pygame.draw.circle(surf, color, (size[0] // 2, size[1] // 2), size[0] // 2)
        else:
            # 默认画圆角矩形，看起来更像“能量体”
            pygame.draw.rect(surf, color, (0, 0, size[0], size[1]), border_radius=3)
        return surf

    def on_hit(self):
        """穿透逻辑：被战斗系统调用"""
        self.pierce -= 1
        if self.pierce <= 0:
            self.kill()

    def update(self, dt):
        # 物理移动
        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # 寿命检测
        if pygame.time.get_ticks() - self.spawn_time > self.life_time:
            self.kill()