import pygame
from core.registry import registry
from combat.weapons.base_weapon import BaseWeapon
from combat.projectiles.bullet import Bullet
from combat.combat_utils import CombatUtils

@registry.register_logic("projectile")  # <--- 补上这一句
class ProjectileWeapon(BaseWeapon):
    def update(self, dt, enemies):
        now = pygame.time.get_ticks()
        # 自动读取 Player 的冷却缩减属性
        cdr = getattr(self.player.stats, 'cooldown_reduction', None)
        reduction = cdr.value if cdr else 0

        if now - self.last_shot >= self.cooldown * (1 - reduction):
            target = CombatUtils.get_nearest_enemy(self.player.pos, enemies)
            if target:
                self.fire(target)
                self.last_shot = now

    def fire(self, target):
        direction = (target.pos - self.player.pos).normalize()
        for i in range(self.bullet_count):
            angle_offset = (i - (self.bullet_count - 1) / 2) * 10
            # 这里 groups 已经在 BaseWeapon.__init__ 中保存为 self.groups
            Bullet(self.player.pos, direction.rotate(angle_offset), self.groups, self.damage)