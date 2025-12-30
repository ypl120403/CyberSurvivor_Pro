import pygame
import math
from src.core.registry import registry
from src.combat.weapon_logic.base_weapon import BaseWeapon
from src.combat.damage_system import DamageSystem


@registry.register_logic("orbital")
class OrbitalWeapon(BaseWeapon):
    def __init__(self, player, groups, config):
        super().__init__(player, groups, config)
        self.angle = 0.0

    def update(self, dt, enemies):
        # 旋转逻辑
        speed = self.config.get("logic", {}).get("speed", 5.0)
        self.angle += speed * dt * self.player.stats.damage_mult.value

        # 维度 4: 范围加成
        radius = self.config.get("radius", 120) * self.player.stats.attack_area.value

        # 轨道位置
        offset = pygame.math.Vector2(math.cos(self.angle), math.sin(self.angle)) * radius
        current_pos = self.player.pos + offset

        # 维度 6: 碰撞伤害
        final_dmg = self.damage * self.player.stats.damage_mult.value
        for enemy in enemies:
            if current_pos.distance_to(enemy.pos) < 30:  # 30 为碰撞大小
                DamageSystem.apply_damage(self.player.engine, enemy, final_dmg * dt * 5,
                                          attacker_config=self.config, player=self.player)

    def draw_custom(self, screen, offset):
        radius = self.config.get("radius", 120) * self.player.stats.attack_area.value
        pos = self.player.pos + pygame.math.Vector2(math.cos(self.angle), math.sin(self.angle)) * radius
        draw_pos = pos - offset
        color = self.config.get("visuals", {}).get("color", (0, 255, 200))
        pygame.draw.circle(screen, color, draw_pos, 15)
        pygame.draw.circle(screen, (255, 255, 255), draw_pos, 15, 2)