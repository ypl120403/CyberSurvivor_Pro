from src.combat.weapon_factory import WeaponFactory
from src.core.registry import registry


class WeaponManager:
    """
    12 维度通用武器调度中心
    职责：
    - 负责武器的装配与生命周期管理
    - [维度 7] 处理武器升级与进化 (Evolution)
    - [维度 12] 为 UI 提供动态描述与元数据
    """

    def __init__(self, player, enemy_group, projectile_groups):
        self.player = player
        self.enemy_group = enemy_group
        self.projectile_groups = projectile_groups
        self.max_slots = 6
        self.weapons = {}  # 格式: { 'weapon_id': weapon_instance }

    def add_or_upgrade_weapon(self, weapon_data):
        """
        一劳永逸接口：支持 ID 字符串、嵌套 JSON 或进化后的新武器。
        """
        # A. 解析 ID 和配置 (维度 0)
        config = self._resolve_config(weapon_data)
        if not config:
            return False

        weapon_id = config.get('id', config.get('weapon_id', 'temp_id'))

        # B. 逻辑分发：是进化、升级还是装配？

        # 1. 检查是否触发进化 (维度 7)
        if weapon_id in self.weapons:
            if self._should_evolve(self.weapons[weapon_id]):
                return self._perform_evolution(weapon_id)

            # 2. 普通升级 (维度 7)
            self.weapons[weapon_id].level_up()
            return True

        # 3. 新武器装配
        if len(self.weapons) < self.max_slots:
            new_weapon = WeaponFactory.create_weapon_by_data(config, self.player, self.projectile_groups)
            if new_weapon:
                self.weapons[weapon_id] = new_weapon
                return True
        else:
            print(f"🚫 战斗模组插槽已满: {weapon_id}")
        return False

    def _resolve_config(self, data):
        """解析器：确保能从任何地方抓取到 JSON 配置"""
        if isinstance(data, str):
            return registry.weapons.get(data)
        return data

    def _should_evolve(self, weapon_inst):
        """[维度 7] 判定是否满足进化条件"""
        evolve_cfg = weapon_inst.config.get("evolution")
        if not evolve_cfg: return False

        # 条件：达到满级 且 拥有核心配件
        is_max_level = weapon_inst.level >= weapon_inst.max_level
        # 预留：这里以后可以检查 player.inventory 是否拥有所需道具
        # required_item = evolve_cfg.get("required_items", [])
        return is_max_level

    def _perform_evolution(self, old_id):
        """[维度 7] 执行武器进化：旧武器销毁，新武器降临"""
        old_weapon = self.weapons[old_id]
        evolve_to_id = old_weapon.config.get("evolution", {}).get("evolve_to")

        if not evolve_to_id: return False

        print(f"🌀 [Evolution] {old_id} 正在进化为 {evolve_to_id}!")

        # 1. 移除旧武器（自动卸载属性加成）
        # 注意：BaseWeapon 应该有销毁钩子，此处先简单弹出
        del self.weapons[old_id]

        # 2. 安装进化后的武器
        return self.add_or_upgrade_weapon(evolve_to_id)

    def update(self, dt):
        """维度 9 & 10：驱动所有武器逻辑更新"""
        for weapon in list(self.weapons.values()):
            weapon.update(dt, self.enemy_group)

    def draw_weapons(self, screen, camera_offset):
        """维度 12：驱动自定义渲染（如电弧、光环）"""
        for weapon in self.weapons.values():
            if hasattr(weapon, 'draw_custom'):
                weapon.draw_custom(screen, camera_offset)

    def get_upgrade_candidates(self):
        """
        [维度 12] 为 UI 提供候选清单。
        核心修复：确保专属武器不会丢失配置信息。
        """
        candidates = []

        # 1. 已有武器升级
        for w_id, w_inst in self.weapons.items():
            if w_inst.level < w_inst.max_level:
                candidates.append({
                    "type": "weapon_upgrade",
                    "id": w_id,
                    "level": w_inst.level + 1,
                    "config": w_inst.config  # 👈 注入配置，防止 UI KeyError
                })
            # 检查是否有可用的进化路径
            elif self._should_evolve(w_inst):
                candidates.append({
                    "type": "weapon_evolution",
                    "id": w_id,
                    "config": w_inst.config
                })

        # 2. 新武器发现 (从注册表获取池)
        if len(self.weapons) < self.max_slots:
            for w_id, w_cfg in registry.weapons.items():
                if w_id not in self.weapons:
                    candidates.append({
                        "type": "weapon_new",
                        "id": w_id,
                        "config": w_cfg
                    })
        return candidates

    def get_weapon_metadata(self, weapon_id):
        """[维度 12] UI 专用：获取武器的显示名称和描述，支持实例优先"""
        inst = self.weapons.get(weapon_id)
        if inst:
            return {
                "name": inst.config.get("name", weapon_id),
                "desc": inst.config.get("desc", ""),
                "level": inst.level
            }
        # 降级从注册表获取
        cfg = registry.weapons.get(weapon_id)
        if cfg:
            return {"name": cfg.get("name", weapon_id), "desc": cfg.get("desc", ""), "level": 0}
        return {"name": "未知武装", "desc": "", "level": 0}