# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
ThinkCheck适配器 —— 调用老实验台的U/D/A/H分析能力。
防范工具理性悖论：适配器只读取分析结果，不修改原系统。
"""
import sys
import os
import json
import subprocess
from typing import Dict, Any, Optional


class ThinkCheckAdapter:
    def __init__(self, thinkcheck_path: str = None):
        if thinkcheck_path:
            self.thinkcheck_path = thinkcheck_path
        else:
            self.thinkcheck_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "thinkcheck-agent-v6"
            )
        self.trajectory_script = os.path.join(self.thinkcheck_path, "run_self_contained.py")

    def analyze_text(self, text: str, output_prefix: str = "thinkcheck_result") -> Optional[Dict[str, Any]]:
        temp_file = f"{output_prefix}_input.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(text)

        try:
            result = subprocess.run(
                [sys.executable, self.trajectory_script, temp_file],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.thinkcheck_path
            )

            report_file = f"{output_prefix}_pure_multidim.json"
            if os.path.exists(report_file):
                with open(report_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, list) and len(data) > 0:
                    last = data[-1]
                    return {
                        "U": last.get("U", 0.5),
                        "D": last.get("D", 0.5),
                        "A": last.get("A", 0.0),
                        "H": last.get("H", 0.5),
                        "trajectory": data,
                        "sample_count": len(data)
                    }
        except subprocess.TimeoutExpired:
            print(f"[ThinkCheckAdapter] 分析超时")
        except Exception as e:
            print(f"[ThinkCheckAdapter] 分析异常: {e}")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        return None

    def get_field_health(self, text: str) -> Dict[str, Any]:
        result = self.analyze_text(text)
        if result is None:
            return {"U": 0.5, "D": 0.5, "A": 0.0, "H": 0.5, "status": "unknown"}

        H = result["H"]
        if H > 0.5:
            status = "healthy"
        elif H > 0.3:
            status = "warning"
        else:
            status = "danger"

        return {
            "U": result["U"],
            "D": result["D"],
            "A": result["A"],
            "H": H,
            "status": status,
            "sample_count": result.get("sample_count", 0)
        }