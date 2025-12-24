import pygame
from combat.weapon_factory import WeaponFactory

class WeaponManager:
    """
    工业级武器管理器：
    1. 负责 6 个武器插槽的生命周期管理。
    2. 协调 WeaponFactory 生成不同逻辑类型的武器（弹道类 vs 挂载类）。
    3. 提供升级候选列表供 UI 系统调用。
    """
    def __init__(self, player, enemy_group, projectile_groups):
        self.player = player
        self.enemy_group = enemy_group
        self.projectile_groups = projectile_groups
        self.max_slots = 6
        self.weapons = {}  # 格式：{ 'weapon_id': weapon_instance }

    def add_or_upgrade_weapon(self, weapon_id):
        """核心业务逻辑：自动判定是升级现有武器还是占用新槽位"""
        # 1. 检查是否已经持有该武器
        if weapon_id in self.weapons:
            self.weapons[weapon_id].level_up()
            return True

        # 2. 检查插槽是否已满
        if len(self.weapons) < self.max_slots:
            # 调用工厂创建实例，传入 player、显示/物理组、以及配置
            new_weapon = WeaponFactory.create_weapon(weapon_id, self.player, self.projectile_groups)
            if new_weapon:
                self.weapons[weapon_id] = new_weapon
                print(f"✅ 已装配新武器逻辑: {weapon_id}")
                return True
        else:
            print(f"🚫 武器插槽已满({self.max_slots})，无法学习新武器: {weapon_id}")
        return False

    def get_upgrade_candidates(self):
        """
        为 UpgradePanel 提供可选列表。
        包含：未满级的已有武器 + 库中未获取的新武器。
        """
        from core.registry import registry
        candidates = []

        # 候选项 A: 已有武器的升级 (Level Up)
        for w_id, w_inst in self.weapons.items():
            if w_inst.level < w_inst.max_level:
                candidates.append({
                    "type": "weapon_upgrade", 
                    "id": w_id, 
                    "level": w_inst.level + 1
                })

        # 候选项 B: 库中尚未获取的新武器 (New Weapon)
        if len(self.weapons) < self.max_slots:
            for w_id in registry.weapons.keys():
                if w_id not in self.weapons:
                    candidates.append({
                        "type": "weapon_new", 
                        "id": w_id
                    })

        return candidates

    def update(self, dt):
        """驱动所有已装备武器的逻辑（如：开火判定、光环判定）"""
        for weapon in list(self.weapons.values()):
            weapon.update(dt, self.enemy_group)

    def draw_weapons(self, screen, camera_offset):
        """
        【新增功能】
        解决非弹道类武器（如赛博光环、磁场）不可见的问题。
        这些武器不是独立的 Sprite，因此需要手动触发它们的绘制逻辑。
        """
        for weapon in self.weapons.values():
            # 如果武器类实现了 draw_custom 方法，则进行绘制
            if hasattr(weapon, 'draw_custom'):
                weapon.draw_custom(screen, camera_offset)

    # --- 工业级兼容性维护 ---
    def add_weapon(self, weapon_instance_or_id):
        """
        保留旧接口兼容性。
        如果传入的是 ID 字符串，自动转入 add_or_upgrade 流程。
        """
        if isinstance(weapon_instance_or_id, str):
            self.add_or_upgrade_weapon(weapon_instance_or_id)
        else:
            # 兼容手动创建实例并直接添加的情况
            w_id = getattr(weapon_instance_or_id, 'id', None)
            if w_id:
                self.weapons[w_id] = weapon_instance_or_id