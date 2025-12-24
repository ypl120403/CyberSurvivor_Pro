import os
import json


class Registry:
    def __init__(self):
        self.weapons = {}
        self.enemies = {}
        self.upgrades = []  # 这里改为列表

    def load(self):
        # 1. 加载武器和敌人 (文件夹模式)
        for cat in ['weapons', 'enemies']:
            path = f"data/configs/{cat}"
            if os.path.exists(path):
                for f in os.listdir(path):
                    if f.endswith(".json"):
                        with open(os.path.join(path, f), 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            getattr(self, cat)[data['id']] = data

        # 2. 加载升级项 (单文件模式)
        upgrade_file = "data/configs/upgrades.json"
        if os.path.exists(upgrade_file):
            with open(upgrade_file, 'r', encoding='utf-8') as file:
                self.upgrades = json.load(file)

        print(f"📦 Registry: 武器{len(self.weapons)} 敌人{len(self.enemies)} 升级项{len(self.upgrades)}")

    # 在 Registry 类中增加一个安全获取方法
    def get_config(self, category, item_id):
        data = getattr(self, category, {}).get(item_id)
        if not data:
            print(f"❌ [Registry] 找不到致命数据: {category}/{item_id}. 使用默认值。")
            return {"name": "未知项目", "damage": 0}  # 返回空对象防止崩溃
        return data



