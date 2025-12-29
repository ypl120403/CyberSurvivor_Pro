import pygame
from src.entities.base_entity import BaseEntity
from src.core.constants import *


class ExperienceGem(BaseEntity):
    def __init__(self, pos, groups, player):
        super().__init__(pos, groups, LAYER_PICKUP)
        self.player = player
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (50, 255, 50), [(8, 0), (16, 8), (8, 16), (0, 8)])
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)

        self.xp_value = 20
        self.speed = 0
        self.is_magnetized = False

    def update(self, dt):
        dist_vec = self.player.pos - self.pos
        distance = dist_vec.length()

        if distance < self.player.stats.pickup_range.value:
            self.is_magnetized = True

        if self.is_magnetized:
            self.speed += 40
            if distance > 0:
                self.pos += dist_vec.normalize() * self.speed * dt

        self.rect.center = (round(self.pos.x), round(self.pos.y))