import os
import json

class Registry:
    def __init__(self):
        self.weapons = {}        # 存放 JSON 配置数据
        self.weapon_logic = {}   # 存放 Python 类逻辑 (ID -> Class)
        self.enemies = {}
        self.upgrades = []

    def register_logic(self, logic_id):
        """工业级装饰器：在武器类定义处直接注册"""
        def wrapper(cls):
            self.weapon_logic[logic_id] = cls
            return cls
        return wrapper

    def load(self):
        # 1. 加载武器和敌人 JSON
        for cat in ['weapons', 'enemies']:
            path = f"data/configs/{cat}"
            if os.path.exists(path):
                for f in os.listdir(path):
                    if f.endswith(".json"):
                        with open(os.path.join(path, f), 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            getattr(self, cat)[data['id']] = data

        # 2. 加载升级项
        upgrade_file = "data/configs/upgrades.json"
        if os.path.exists(upgrade_file):
            with open(upgrade_file, 'r', encoding='utf-8') as file:
                self.upgrades = json.load(file)

        print(f"📦 Registry: 数据加载完成 | 逻辑库规模: {len(self.weapon_logic)}")

registry = Registry()