import pygame
from combat.weapons.base_weapon import BaseWeapon
from combat.projectiles.bullet import Bullet
from combat.combat_utils import CombatUtils


class ProjectileWeapon(BaseWeapon):
    def update(self, dt, enemies):
        now = pygame.time.get_ticks()
        # 自动获取玩家的冷却缩减
        reduction = getattr(self.player.stats.cooldown_reduction, 'value', 0)

        if now - self.last_shot >= self.cooldown * (1 - reduction):
            target = CombatUtils.get_nearest_enemy(self.player.pos, enemies)
            if target:
                self.fire(target)
                self.last_shot = now

    def fire(self, target):
        direction = (target.pos - self.player.pos).normalize()
        for i in range(self.bullet_count):
            angle = (i - (self.bullet_count - 1) / 2) * 10
            Bullet(self.player.pos, direction.rotate(angle), self.groups, self.damage)