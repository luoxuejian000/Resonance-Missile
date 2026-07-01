# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
场域感知器 —— 关系本体论：将智能体团队的协同状态量化为U/D/A/H指标。
"""
import numpy as np
from typing import List, Dict, Any
from config import settings


class FieldPerceiver:
    def __init__(self, lambda_u=None, lambda_d=None, lambda_a=None):
        self.lambda_u = lambda_u or settings.lambda_u
        self.lambda_d = lambda_d or settings.lambda_d
        self.lambda_a = lambda_a or settings.lambda_a

    def perceive(self, agent_states: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        if not agent_states:
            return {"U": 0.5, "D": 0.5, "A": 0.0, "H": 0.5}

        u_vals = [s.get("u", 0.5) for s in agent_states.values()]
        U = np.mean(u_vals) * (1 - np.std(u_vals))

        d_vals = [s.get("d", 0.5) for s in agent_states.values()]
        D = np.mean(d_vals)

        a_vals = [s.get("a", 0.0) for s in agent_states.values()]
        A = np.max(a_vals)

        H = self.lambda_u * U + self.lambda_d * D - self.lambda_a * A
        H = max(0.0, min(1.0, H))

        return {"U": round(U, 3), "D": round(D, 3), "A": round(A, 3), "H": round(H, 3)}