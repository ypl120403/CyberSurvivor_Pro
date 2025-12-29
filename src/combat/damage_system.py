import pygame


class DamageSystem:
    @staticmethod
    def handle_collision(bullet, enemy):
        # 1. 基础伤害计算（未来可以在这里加入暴击判定）
        damage = bullet.damage

        # 2. 敌人扣血
        is_dead = enemy.take_damage(damage)

        # 3. 子弹处理（目前简单处理为命中消失）
        bullet.kill()

        return is_dead