import importlib
import os
from core.registry import registry


class WeaponFactory:
    _logic_classes = {}  # 自动存放加载的类

    @classmethod
    def auto_discover_logic(cls):
        """黑科技：自动扫描并加载所有武器逻辑类"""
        path = "combat/weapons"
        for filename in os.listdir(path):
            if filename.endswith(".py") and filename != "__init__.py" and filename != "base_weapon.py":
                module_name = f"combat.weapons.{filename[:-3]}"
                module = importlib.import_module(module_name)
                # 寻找模块中所有以 Weapon 结尾的类
                for name in dir(module):
                    attr = getattr(module, name)
                    if isinstance(attr, type) and name.endswith("Weapon"):
                        # 自动注册，例如 {'projectile': ProjectileWeapon}
                        logic_id = filename[:-3]  # 以前缀文件名作为 ID
                        cls._logic_classes[logic_id] = attr
        print(f"🛠️ 武器工厂已自动识别逻辑: {list(cls._logic_classes.keys())}")

    @classmethod
    def create_weapon(cls, weapon_id, player, groups):
        config = registry.weapons.get(weapon_id)
        if not config: return None

        logic_id = config.get("logic_type")
        logic_class = cls._logic_classes.get(logic_id)

        if logic_class:
            # 协议标准化：所有的武器构造函数必须一致
            return logic_class(player, groups, config)
        return None