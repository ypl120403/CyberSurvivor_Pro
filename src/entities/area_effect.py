import pygame
from src.entities.base_entity import BaseEntity
from src.core.constants import *
from src.combat.damage_system import DamageSystem


class AreaEffectEntity(BaseEntity):
    def __init__(self, pos, groups, player, config):
        # 初始图层设为背景层
        super().__init__(pos, groups, LAYER_BG)
        self.player = player
        self.config = config

        # 1. 行为参数解析
        behavior = config.get("behavior", {})
        self.is_attached = behavior.get("is_attached", True)
        self.max_duration = behavior.get("max_duration", 9999)
        self.tick_interval = behavior.get("tick_interval", 0.5)

        # 2. 状态计时
        self.life_timer = 0.0
        self.tick_timer = 0.0

        # 3. 初始物理位置
        self.pos = pygame.math.Vector2(pos)
        self.rect = pygame.Rect(0, 0, 1, 1)  # 逻辑坐标由 self.pos 驱动

    def update(self, dt):
        # 生命周期管理
        self.life_timer += dt
        if self.life_timer >= self.max_duration:
            self.kill()
            return

        # 位置同步（光环模式跟随玩家，陷阱模式原地不动）
        if self.is_attached:
            self.pos = pygame.math.Vector2(self.player.pos)

        self.rect.center = (round(self.pos.x), round(self.pos.y))

        # 频率触发逻辑
        self.tick_timer += dt
        if self.tick_timer >= self.tick_interval:
            self._execute_area_damage()
            self.tick_timer = 0

    def _execute_area_damage(self):
        """核心：在这里调用统一的单体伤害逻辑"""
        stats = self.player.stats

        # 计算最终半径和伤害 (配置 * 玩家加成)
        final_radius = self.config.get("radius", 100) * stats.attack_area.value
        final_damage = self.config.get("damage", 10) * stats.damage_mult.value

        scene = self.player.engine.scene
        if hasattr(scene, 'enemy_group'):
            for enemy in scene.enemy_group:
                # 空间扫描：如果在圆圈内
                if self.pos.distance_to(enemy.pos) <= final_radius:
                    # --- 一劳永逸：无论什么武器，伤害都走这一个入口 ---
                    DamageSystem.apply_damage(self.player.engine, enemy, final_damage)

    def draw_custom(self, screen, offset):
        """视觉表现：画一个带呼吸感的赛博圆环"""
        stats = self.player.stats
        radius = self.config.get("radius", 100) * stats.attack_area.value
        draw_pos = self.pos - offset

        color = self.config.get("vfx_color", [0, 255, 240, 40])

        # 性能优化：直接在主屏幕上画，不创建多余 Surface
        # 绘制半透明圆（利用圆环宽度模拟）
        pygame.draw.circle(screen, (color[0], color[1], color[2], 30), draw_pos, radius)
        pygame.draw.circle(screen, (color[0], color[1], color[2], 150), draw_pos, radius, 2)