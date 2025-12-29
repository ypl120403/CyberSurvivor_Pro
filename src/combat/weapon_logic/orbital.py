import pygame
import math
from src.core.registry import registry
from src.combat.weapon_logic.base_weapon import BaseWeapon


@registry.register_logic("orbital")
class OrbitalWeapon(BaseWeapon):
    def __init__(self, player, groups, config):
        # 必须先调用父类初始化
        super().__init__(player, groups, config)
        # 初始化旋转角度和基础半径
        self.angle = 0.0
        self.base_radius = 120
        self.rotation_speed = 5.0

    def init_stats(self):
        """从 JSON 等级表更新轨道属性"""
        super().init_stats()
        lvl_data = self.config.get('levels', {}).get(str(self.level), {})
        # 优先读取 JSON 中的半径和速度，没有则用默认值
        self.base_radius = lvl_data.get('radius', 120)
        self.rotation_speed = lvl_data.get('speed', 5.0)

    def update(self, dt, enemies):
        # 1. 计算旋转：速度受玩家伤害加成影响（也可以改为受攻击频率加成）
        speed_mult = getattr(self.player.stats.damage_mult, 'value', 1.0)
        self.angle += self.rotation_speed * dt * speed_mult

        # 2. 计算半径：受玩家“攻击范围”加成（如果有该属性）
        area_stat = getattr(self.player.stats, 'attack_area', None)
        final_radius = self.base_radius * (area_stat.value if area_stat else 1.0)

        # 3. 计算当前位置 (环绕玩家)
        offset = pygame.math.Vector2(math.cos(self.angle), math.sin(self.angle)) * final_radius
        current_pos = self.player.pos + offset

        # 4. 碰撞判定：对半径内的敌人造成伤害
        # 这里的 30 是轨道球的大小，未来也可以写进 JSON
        hit_radius = 30 * (area_stat.value if area_stat else 1.0)
        final_damage = self.damage * self.player.stats.damage_mult.value

        from src.combat.damage_system import DamageSystem
        for enemy in enemies:
            if current_pos.distance_to(enemy.pos) < hit_radius:
                # 轨道类武器通常是每帧造成少量伤害
                DamageSystem.apply_damage(self.player.engine, enemy, final_damage * dt * 5)

    def draw_custom(self, screen, offset):
        """绘制轨道球视觉效果"""
        area_stat = getattr(self.player.stats, 'attack_area', None)
        final_radius = self.base_radius * (area_stat.value if area_stat else 1.0)

        pos = self.player.pos + pygame.math.Vector2(math.cos(self.angle), math.sin(self.angle)) * final_radius
        draw_pos = pos - offset

        # 绘制赛博感的光球
        pygame.draw.circle(screen, (0, 255, 200), draw_pos, 15)
        pygame.draw.circle(screen, (255, 255, 255), draw_pos, 15, 2)