from src.combat.weapon_factory import WeaponFactory
from src.core.registry import registry

class WeaponManager:
    def __init__(self, player, enemy_group, projectile_groups):
        self.player = player
        self.enemy_group = enemy_group
        self.projectile_groups = projectile_groups
        self.max_slots = 6
        self.weapons = {} # 格式: { 'weapon_id': weapon_instance }

    def add_or_upgrade_weapon(self, weapon_data):
        """
        一劳永逸接口：
        1. 如果传入字符串: 认为是 Registry ID。
        2. 如果传入字典: 认为是自定义武器配置（角色 JSON 嵌套模式）。
        """
        # A. 解析配置与 ID
        if isinstance(weapon_data, str):
            weapon_id = weapon_data
            config = registry.weapons.get(weapon_id)
        else:
            config = weapon_data
            weapon_id = config.get('id', 'temp_id')

        if not config: return False

        # B. 逻辑分发：是升级还是装配？
        if weapon_id in self.weapons:
            self.weapons[weapon_id].level_up()
            return True

        if len(self.weapons) < self.max_slots:
            new_weapon = WeaponFactory.create_weapon_by_data(config, self.player, self.projectile_groups)
            if new_weapon:
                self.weapons[weapon_id] = new_weapon
                return True
        else:
            print(f"🚫 插槽已满，无法装配: {weapon_id}")
        return False

    def update(self, dt):
        for weapon in list(self.weapons.values()):
            weapon.update(dt, self.enemy_group)

    def draw_weapons(self, screen, camera_offset):
        for weapon in self.weapons.values():
            if hasattr(weapon, 'draw_custom'):
                weapon.draw_custom(screen, camera_offset)

    def get_upgrade_candidates(self):
        """规则：自动获取升级选项"""
        candidates = []
        # 已有武器升级
        for w_id, w_inst in self.weapons.items():
            if w_inst.level < w_inst.max_level:
                candidates.append({"type": "weapon_upgrade", "id": w_id, "level": w_inst.level + 1})
        # 新武器发现 (从 Registry 加载)
        if len(self.weapons) < self.max_slots:
            for w_id in registry.weapons.keys():
                if w_id not in self.weapons:
                    candidates.append({"type": "weapon_new", "id": w_id})
        return candidates