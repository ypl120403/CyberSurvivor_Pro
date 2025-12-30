import pygame
from src.entities.base_entity import BaseEntity
from src.core.constants import *
from src.combat.damage_system import DamageSystem


class AreaEffectEntity(BaseEntity):
    def __init__(self, pos, groups, player, config):
        # 初始图层设为底层 (LAYER_BG 或新开 LAYER_EFFECT)
        super().__init__(pos, groups, LAYER_BG)
        self.player = player
        self.config = config
        self.behavior = config.get("behavior", {})
        self.effect_data = config.get("on_hit_effect", {})

        # 1. 生命周期管理
        self.max_duration = self.behavior.get("max_duration", float('inf'))
        self.life_timer = 0.0

        # 2. Tick 系统
        self.tick_interval = self.behavior.get("tick_interval", 0.5)
        self.tick_timer = 0.0

        # 3. 初始位置同步
        self.is_attached = self.behavior.get("is_attached", False)
        if self.is_attached:
            self.pos = pygame.math.Vector2(self.player.pos)

    def update(self, dt):
        # A. 存活判定
        self.life_timer += dt
        if self.life_timer >= self.max_duration:
            self.kill()
            return

        # B. 位置同步 (光环模式)
        if self.is_attached:
            self.pos = pygame.math.Vector2(self.player.pos)

        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # C. Tick 触发逻辑
        self.tick_timer += dt
        if self.tick_timer >= self.tick_interval:
            self._execute_area_logic()
            self.tick_timer = 0

    def _execute_area_logic(self):
        """核心空间扫描：根据属性加成实时计算范围"""
        # 实时从 Player Stats 抓取加成
        stats = self.player.stats
        final_radius = self.config.get("radius", 100) * stats.attack_area.value
        final_damage = self.config.get("damage", 10) * stats.damage_mult.value

        # 获取当前场景的敌人组
        scene = self.player.engine.scene
        if not hasattr(scene, 'enemy_group'): return

        for enemy in scene.enemy_group:
            # 距离检测
            if self.pos.distance_to(enemy.pos) <= final_radius:
                # 调用统一伤害系统
                DamageSystem.apply_damage(self.player.engine, enemy, final_damage)
                # 预留：此处可扩展 debuff 逻辑
                # if "debuff" in self.effect_data: apply_debuff(enemy, self.effect_data['debuff'])

    def draw_custom(self, screen, offset):
        """视觉表现：根据形状模版绘制"""
        stats = self.player.stats
        final_radius = self.config.get("radius", 100) * stats.attack_area.value

        draw_pos = self.pos - offset
        shape = self.behavior.get("shape", "circle")
        color = self.config.get("vfx_color", (0, 255, 240, 50))  # 半透明赛博色

        if shape == "circle":
            # 绘制内层发光
            pygame.draw.circle(screen, color, draw_pos, final_radius)
            # 绘制外层轮廓
            pygame.draw.circle(screen, (color[0], color[1], color[2], 200), draw_pos, final_radius, 2)