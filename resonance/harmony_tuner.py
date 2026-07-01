# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
谐振调谐引擎 —— 谐振调谐论：根据场域状态动态调整协同参数。
"""
import numpy as np
from typing import Dict, Any, Optional
from config import settings


class HarmonyTuner:
    def __init__(self):
        self.temperature = settings.initial_temperature
        self.tuning_history: list = []

    def tune(self, field_state: Dict[str, float], phase_alerts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        suggestions = []
        H = field_state.get("H", 0.5)
        A = field_state.get("A", 0.0)
        U = field_state.get("U", 0.5)

        if H < 0.3:
            self.temperature = min(2.0, self.temperature + 0.1)
            suggestions.append(f"场域失谐(H={H:.2f})，提高温度至{self.temperature:.2f}，增加探索力度。")
        elif H > 0.6:
            self.temperature = max(0.5, self.temperature - 0.05)
            suggestions.append(f"场域健康(H={H:.2f})，降低温度至{self.temperature:.2f}，聚焦利用。")

        if A > 0.6:
            suggestions.append(f"对抗性过高(A={A:.2f})，建议将高矛盾任务分配给验证Agent进行独立复现。")
        if U < 0.3:
            suggestions.append(f"统一性过低(U={U:.2f})，建议暂停争议任务，等待人类专家介入。")

        record = {
            "field_state": field_state,
            "suggestions": suggestions,
            "temperature": self.temperature
        }
        self.tuning_history.append(record)

        return record