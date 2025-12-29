import pygame
from src.core.registry import registry
from src.combat.weapon_logic.base_weapon import BaseWeapon
from src.entities.bullet import Bullet
from src.combat.combat_utils import CombatUtils


@registry.register_logic("projectile")
class ProjectileWeapon(BaseWeapon):
    """
    万能弹道逻辑：
    由 JSON 配置驱动，所有的视觉表现（颜色、速度）都在 Bullet 类内部通过 config 解析。
    """

    def update(self, dt, enemies):
        now = pygame.time.get_ticks()

        # 1. 计算最终冷却（考虑玩家属性加成）
        cdr_stat = getattr(self.player.stats, 'cooldown_reduction', None)
        reduction = cdr_stat.value if cdr_stat else 0
        final_cooldown = self.cooldown * (1 - reduction)

        # 2. 判定开火
        if now - self.last_shot >= final_cooldown:
            target = CombatUtils.get_nearest_enemy(self.player.pos, enemies)
            if target:
                self.fire(target)
                self.last_shot = now

    def fire(self, target):
        """
        核心规则：一劳永逸。
        这里只负责发射，不负责计算子弹的长相和速度。
        长相和速度由 Bullet 类根据 self.config 自动处理。
        """
        direction = (target.pos - self.player.pos).normalize()

        for i in range(self.bullet_count):
            # 计算扇形偏移
            angle_offset = (i - (self.bullet_count - 1) / 2) * 10
            rotated_dir = direction.rotate(angle_offset)

            # 这里的调用顺序必须严格对应 Bullet.__init__ 的顺序：
            # (pos, direction, groups, damage, weapon_config)
            Bullet(
                self.player.pos,    # pos
                rotated_dir,        # direction
                self.groups,        # groups
                self.damage,        # damage
                self.config         # weapon_config (这是一个字典)
            )