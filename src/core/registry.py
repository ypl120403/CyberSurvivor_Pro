# core/registry.py
import os
import json
import pygame


class Registry:
    def __init__(self):
        # 1. 结构化存储：分类存放所有 JSON 配置
        self.weapons = {}
        self.enemies = {}
        self.characters = {}
        self.waves = {}  # 预留给未来的波次系统
        self.upgrades = []

        # 2. 逻辑映射：存放 Python 类逻辑 (由装饰器注入)
        self.weapon_logic = {}

        # 3. 资产库：存放加载好的 Surface 对象
        self.textures = {}

    def register_logic(self, logic_id):
        """规则：使用装饰器将 Python 类关联到 JSON 配置的 logic_type"""

        def wrapper(cls):
            self.weapon_logic[logic_id] = cls
            return cls

        return wrapper

    def load_all(self):
        """规则：一键启动所有规则化加载"""
        self._load_configs()
        self._load_assets()
        print(f"🚀 Registry 全量同步完成")

    def _load_configs(self):
        """规则：配置驱动。只需增加字典项即可支持新类型 JSON"""
        config_map = {
            'weapons': 'data/configs/weapons',
            'enemies': 'data/configs/enemies',
            'characters': 'data/configs/characters',
            'waves': 'data/configs/waves'
        }

        for attr, path in config_map.items():
            if not os.path.exists(path):
                continue

            for f in os.listdir(path):
                if f.endswith(".json"):
                    try:
                        with open(os.path.join(path, f), 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            # 规则：所有配置文件必须包含 'id' 字段作为 Key
                            if 'id' in data:
                                getattr(self, attr)[data['id']] = data
                    except Exception as e:
                        print(f"❌ 配置文件解析失败 [{f}]: {e}")

        # 独立处理特殊的数组型配置
        upgrade_file = "data/configs/upgrades.json"
        if os.path.exists(upgrade_file):
            with open(upgrade_file, 'r', encoding='utf-8') as f:
                self.upgrades = json.load(f)

    def _load_assets(self):
        """规则：资产自动发现。扫描 assets/textures 下所有图片，自动生成层级 ID"""
        base_path = "assets/textures"
        if not os.path.exists(base_path):
            os.makedirs(base_path, exist_ok=True)
            return

        for root, _, files in os.walk(base_path):
            for f in files:
                if f.lower().endswith(('.png', '.jpg', '.webp')):
                    full_path = os.path.join(root, f)

                    # 规则：将相对路径转换为 ID。
                    # 例如: assets/textures/ui/icons/hp.png -> ID: 'ui/icons/hp'
                    rel_path = os.path.relpath(full_path, base_path)
                    asset_id = os.path.splitext(rel_path)[0].replace("\\", "/")

                    try:
                        # 自动处理透明度并优化渲染效率
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.textures[asset_id] = surf
                    except Exception as e:
                        print(f"❌ 资产加载失败 [{asset_id}]: {e}")

    def get_texture(self, asset_id, fallback_color=(255, 0, 255)):
        """规则：安全的资产获取。如果贴图缺失，自动生成一个紫色方块补丁"""
        if asset_id in self.textures:
            return self.textures[asset_id]

        # 工业级补救：动态生成错误提示图
        print(f"⚠️ 资产缺失: {asset_id}，已生成占位符")
        error_surf = pygame.Surface((32, 32))
        error_surf.fill(fallback_color)
        self.textures[asset_id] = error_surf
        return error_surf


# 创建全局单例
registry = Registry()