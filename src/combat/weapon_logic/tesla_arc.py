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
        self.arc_color = config.get("bullet_color", (255, 255, 100))
        self.active_arcs = []  # 存储待渲染的电弧

    def update(self, dt, enemies):
        now = pygame.time.get_ticks()

        # 1. 属性联动：冷却缩减 (CDR)
        cdr_stat = getattr(self.player.stats, 'cooldown_reduction', None)
        reduction = cdr_stat.value if cdr_stat else 0
        final_cooldown = self.cooldown * (1 - reduction)

        # 2. 判定开火 (注意：这里调用的方法名必须与下面定义的一致)
        if now - self.last_shot >= final_cooldown:
            target = CombatUtils.get_nearest_enemy(self.player.pos, enemies)
            if target:
                self.fire_arc(target)  # 👈 确保这里叫 fire_arc
                self.last_shot = now

        # 3. 视觉电弧寿命管理
        self.active_arcs = [a for a in self.active_arcs if a['life'] > 0]
        for a in self.active_arcs:
            a['life'] -= dt

    def fire_arc(self, target):
        """执行伤害并生成电弧视觉数据"""
        # 计算最终伤害 (基础 * 角色倍率)
        final_dmg = self.damage * self.player.stats.damage_mult.value

        # 核心：调用统一伤害接口，确保触发 UI 数字和掉落
        DamageSystem.apply_damage(self.player.engine, target, final_dmg)

        # 记录视觉点位用于 draw_custom 绘制
        self.active_arcs.append({
            'points': self._gen_points(self.player.pos, target.pos),
            'life': 0.1  # 电弧只闪烁 0.1 秒
        })

    def _gen_points(self, start, end):
        """生成具有赛博感的折线电弧"""
        pts = [start]
        dist_vec = end - start
        steps = 4
        for i in range(1, steps):
            mid = start + dist_vec * (i / steps)
            # 添加随机抖动
            jitter = pygame.Vector2(random.randint(-15, 15), random.randint(-15, 15))
            pts.append(mid + jitter)
        pts.append(end)
        return pts

    def draw_custom(self, screen, offset):
        """由 WeaponManager 遍历调用，绕开 Sprite 系统实现高性能绘图"""
        for arc in self.active_arcs:
            # 摄像机坐标转换
            draw_pts = [p - offset for p in arc['points']]
            if len(draw_pts) > 1:
                # 绘制外发光 (粗)
                pygame.draw.lines(screen, self.arc_color, False, draw_pts, 3)
                # 绘制内芯 (白)
                pygame.draw.lines(screen, (255, 255, 255), False, draw_pts, 1)