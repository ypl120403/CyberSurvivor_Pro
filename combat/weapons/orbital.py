import pygame
import math
from core.registry import registry
from combat.weapons.base_weapon import BaseWeapon


@registry.register_logic("orbital")  # <--- 补上这一句
class OrbitalWeapon(BaseWeapon):
    def __init__(self, player, groups, config):
        super().__init__(player, groups, config)
        self.angle = 0
        self.radius = 120
        # 视觉：创建一个常驻光环 Surface
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 255, 100), (20, 20), 20, 3)

    def update(self, dt, enemies):
        self.angle += 5 * dt
        # 环绕逻辑
        offset = pygame.math.Vector2(math.cos(self.angle), math.sin(self.angle)) * self.radius
        current_pos = self.player.pos + offset

        # 简易碰撞：光环范围内敌人受伤
        for enemy in enemies:
            if current_pos.distance_to(enemy.pos) < 30:
                enemy.take_damage(self.damage * dt * 5)

    def draw_custom(self, screen, offset):
        """如果想让环绕武器也有特殊特效绘制，可以在这里写逻辑"""
        pass