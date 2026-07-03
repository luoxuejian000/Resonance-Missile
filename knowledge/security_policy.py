# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
安全策略配置 —— 谐振调谐论：定义系统在不同场域状态下的行为边界。
"""
from typing import Dict, Any, List
from enum import Enum


class PolicyLevel(str, Enum):
    STRICT = "strict"
    NORMAL = "normal"
    RELAXED = "relaxed"


class SecurityPolicy:
    def __init__(self):
        self.current_level = PolicyLevel.NORMAL
        self.policy_rules = {
            PolicyLevel.STRICT: {
                "auto_approve_threshold": "none",
                "max_scan_depth": 3,
                "network_access": False,
                "file_modification": False,
                "requires_human_for": "all"
            },
            PolicyLevel.NORMAL: {
                "auto_approve_threshold": "low",
                "max_scan_depth": 5,
                "network_access": True,
                "file_modification": False,
                "requires_human_for": "high"
            },
            PolicyLevel.RELAXED: {
                "auto_approve_threshold": "medium",
                "max_scan_depth": 10,
                "network_access": True,
                "file_modification": True,
                "requires_human_for": "critical"
            }
        }

    def adjust_by_field_state(self, field_state: Dict[str, float]):
        H = field_state.get("H", 0.5)
        A = field_state.get("A", 0.0)

        suggested_level = self.current_level

        if H < 0.2 or A > 0.8:
            suggested_level = PolicyLevel.STRICT
        elif H < 0.4 or A > 0.5:
            suggested_level = PolicyLevel.NORMAL
        elif H > 0.6 and A < 0.3:
            suggested_level = PolicyLevel.RELAXED

        return {
            "current": self.current_level,
            "suggested": suggested_level,
            "changed": suggested_level != self.current_level,
            "reason": f"H={H:.2f}, A={A:.2f}"
        }

    def is_operation_allowed(self, operation_type: str, risk_level: str) -> bool:
        rules = self.policy_rules[self.current_level]

        if rules["requires_human_for"] == "all":
            return False
        if rules["requires_human_for"] == "critical" and risk_level == "critical":
            return False
        if rules["requires_human_for"] == "high" and risk_level in ["high", "critical"]:
            return False

        return True