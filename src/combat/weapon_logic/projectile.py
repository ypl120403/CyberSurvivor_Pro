import pygame
from src.core.registry import registry
from src.combat.weapon_logic.base_weapon import BaseWeapon
from src.entities.universal_projectile import UniversalProjectile

@registry.register_logic("projectile")
class ProjectileWeapon(BaseWeapon):
    def update(self, dt, enemies):
        # 维度 9: 频率控制
        now = pygame.time.get_ticks()
        cdr = getattr(self.player.stats, 'cooldown_reduction', None)
        reduction = cdr.value if cdr else 0
        final_cooldown = self.cooldown * (1 - reduction)

        if now - self.last_shot >= final_cooldown:
            # 维度 8: 索敌
            from src.combat.combat_utils import CombatUtils
            target = CombatUtils.get_nearest_enemy(self.player.pos, enemies)
            if target:
                self.fire(target)
                self.last_shot = now

    def fire(self, target):
        # 维度 2: 弹道分布 (Pattern)
        count = self.bullet_count
        spread = self.config.get("params", {}).get("angle_spread", 15)
        direction = (target.pos - self.player.pos).normalize()

        for i in range(count):
            angle_offset = (i - (count - 1) / 2) * spread
            # 实例化 UniversalProjectile (维度 1: 阶段状态机子弹)
            UniversalProjectile(
                pos=self.player.pos,
                direction=direction.rotate(angle_offset),
                groups=self.groups,
                player=self.player,
                weapon_config=self.config # 👈 传入整份配置以驱动 Phases
            )