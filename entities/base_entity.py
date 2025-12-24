import pygame
from core.constants import *

class BaseEntity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, layer=LAYER_BG):
        super().__init__(groups)
        self.z_index = layer
        self.pos = pygame.math.Vector2(pos)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        pass