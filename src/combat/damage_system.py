import pygame


class DamageSystem:
    @staticmethod
    def apply_damage(engine, victim, amount, attacker=None):
        """
        全量伤害接口：所有伤害必须经过这里！
        1. 扣血
        2. 弹出伤害数字
        3. 判定死亡并生成经验
        """
        # 1. 扣血并获取死亡状态
        is_dead = victim.take_damage(amount)

        # 2. 统一触发 UI 数字
        engine.ui_manager.spawn_damage_text(victim.rect.center, amount)

        # 3. 判定死亡并触发全球信号
        if is_dead:
            engine.on_enemy_killed(victim)

        return is_dead

    @staticmethod
    def handle_collision(bullet, enemy, engine):
        """专门给 Projectile 这种有实体碰撞的武器使用"""
        is_dead = DamageSystem.apply_damage(engine, enemy, bullet.damage, bullet)
        bullet.on_hit()  # 处理子弹穿透或销毁
        return is_dead