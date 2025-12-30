import pygame
from src.core.event_bus import bus


class BaseWeapon:
    """
    通用武器基类 (Universal Weapon Base)
    负责解释 12 维度 JSON 协议中的：
    - 维度 4: 属性加成 (Equip Buffs)
    - 维度 5: 特权标签 (Privilege Tags)
    - 维度 7: 成长进化 (Progression)
    - 维度 9: 资源频率 (Resource/Cooldown)
    """

    def __init__(self, player, groups, config):
        self.player = player
        self.groups = groups  # 通常是 [all_sprites, projectile_group]
        self.config = config
        self.id = config.get('id', config.get('weapon_id', 'unknown_wpn'))

        # --- 维度 7: 生命周期与等级管理 ---
        self.level = 1
        self.max_level = config.get('max_level', 5)
        self.is_active = True

        # --- 维度 9: 运行时资源状态 ---
        self.last_shot = 0

        # --- 核心初始化流程 ---
        self._apply_static_buffs()  # 注入维度 4
        self._register_privilege_tags()  # 注入维度 5
        self.init_stats()  # 初始化维度 7 的数值映射

    def _apply_static_buffs(self):
        """维度 4: 装备即获得的固定属性加成 (Equip Buffs)"""
        # 兼容两种路径：config['stats']['on_equip'] 或 config['static_buffs']
        stats_node = self.config.get("stats", {})
        buffs = stats_node.get("on_equip", self.config.get("static_buffs", {}))

        for stat_name, value in buffs.items():
            if hasattr(self.player.stats, stat_name):
                # 调用 StatsComponent 的 add_modifier
                self.player.stats.add_modifier(stat_name, value, is_percent=False)
                print(f"🛠️ [Equip] {self.id} 强化属性: {stat_name} +{value}")

    def _register_privilege_tags(self):
        """维度 5: 机制特权标签 (Privilege Tags)"""
        stats_node = self.config.get("stats", {})
        tags = stats_node.get("tags", self.config.get("tags", []))

        if not hasattr(self.player, 'privilege_tags'):
            self.player.privilege_tags = set()

        for tag in tags:
            self.player.privilege_tags.add(tag)
            print(f"🔗 [Privilege] {self.id} 激活特权: {tag}")

    def init_stats(self):
        """
        维度 7: 属性实时映射
        根据当前 self.level 从 JSON 的 levels 字典中抓取数值
        """
        lvl_key = str(self.level)
        levels_config = self.config.get('levels', {})

        # 寻找当前等级的数据，如果没有，则尝试读取根目录的默认值
        lvl_data = levels_config.get(lvl_key, {})

        # 统一属性映射 (伤害、冷却、数量)
        self.damage = lvl_data.get('damage', self.config.get('damage', 10))
        self.cooldown = lvl_data.get('cooldown',
                                     self.config.get('logic', {}).get('cooldown', 800))
        self.bullet_count = lvl_data.get('count',
                                         self.config.get('params', {}).get('count', 1))

        # 扩展：读取当前阶段的运动数据 (维度 1)
        self.phases = lvl_data.get('phases', self.config.get('logic', {}).get('phases', []))

    def level_up(self):
        """
        核心修复：实现升级协议。
        所有派生类（如 TeslaArcWeapon）通过 super().level_up() 即可完成属性刷新。
        """
        if self.level < self.max_level:
            self.level += 1
            self.init_stats()
            print(f"🔝 [Upgrade] {self.config.get('name', self.id)} 晋升至 LV.{self.level}")
        else:
            print(f"⭐ [Max] {self.id} 已达到最高等级")

    def update(self, dt, enemies):
        """维度 9: 资源与频率控制中心"""
        if not self.is_active: return

        now = pygame.time.get_ticks()

        # 耦合 StatsComponent 的冷却缩减 (CDR)
        cdr_stat = getattr(self.player.stats, 'cooldown_reduction', None)
        reduction = cdr_stat.value if cdr_stat else 0
        final_cooldown = self.cooldown * (1 - reduction)

        if now - self.last_shot >= final_cooldown:
            # 维度 8: 索敌逻辑
            target = self.get_target(enemies)
            # 如果是面向方向攻击或找到了目标
            if target or self.config.get("targeting") == "facing_direction":
                self.fire(target)
                self.last_shot = now

    def get_target(self, enemies):
        """维度 8: 索敌过滤系统"""
        mode = self.config.get("targeting", "closest")
        from src.combat.combat_utils import CombatUtils

        if mode == "closest":
            return CombatUtils.get_nearest_enemy(self.player.pos, enemies)
        elif mode == "random":
            import random
            enemy_list = enemies.sprites()
            return random.choice(enemy_list) if enemy_list else None
        return None

    def fire(self, target):
        """
        维度 2: 弹道分布。
        这里预留给 UniversalProjectile 或子类重写。
        """
        pass