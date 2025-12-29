import pygame
import math
from src.core.registry import registry
from src.combat.weapons.base_weapon import BaseWeapon


@registry.register_logic("orbital")
class OrbitalWeapon(BaseWeapon):
    def update(self, dt, enemies):
        # 规则：旋转速度受到玩家“攻击速度/冷却”属性的影响
        # 如果没有这个属性，stats.py 里的 defaults 会给 1.0
        self.angle += 5 * dt * self.player.stats.damage_mult.value  # 假设伤害高转得快

        # 规则：轨道半径受到玩家“攻击范围”加成
        final_radius = self.radius * self.player.stats.attack_area.value

        # 环绕逻辑
        offset = pygame.math.Vector2(math.cos(self.angle), math.sin(self.angle)) * final_radius
        current_pos = self.player.pos + offset

        # 碰撞计算
        final_damage = self.damage * self.player.stats.damage_mult.value
        for enemy in enemies:
            if current_pos.distance_to(enemy.pos) < (30 * self.player.stats.attack_area.value):
                enemy.take_damage(final_damage * dt * 5)