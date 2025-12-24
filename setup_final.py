import os


def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ 成功创建: {path}")


# --- 1. constants.py ---
CONSTANTS_PY = """
import pygame
WIDTH, HEIGHT = 1280, 720
FPS = 60
TILE_SIZE = 64
LAYER_BG, LAYER_PICKUP, LAYER_ENEMY, LAYER_PLAYER, LAYER_PROJECTILE, LAYER_UI = 0, 10, 20, 30, 40, 100
COLOR_BG = (12, 12, 20)
COLOR_GRID = (35, 35, 55)
COLOR_PLAYER = (0, 255, 240)
COLOR_ENEMY = (255, 50, 80)
"""

# --- 2. base_entity.py ---
BASE_ENTITY_PY = """
import pygame
from core.constants import *

class BaseEntity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, layer=LAYER_BG):
        super().__init__(groups)
        self.z_index = layer
        self.pos = pygame.math.Vector2(pos)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        pass
"""

# --- 3. camera.py ---
CAMERA_PY = """
import pygame
from core.constants import *

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # 丝滑跟随 (Lerp)
        self.offset.x += (player.rect.centerx - WIDTH // 2 - self.offset.x) * 0.1
        self.offset.y += (player.rect.centery - HEIGHT // 2 - self.offset.y) * 0.1

        self.display_surface.fill(COLOR_BG)

        # 排序绘制
        for sprite in sorted(self.sprites(), key=lambda s: (getattr(s, 'z_index', 0), s.rect.centery)):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
"""

# --- 4. registry.py ---
REGISTRY_PY = """
import os, json
class Registry:
    def __init__(self):
        self.weapons = {}
        self.enemies = {}
    def load(self):
        paths = {'weapons': 'data/configs/weapons', 'enemies': 'data/configs/enemies'}
        for key, path in paths.items():
            if not os.path.exists(path): os.makedirs(path); continue
            for f in os.listdir(path):
                if f.endswith(".json"):
                    with open(os.path.join(path, f), 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        self.__dict__[key][data['id']] = data
        print(f"📦 注册中心已加载武器: {list(self.weapons.keys())}")
registry = Registry()
"""

# --- 5. engine.py ---
ENGINE_PY = """
import pygame
from core.constants import *
from core.registry import registry
from core.camera import CameraGroup
from entities.player import Player

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        registry.load()
        self.all_sprites = CameraGroup()
        self.player = Player((WIDTH//2, HEIGHT//2), [self.all_sprites])

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False

            self.all_sprites.update(dt)
            self.all_sprites.custom_draw(self.player)
            pygame.display.flip()
"""

# --- 6. player.py ---
PLAYER_PY = """
import pygame
from entities.base_entity import BaseEntity
from core.constants import *

class Player(BaseEntity):
    def __init__(self, pos, groups):
        super().__init__(pos, groups, LAYER_PLAYER)
        pygame.draw.circle(self.image, COLOR_PLAYER, (TILE_SIZE//2, TILE_SIZE//2), 20)
        self.speed = 400

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
            (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        )
        if direction.length() > 0:
            direction = direction.normalize()
        self.pos += direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
"""

# --- 7. main.py ---
MAIN_PY = """
from core.engine import GameEngine

if __name__ == '__main__':
    game = GameEngine()
    game.run()
"""

# --- 执行 ---
if __name__ == "__main__":
    create_file("core/constants.py", CONSTANTS_PY)
    create_file("core/camera.py", CAMERA_PY)
    create_file("core/registry.py", REGISTRY_PY)
    create_file("core/engine.py", ENGINE_PY)
    create_file("entities/base_entity.py", BASE_ENTITY_PY)
    create_file("entities/player.py", PLAYER_PY)
    create_file("main.py", MAIN_PY)

    # 创建必要的空目录
    for d in ["data/configs/weapons", "data/configs/enemies", "entities/components", "combat/weapons"]:
        os.makedirs(d, exist_ok=True)

    # 创建一个空的 stats.py 防止导入错误
    create_file("entities/components/stats.py", "class StatsComponent:\\n    def __init__(self, config): pass")
    # 创建一个空的 event_bus.py
    create_file("core/event_bus.py", "class EventBus:\\n    def __init__(self): pass\\nbus = EventBus()")

    print("\n🚀 [CyberSurvivor_Pro] 初始化成功！请运行 main.py 测试。")