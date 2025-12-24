import pygame
from combat.weapon_factory import WeaponFactory


class WeaponManager:
    def __init__(self, player, enemy_group, projectile_groups):
        self.player = player
        self.enemy_group = enemy_group
        self.projectile_groups = projectile_groups
        self.max_slots = 6
        self.weapons = {}  # 格式：{ 'weapon_id': weapon_instance }

    def add_or_upgrade_weapon(self, weapon_id):
        """核心方法：处理新武器获取或旧武器升级"""
        if weapon_id in self.weapons:
            self.weapons[weapon_id].level_up()
            return True

        # 检查插槽是否已满
        if len(self.weapons) < self.max_slots:
            new_weapon = WeaponFactory.create_weapon(weapon_id, self.player, self.projectile_groups)
            if new_weapon:
                self.weapons[weapon_id] = new_weapon
                return True
        else:
            print("🚫 武器插槽已满！")
        return False

    def get_upgrade_candidates(self):
        """为升级面板提供可选列表"""
        from core.registry import registry
        candidates = []

        # 1. 已有武器的升级 (如果未满级)
        for w_id, w_inst in self.weapons.items():
            if w_inst.level < w_inst.max_level:
                candidates.append({"type": "weapon_upgrade", "id": w_id, "level": w_inst.level + 1})

        # 2. 新武器的获取 (如果槽位未满)
        if len(self.weapons) < self.max_slots:
            for w_id in registry.weapons.keys():
                if w_id not in self.weapons:
                    candidates.append({"type": "weapon_new", "id": w_id})

        return candidates

    def update(self, dt):
        """更新所有已安装的武器"""
        for weapon in self.weapons.values():
            weapon.update(dt, self.enemy_group)

    # 别名兼容：防止旧代码调用报错
    def add_weapon(self, weapon_instance_or_id):
        if isinstance(weapon_instance_or_id, str):
            self.add_or_upgrade_weapon(weapon_instance_or_id)