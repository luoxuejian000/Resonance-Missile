# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
翻转点检测器 —— 矛盾动力论：检测场域相变的前兆信号。
"""
import numpy as np
from typing import List, Dict, Optional, Any
from config import settings


class PhaseDetector:
    def __init__(self):
        self.history: List[Dict[str, float]] = []

    def update(self, field_state: Dict[str, float]) -> Optional[Dict[str, Any]]:
        self.history.append(field_state)
        if len(self.history) < 5:
            return None

        alerts = []
        current = self.history[-1]

        recent_a = [s["A"] for s in self.history[-settings.sigma_d_window:]]
        if len(recent_a) >= 3:
            sigma_a = np.std(recent_a)
            if sigma_a <= settings.a_inert_threshold:
                if current["A"] <= settings.a_boundary_low or current["A"] >= settings.a_boundary_high:
                    recent_u = [s["U"] for s in self.history[-5:]]
                    if len(recent_u) >= 2 and recent_u[-1] < recent_u[0] - 0.05:
                        alerts.append({
                            "type": "PRIMARY",
                            "message": f"A值僵死（σ={sigma_a:.3f}），U值持续下降，场域可能正在失谐。"
                        })

        if len(self.history) >= settings.u_peak_lookback + 1:
            recent_u_vals = [s["U"] for s in self.history[-(settings.u_peak_lookback+1):]]
            peak_u = max(recent_u_vals[:-1])
            current_u = recent_u_vals[-1]
            if current_u - peak_u <= settings.u_delta_reversal and current["H"] < 0.4:
                alerts.append({
                    "type": "U_PEAK_REVERSAL",
                    "message": f"U值从{peak_u:.3f}骤降至{current_u:.3f}，统一性在场强度正在衰减。"
                })

        if alerts:
            return {"alerts": alerts, "field_state": current}
        return None