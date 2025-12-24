import os


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ 已创建文件: {path}")


# --- 1. 全局常量 (Constitution) ---
CONSTANTS_PY = """
import pygame
WIDTH, HEIGHT = 1280, 720
FPS = 60
TILE_SIZE = 64
# 渲染层级
LAYER_BG, LAYER_PICKUP, LAYER_ENEMY, LAYER_PLAYER, LAYER_PROJECTILE, LAYER_UI = 0, 10, 20, 30, 40, 100
# 配色
COLOR_BG = (10, 10, 18)
COLOR_GRID = (35, 35, 60)
COLOR_PLAYER = (0, 255, 240)
COLOR_ENEMY = (255, 45, 85)
COLOR_TEXT = (245, 245, 245)
"""

# --- 2. 自动注册中心 (The Brain) ---
REGISTRY_PY = """
import os, json
class Registry:
    def __init__(self):
        self.weapons = {}
        self.enemies = {}
        self.characters = {}
    def load(self):
        for cat in ['weapons', 'enemies', 'characters']:
            path = f"data/configs/{cat}"
            if not os.path.exists(path): os.makedirs(path); continue
            for f in os.listdir(path):
                if f.endswith(".json"):
                    with open(os.path.join(path, f), 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        self.__dict__[cat][data['id']] = data
        print(f"📦 Registry loaded: {len(self.weapons)} Weapons")
registry = Registry()
"""

# --- 3. 事件总线 (The Nervous System) ---
EVENT_BUS_PY = """
class EventBus:
    def __init__(self):
        self.listeners = {}
    def subscribe(self, event_type, callback):
        if event_type not in self.listeners: self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    def emit(self, event_type, **kwargs):
        if event_type in self.listeners:
            for callback in self.listeners[event_type]: callback(**kwargs)
bus = EventBus()
"""

# --- 4. 万能属性组件 (The Soul) ---
STATS_PY = """
class Attribute:
    def __init__(self, base):
        self.base = base
        self.flat = 0
        self.mult = 0
    @property
    def value(self):
        return (self.base + self.flat) * (1 + self.mult)

class StatsComponent:
    def __init__(self, config):
        self.hp = Attribute(config.get('hp', 100))
        self.speed = Attribute(config.get('speed', 400))
        self.atk = Attribute(config.get('atk', 10))
        self.crit_rate = Attribute(0.05)
        self.pickup_range = Attribute(150)
        # 冗余位
        self.luck = Attribute(1.0)
        self.armor = Attribute(0)
"""

# --- 5. 样例数据 (Content) ---
WEAPON_JSON = """
{
    "id": "starter_gun",
    "name": "初始机枪",
    "atk": 12,
    "cooldown": 500,
    "pierce": 1,
    "logic": "projectile"
}
"""

# --- 6. 核心引擎 (The Heart) ---
ENGINE_PY = """
import pygame
from core.constants import *
from core.registry import registry
from core.event_bus import bus

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        registry.load() # 启动即加载所有JSON

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
            self.screen.fill(COLOR_BG)
            pygame.display.flip()
"""

# --- 执行初始化 ---
if __name__ == "__main__":
    create_file("core/constants.py", CONSTANTS_PY)
    create_file("core/registry.py", REGISTRY_PY)
    create_file("core/event_bus.py", EVENT_BUS_PY)
    create_file("entities/components/stats.py", STATS_PY)
    create_file("core/engine.py", ENGINE_PY)
    create_file("data/configs/weapons/starter_gun.json", WEAPON_JSON)
    create_file("main.py", "from core.engine import GameEngine\\nif __name__ == '__main__':\\n    GameEngine().run()")

    # 建立其他必要的空文件夹
    dirs = ["assets/textures", "assets/sfx", "entities/enemies", "combat/weapons", "ui/hud"]
    for d in dirs: os.makedirs(d, exist_ok=True); print(f"📁 已创建文件夹: {d}")

    print("\\n🚀 [CyberSurvivor_Pro] 工业化地基浇筑完成！请直接运行 main.py 测试。")