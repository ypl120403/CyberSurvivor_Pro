import pygame
import random
from src.entities.base_entity import BaseEntity
from src.entities.components.stats import StatsComponent
from src.core.constants import *


class Enemy(BaseEntity):
    def __init__(self, pos, groups, config, player):
        super().__init__(pos, groups, LAYER_ENEMY)
        self.player = player
        self.config = config

        # 挂载属性组件
        self.stats = StatsComponent(config)
        self.hp = self.stats.health.value

        # 视觉
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, COLOR_ENEMY, (0, 0, 30, 30), border_radius=4)
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        # 基础追击逻辑
        direction = self.player.pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()

        self.pos += direction * self.stats.move_speed.value * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True  # 返回死亡信号
        return False