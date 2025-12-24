import pygame
from entities.base_entity import BaseEntity
from entities.components.stats import StatsComponent
from core.constants import *


class Player(BaseEntity):
    def __init__(self, pos, groups, engine):  # 增加 engine 参数
        super().__init__(pos, groups, LAYER_PLAYER)
        self.engine = engine  # 关键：保存引擎引用
        self.stats = StatsComponent({})

        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLOR_PLAYER, (20, 20), 20)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)

        self.current_hp = self.stats.max_health.value
        self.current_xp = 0
        self.xp_required = 100
        self.level = 1
        self.vulnerable = True
        self.hurt_time = 0

    def take_damage(self, amount):
        if self.vulnerable:
            self.current_hp -= amount
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()

    def gain_xp(self, amount):
        self.current_xp += amount

    def perform_level_up(self):
        self.level += 1
        self.current_xp -= self.xp_required
        self.xp_required = int(self.xp_required * 1.3)
        self.current_hp = self.stats.max_health.value

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
            (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        )
        if direction.length() > 0: direction = direction.normalize()
        self.pos += direction * self.stats.move_speed.value * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        if not self.vulnerable:
            if pygame.time.get_ticks() - self.hurt_time >= 500:
                self.vulnerable = True