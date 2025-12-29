import os

# 定义需要备份的核心文件夹（增加了 assets）
CORE_DIRS = ['core', 'systems', 'ui', 'combat', 'entities', 'data', 'assets']
OUTPUT_FILE = "project_snapshot.txt"


def dump_project():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("项目：CyberSurvivor_Pro 全量代码快照\n")
        out.write("技术栈：Python 3.14 + pygame-ce 2.5.6\n")
        out.write("资产目录说明：assets 文件夹用于存放后续的贴图(textures)、音效(sfx)和字体(fonts)\n\n")

        for folder in CORE_DIRS:
            for root, dirs, files in os.walk(folder):
                # 排除 pycache
                if '__pycache__' in root:
                    continue

                for file in files:
                    # 记录代码、配置以及资产文件的路径
                    if file.endswith(('.py', '.json', '.txt')):
                        path = os.path.join(root, file)
                        out.write(f"\n{'=' * 30}\nFILE: {path}\n{'=' * 30}\n")
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                out.write(f.read())
                        except:
                            out.write("[读取失败或非文本文件]")
                    elif file.endswith(('.png', '.wav', '.ogg', '.ttf')):
                        # 对于图片和音频，只记录路径证明其存在
                        path = os.path.join(root, file)
                        out.write(f"\n[ASSET DETECTED]: {path}\n")

        # 记录根目录文件
        for file in os.listdir("."):
            if file.endswith(".py") and file != "dump_for_new_chat.py":
                out.write(f"\n{'=' * 30}\nFILE: {file}\n{'=' * 30}\n")
                with open(file, "r", encoding="utf-8") as f:
                    out.write(f.read())


if __name__ == "__main__":
    dump_project()
    print(f"快照已生成：{OUTPUT_FILE}。请打开并全选内容，准备粘贴到新对话中。")