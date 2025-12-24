import importlib
import os
from core.registry import registry


class WeaponFactory:
    @classmethod
    def auto_discover_logic(cls):
        """扫描 weapons 文件夹并动态加载模块以触发装饰器"""
        path = "combat/weapons"
        if not os.path.exists(path): return

        for filename in os.listdir(path):
            if filename.endswith(".py") and filename not in ["__init__.py", "base_weapon.py"]:
                module_name = f"combat.weapons.{filename[:-3]}"
                # 动态加载会执行模块代码，从而触发 @registry.register_logic
                importlib.import_module(module_name)

        print(f"🛠️ 武器工厂：逻辑自动发现完成 -> {list(registry.weapon_logic.keys())}")

    @classmethod
    def create_weapon(cls, weapon_id, player, groups):
        config = registry.weapons.get(weapon_id)
        if not config:
            print(f"⚠️ 找不到武器配置: {weapon_id}");
            return None

        logic_id = config.get("logic_type")
        logic_class = registry.weapon_logic.get(logic_id)

        if logic_class:
            return logic_class(player, groups, config)

        print(f"❌ 找不到逻辑实现: {logic_id}")
        return None