import pygame
from src.core.registry import registry
from src.combat.weapon_logic.base_weapon import BaseWeapon
from src.entities.bullet import Bullet  # 👈 确保路径指向搬家后的位置
from src.combat.combat_utils import CombatUtils


@registry.register_logic("projectile")
class ProjectileWeapon(BaseWeapon):
    """
    万能弹道逻辑：
    无论你是射箭、打枪、还是雷电法王放电，都用这一个类。
    """

    def update(self, dt, enemies):
        now = pygame.time.get_ticks()

        # 1. 规则：自动读取玩家属性中的“冷却缩减” (CDR)
        cdr_stat = getattr(self.player.stats, 'cooldown_reduction', None)
        reduction = cdr_stat.value if cdr_stat else 0

        # 2. 计算最终冷却时间
        final_cooldown = self.cooldown * (1 - reduction)

        # 3. 判定开火 (雷电法王被动触发时，self.last_shot 会被重置为 0，从而立即开火)
        if now - self.last_shot >= final_cooldown:
            target = CombatUtils.get_nearest_enemy(self.player.pos, enemies)
            if target:
                self.fire(target)
                self.last_shot = now

    def fire(self, target):
        """
        核心规则：一劳永逸的参数化发射。
        所有的子弹颜色、速度、外观都从 self.config 中实时抓取。
        """
        direction = (target.pos - self.player.pos).normalize()

        # --- 数据驱动参数提取 ---
        # 如果 JSON 里没写，就用默认值 (青色、1000速)
        b_color = self.config.get("bullet_color", (0, 255, 255))
        b_speed = self.config.get("bullet_speed", 1000)
        b_size = self.config.get("bullet_size", (12, 6))

        # 4. 循环发射多枚弹药 (如雷电法王一次发多条电弧)
        for i in range(self.bullet_count):
            # 计算扇形散射偏移
            angle_offset = (i - (self.bullet_count - 1) / 2) * 10

            # --- 实例化通用子弹 ---
            # 所有的个性化都通过参数传给 Bullet 类
            Bullet(
                pos=self.player.pos,
                direction=direction.rotate(angle_offset),
                groups=self.groups,
                damage=self.damage,  # 这是 BaseWeapon 算好的(基础*倍率)
                speed=b_speed,
                color=b_color,
                size=b_size
            )