import importlib
import os
from core.registry import registry


class WeaponFactory:
    """
    工业级全自动工厂：
    它会自动扫描目录下的所有 .py 文件，寻找符合协议的武器类。
    """
    _logic_classes = {}

    @classmethod
    def auto_discover_logic(cls):
        """动态发现系统：自动扫描 combat/weapons/ 下的逻辑脚本"""
        cls._logic_classes.clear()
        weapon_dir = "combat/weapons"

        # 遍历文件夹
        for filename in os.listdir(weapon_dir):
            if filename.endswith(".py") and filename not in ["__init__.py", "base_weapon.py"]:
                module_name = f"combat.weapons.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    # 寻找模块内以 'Weapon' 结尾的类 (如 ProjectileWeapon)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and attr_name.endswith("Weapon"):
                            # 建立映射：例如 logic_type "projectile" -> ProjectileWeapon 类
                            logic_id = filename[:-3]
                            cls._logic_classes[logic_id] = attr
                except Exception as e:
                    print(f"❌ 武器逻辑加载失败 [{filename}]: {e}")

        print(f"🛠️  Factory: 逻辑自动发现完成 -> {list(cls._logic_classes.keys())}")

    @classmethod
    def create_weapon(cls, weapon_id, player, groups):
        # 1. 获取 JSON 配置
        config = registry.weapons.get(weapon_id)
        if not config:
            print(f"❌ Registry: 找不到武器配置 ID: {weapon_id}")
            return None

        # 2. 根据 JSON 里的 logic_type 自动匹配已发现的逻辑类
        logic_id = config.get("logic_type")
        logic_class = cls._logic_classes.get(logic_id)

        if logic_class:
            # 统一协议实例化
            return logic_class(player, groups, config)

        print(f"❌ Factory: 无法为 {weapon_id} 匹配到逻辑类型: {logic_id}")
        return None