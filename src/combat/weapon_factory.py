import importlib
import os
from src.core.registry import registry


class WeaponFactory:
    @classmethod
    def auto_discover_logic(cls):
        """一劳永逸：扫描 src/combat/weapon_logic 文件夹并自动注册"""
        # 搬家后的新路径
        path = "src/combat/weapon_logic"
        if not os.path.exists(path): return

        for filename in os.listdir(path):
            if filename.endswith(".py") and filename not in ["__init__.py", "base_weapon.py"]:
                # 对应 src 内部的模块路径
                module_name = f"src.combat.weapon_logic.{filename[:-3]}"
                try:
                    importlib.import_module(module_name)
                except Exception as e:
                    print(f"❌ 加载武器逻辑失败 [{module_name}]: {e}")

        print(f"🛠️ 武器工厂：逻辑库同步完成 -> {list(registry.weapon_logic.keys())}")

    @classmethod
    def create_weapon_by_data(cls, config, player, groups):
        """核心规则：根据传入的字典数据直接制造武器，无需预存 Registry"""
        logic_id = config.get("logic_type")
        logic_class = registry.weapon_logic.get(logic_id)

        if logic_class:
            return logic_class(player, groups, config)

        print(f"❌ 找不到逻辑模版: {logic_id}")
        return None

    @classmethod
    def create_weapon(cls, weapon_id, player, groups):
        """辅助方法：传统的根据 ID 从注册中心制造"""
        config = registry.weapons.get(weapon_id)
        if not config:
            print(f"⚠️ 找不到武器配置: {weapon_id}")
            return None
        return cls.create_weapon_by_data(config, player, groups)