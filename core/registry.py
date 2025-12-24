import os
import json


class Registry:
    def __init__(self):
        self.weapons = {}
        self.enemies = {}
        self.upgrades = []

    def load(self):
        # 1. 加载武器和敌人 (文件夹扫描模式)
        categories = {'weapons': 'data/configs/weapons', 'enemies': 'data/configs/enemies'}
        for key, path in categories.items():
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                continue
            for f in os.listdir(path):
                if f.endswith(".json"):
                    with open(os.path.join(path, f), 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        getattr(self, key)[data['id']] = data

        # 2. 加载升级项 (单文件模式)
        upgrade_file = "data/configs/upgrades.json"
        if os.path.exists(upgrade_file):
            with open(upgrade_file, 'r', encoding='utf-8') as file:
                self.upgrades = json.load(file)

        print(f"📦 Registry: 已加载武器{len(self.weapons)} 敌人{len(self.enemies)} 升级项{len(self.upgrades)}")


# --- 关键：必须有这一行，外部才能 from core.registry import registry ---
registry = Registry()