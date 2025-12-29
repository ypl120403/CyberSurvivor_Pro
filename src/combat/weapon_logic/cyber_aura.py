import pygame
from src.core.registry import registry
from src.combat.weapon_logic.base_weapon import BaseWeapon

@registry.register_logic("cyber_aura")
class CyberAuraWeapon(BaseWeapon):
    def __init__(self, player, groups, config):
        super().__init__(player, groups, config)
        self.tick_timer = 0
        self.aura_surface = None
        self._update_visuals()

    def init_stats(self):
        """从 JSON 等级表更新属性"""
        super().init_stats() # 调用基类读取 level_data
        lvl_data = self.config['levels'].get(str(self.level), {})
        self.radius = lvl_data.get('radius', 150)
        self.tick_rate = lvl_data.get('tick_rate', 0.5)
        # 联动 StatsComponent 的伤害倍率
        self.final_damage = self.damage * self.player.stats.damage_mult.value
        self._update_visuals()

    def _update_visuals(self):
        """根据半径预渲染光环，节省每一帧的绘图开销"""
        size = self.radius * 2
        self.aura_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        # 赛博蓝渐变
        pygame.draw.circle(self.aura_surface, (0, 255, 240, 40), (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.aura_surface, (0, 255, 240, 160), (self.radius, self.radius), self.radius, 2)

    def update(self, dt, enemies):
        # 定时器判定伤害触发
        self.tick_timer += dt
        if self.tick_timer >= self.tick_rate:
            self._apply_aoe(enemies)
            self.tick_timer = 0

    def _apply_aoe(self, enemies):
        # 获取玩家中心点
        p_pos = self.player.pos
        # 判定范围内所有敌人
        for enemy in enemies:
            if p_pos.distance_to(enemy.pos) <= self.radius:
                # 造成伤害并触发击退（如果需要）
                enemy.take_damage(self.final_damage)

    def draw_custom(self, screen, offset):
        """如果需要独立绘制特效，可由 CameraGroup 调用"""
        if self.aura_surface:
            render_pos = self.player.rect.center - offset
            rect = self.aura_surface.get_frect(center=render_pos)
            screen.blit(self.aura_surface, rect)