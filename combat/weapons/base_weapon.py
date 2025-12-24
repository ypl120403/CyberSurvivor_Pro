import pygame

class BaseWeapon:
    """所有武器必须遵守的协议"""
    def __init__(self, player, groups, config):
        self.player = player
        self.groups = groups
        self.config = config
        self.id = config['id']
        self.level = 1
        self.max_level = config.get('max_level', 5)
        self.last_shot = 0
        self.init_stats()

    def init_stats(self):
        """从 JSON 读取当前等级数据"""
        lvl_data = self.config['levels'].get(str(self.level), {})
        self.damage = lvl_data.get('damage', 10)
        self.cooldown = lvl_data.get('cooldown', 500)
        self.bullet_count = lvl_data.get('count', 1)

    def level_up(self):
        if self.level < self.max_level:
            self.level += 1
            self.init_stats()
            print(f"⭐ {self.config['name']} 升级 -> LV.{self.level}")

    def update(self, dt, enemies):
        pass # 由子类实现具体行为