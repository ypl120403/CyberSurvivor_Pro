import pygame
from src.entities.base_entity import BaseEntity
from src.core.constants import *


class Bullet(BaseEntity):
    def __init__(self, pos, direction, groups, damage):
        super().__init__(pos, groups, LAYER_PROJECTILE)
        # 工业化：缓存 Surface 防止重复创建
        self.image = pygame.Surface((12, 6), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 255, 255), (0, 0, 12, 6), border_radius=2)

        # 配合飞行方向旋转子弹贴图
        angle = direction.angle_to(pygame.math.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image, angle)

        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.direction = direction
        self.speed = 1000
        self.damage = damage
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt):
        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        if pygame.time.get_ticks() - self.spawn_time > 1500:
            self.kill()