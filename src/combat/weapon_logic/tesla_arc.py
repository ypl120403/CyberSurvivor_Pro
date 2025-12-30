import pygame
import random
from src.core.registry import registry
from src.combat.weapon_logic.base_weapon import BaseWeapon
from src.combat.combat_utils import CombatUtils
from src.combat.damage_system import DamageSystem


@registry.register_logic("tesla_arc")
class TeslaArcWeapon(BaseWeapon):
    def __init__(self, player, groups, config):
        super().__init__(player, groups, config)
        self.active_arcs = []

    def update(self, dt, enemies):
        now = pygame.time.get_ticks()

        # 直接使用 super().init_stats() 算好的 self.cooldown (已包含等级和 CDR 加成)
        # BaseWeapon 已经帮我们处理了复杂的属性抓取，这里直接用即可
        cdr_stat = getattr(self.player.stats, 'cooldown_reduction', None)
        reduction = cdr_stat.value if cdr_stat else 0
        final_cooldown = self.cooldown * (1 - reduction)

        if now - self.last_shot >= final_cooldown:
            target = CombatUtils.get_nearest_enemy(self.player.pos, enemies)
            if target:
                self.fire_arc(target)
                self.last_shot = now

        # 处理视觉残留
        self.active_arcs = [a for a in self.active_arcs if a['life'] > 0]
        for a in self.active_arcs: a['life'] -= dt

    def fire_arc(self, target):
        # 维度 4: 伤害加成
        final_dmg = self.damage * self.player.stats.damage_mult.value

        # 维度 6: 事件钩子点火 (传入 attacker_config=self.config)
        DamageSystem.apply_damage(self.player.engine, target, final_dmg,
                                  attacker_config=self.config, player=self.player)

        self.active_arcs.append({'pts': self._gen_pts(self.player.pos, target.pos), 'life': 0.1})

    def _gen_pts(self, start, end):
        pts, dist = [start], end - start
        for i in range(1, 4):
            jitter = pygame.Vector2(random.randint(-15, 15), random.randint(-15, 15))
            pts.append(start + dist * (i / 4) + jitter)
        pts.append(end)
        return pts

    def draw_custom(self, screen, offset):
        # 维度 12: 视觉表现
        color = self.config.get("visuals", {}).get("color", (255, 255, 100))
        for a in self.active_arcs:
            draw_pts = [p - offset for p in a['pts']]
            pygame.draw.lines(screen, color, False, draw_pts, 3)
            pygame.draw.lines(screen, (255, 255, 255), False, draw_pts, 1)