import pygame
import math
from src.entities.base_entity import BaseEntity
from src.core.constants import *


class UniversalProjectile(BaseEntity):
    def __init__(self, pos, direction, groups, player, weapon_config):
        super().__init__(pos, groups, LAYER_PROJECTILE)
        self.player = player
        self.config = weapon_config
        self.direction = direction
        self.pos = pygame.math.Vector2(pos)

        # 维度 1: 提取阶段状态机
        logic_node = self.config.get("logic", {})
        self.phases = logic_node.get("phases", [{"type": "linear", "speed": 800, "duration": 2.0}])
        self.current_phase_idx = 0
        self.phase_timer = 0.0

        # 维度 3: 基础伤害与属性
        self.damage = weapon_config.get("damage", 10) * player.stats.damage_mult.value

        # 视觉初始化
        self._init_visuals()

    def _init_visuals(self):
        viz = self.config.get("visuals", {})
        size = viz.get("bullet_size", [15, 15])
        color = viz.get("color", [255, 255, 255])
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size[0] // 2, size[1] // 2), size[0] // 2)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        if self.current_phase_idx >= len(self.phases):
            self.kill()
            return

        phase = self.phases[self.current_phase_idx]
        self.phase_timer += dt

        # 阶段切换判定
        if self.phase_timer >= phase.get("duration", 1.0):
            self.current_phase_idx += 1
            self.phase_timer = 0
            return

        # 执行运动 (维度 1)
        self._move(phase, dt)
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def _move(self, phase, dt):
        p_type = phase.get("type", "linear")

        if p_type == "linear":
            speed = phase.get("speed", 600)
            self.pos += self.direction * speed * dt

        elif p_type == "rotate":
            # 这里的旋转角度是内部维护的
            angle = pygame.time.get_ticks() * 0.01 * phase.get("rotation_speed", 10)
            radius = phase.get("radius", 30)
            self.pos += pygame.Vector2(math.cos(angle), math.sin(angle)) * radius * dt

        elif p_type == "homing_player":
            # 回旋镖的核心：向玩家坐标移动
            to_player = self.player.pos - self.pos
            if to_player.length() > 0:
                accel = phase.get("accel", 500)
                speed = phase.get("speed_start", 200) + accel * self.phase_timer
                self.pos += to_player.normalize() * speed * dt
                if to_player.length() < 20: self.kill()

    def on_hit(self):
        # 可以在这里处理碰撞分裂等逻辑 (维度 3)
        self.kill()