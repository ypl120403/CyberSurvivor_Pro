import os
import shutil
import re


def migrate():
    print("🚀 正在执行【终极工业化结构】迁移...")

    # 1. 目标目录规划
    structure = [
        "src/core", "src/entities/components", "src/combat/weapon_logic",
        "src/scenes", "src/ui/screens", "assets/textures", "assets/sfx",
        "assets/fonts", "data/configs", "data/saves", "tools"
    ]
    for d in structure:
        os.makedirs(d, exist_ok=True)

    # 2. 移动映射 (源 -> 目标)
    # 注意：我们将一些逻辑进行了合并和归类
    move_rules = {
        "core": "src/core",
        "entities/components": "src/entities/components",
        "entities/enemies": "src/entities/enemies",
        "entities/pickups": "src/entities/pickups",
        "entities/player.py": "src/entities/player.py",
        "entities/base_entity.py": "src/entities/base_entity.py",
        "combat/weapons": "src/combat/weapon_logic",
        "combat": "src/combat",
        "systems": "src/scenes",
        "ui/menus": "src/ui/screens",
        "ui/ui_manager.py": "src/ui/manager.py",
        "ui/components.py": "src/ui/components.py",
        "setup_all.py": "tools/setup_all.py",
        "setup_final.py": "tools/setup_final.py",
        "setup_project.py": "tools/setup_project.py",
        "dump_for_new_chat.py": "tools/dump_tool.py"
    }

    for src, dst in move_rules.items():
        if os.path.exists(src):
            if os.path.isdir(src):
                # 如果目标文件夹已存在，先合并内容再删源
                os.makedirs(dst, exist_ok=True)
                for item in os.listdir(src):
                    s_path = os.path.join(src, item)
                    d_path = os.path.join(dst, item)
                    if os.path.exists(d_path):
                        if os.path.isdir(d_path):
                            shutil.rmtree(d_path)
                        else:
                            os.remove(d_path)
                    shutil.move(s_path, d_path)
                # 尝试删除可能已经空的源目录
                try:
                    shutil.rmtree(src)
                except:
                    pass
            else:
                if os.path.exists(dst): os.remove(dst)
                shutil.move(src, dst)
            print(f"✅ 搬迁: {src} -> {dst}")

    # 3. 自动重写代码中的 Import 路径 (修复地址)
    print("🔍 正在同步修复代码中的引用路径...")

    replacements = {
        r"from core": "from src.core",
        r"import core": "import src.core",
        r"from entities": "from src.entities",
        r"import entities": "import src.entities",
        r"from combat": "from src.combat",
        r"import combat": "import src.combat",
        r"from ui\.menus": "from src.ui.screens",
        r"from ui": "from src.ui",
        r"import ui": "import src.ui",
        r"from systems": "from src.scenes",
        r"import systems": "import src.scenes",
        # 特殊处理改名后的 UI Manager
        r"from src\.ui\.ui_manager": "from src.ui.manager",
    }

    for root, _, files in os.walk("."):
        if ".venv" in root or ".git" in root or "tools" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                new_content = content
                for pattern, subst in replacements.items():
                    new_content = re.sub(pattern, subst, new_content)

                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"🔧 引用已更新: {path}")

    # 4. 修复 main.py
    if os.path.exists("main.py"):
        with open("main.py", "r", encoding="utf-8") as f:
            m_content = f.read()
        m_content = m_content.replace("from src.core.engine", "from src.core.engine")
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(m_content)

    print("\n✨ 工业化搬家圆满完成！")
    print("--------------------------------------------------")
    print("👉 重要一步：如果你使用 PyCharm，请执行以下操作：")
    print("1. 在左侧项目栏找到 'src' 文件夹。")
    print("2. 右键点击它 -> 选择 'Mark Directory as' -> 'Sources Root'。")
    print("--------------------------------------------------")


if __name__ == "__main__":
    migrate()