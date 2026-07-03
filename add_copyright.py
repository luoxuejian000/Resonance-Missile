import os
import hashlib
from pathlib import Path

FOUNDER = "李广好 (luoxuejian000) - Resonance-Missile 创始人"
HASH = hashlib.sha256(FOUNDER.encode()).hexdigest()[:16]

COPYRIGHT_HEADER = f"""# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: {HASH}
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。
"""

def add_copyright(root_dir: str):
    root = Path(root_dir)
    for py_file in root.rglob("*.py"):
        if py_file.name == "add_copyright.py":
            continue
        content = py_file.read_text(encoding="utf-8")
        if content.startswith("# Copyright"):
            continue
        new_content = COPYRIGHT_HEADER + "\n" + content
        py_file.write_text(new_content, encoding="utf-8")
        print(f"Added to {py_file.relative_to(root)}")

if __name__ == "__main__":
    add_copyright(".")