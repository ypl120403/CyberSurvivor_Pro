import pygame
from src.core.registry import registry
from src.combat.weapon_logic.base_weapon import BaseWeapon
from src.entities.area_effect import AreaEffectEntity


@registry.register_logic("AreaEffectEntity")
class AreaEffectWeapon(BaseWeapon):
    def __init__(self, player, groups, config):
        super().__init__(player, groups, config)
        self.aura_inst = None

        # 核心修复：从所有组中筛选出渲染组(CameraGroup)，排除碰撞组(projectile_group)
        # 这样 AreaEffectEntity 就只会画出来，而不会被当作子弹去撞人
        from src.core.camera import CameraGroup
        self.render_groups = [g for g in self.groups if isinstance(g, CameraGroup)]

    def update(self, dt, enemies):
        now = pygame.time.get_ticks()
        is_attached = self.config.get("behavior", {}).get("is_attached", False)

        if is_attached:
            if not self.aura_inst or not self.aura_inst.alive():
                # 使用过滤后的渲染组
                self.aura_inst = AreaEffectEntity(
                    self.player.pos, self.render_groups, self.player, self.config
                )
        else:
            if now - self.last_shot >= self.cooldown:
                # 使用过滤后的渲染组
                AreaEffectEntity(self.player.pos, self.render_groups, self.player, self.config)
                self.last_shot = now