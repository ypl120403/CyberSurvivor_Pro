import pygame
from src.core.constants import *


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # 1. 摄像机丝滑跟随逻辑
        # 0.1 是平滑系数，数值越小越丝滑，玩家离中心就越远
        self.offset.x += (player.rect.centerx - WIDTH // 2 - self.offset.x) * 0.1
        self.offset.y += (player.rect.centery - HEIGHT // 2 - self.offset.y) * 0.1

        # 2. 填充底色
        self.display_surface.fill(COLOR_BG)

        # 3. 绘制无限网格 (核心参考物)
        # 根据摄像机偏移计算网格的起始位置
        grid_range = 2  # 绘制范围倍数
        start_x = -int(self.offset.x % TILE_SIZE)
        start_y = -int(self.offset.y % TILE_SIZE)

        for x in range(start_x - TILE_SIZE, WIDTH + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.display_surface, COLOR_GRID, (x, 0), (x, HEIGHT))
        for y in range(start_y - TILE_SIZE, HEIGHT + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.display_surface, COLOR_GRID, (0, y), (WIDTH, y))

        # 4. 排序绘制所有精灵 (Y-sort 伪3D)
        for sprite in sorted(self.sprites(), key=lambda s: (getattr(s, 'z_index', 0), s.rect.centery)):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)