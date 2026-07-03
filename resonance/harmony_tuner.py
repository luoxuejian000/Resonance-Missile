# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
HarmonyTuner — 谐振调谐引擎
晶脉哲学映射：
  - 谐振调谐论：生成建议但不执行，人类保持最终决策权
  - 悖论防护：建议冷却期防止过度活跃
"""
import time
import numpy as np
from typing import Dict, Any, List, Optional
from config import settings


class HarmonyTuner:
    def __init__(self):
        self.temperature = settings.initial_temperature
        self.tuning_history: list = []
        self.sandbox_mode: bool = False
        self.sandbox_results: list = []
        self.applied_actions: list = []
        self.pending_suggestions = []
        self._suggestion_frequency = {}
        self._cooldown_seconds = 3600
        self._last_suggestion_time = {}

    def _check_cooldown(self, action_type: str) -> bool:
        if action_type not in self._suggestion_frequency:
            return False
        timestamps = self._suggestion_frequency[action_type]
        now = time.time()
        recent = [t for t in timestamps if now - t < self._cooldown_seconds]
        if len(recent) >= 3:
            return True
        return False

    def _record_suggestion(self, action_type: str) -> None:
        self._suggestion_frequency.setdefault(action_type, []).append(time.time())

    def generate_tuning_suggestions(self, field_state: Dict[str, float]) -> List[Dict]:
        H = field_state.get("H", 0.5)
        A = field_state.get("A", 0.0)
        U = field_state.get("U", 0.5)

        suggestions = []

        if H < 0.3:
            if not self._check_cooldown("low_h"):
                suggestions.append({
                    "action": "increase_verify_weight",
                    "suggested_value": 1.5,
                    "reason": f"H={H:.2f} 过低，建议提升验证Agent权重",
                    "requires_human_approval": True,
                    "cooldown_applied": False
                })
                suggestions.append({
                    "action": "increase_temperature",
                    "current_value": self.temperature,
                    "suggested_value": min(2.0, self.temperature + 0.1),
                    "reason": f"H={H:.2f} 过低，建议提高探索温度",
                    "requires_human_approval": True,
                    "cooldown_applied": False
                })
                self._record_suggestion("low_h")
            else:
                suggestions.append({
                    "action": "low_h_suggestion_blocked",
                    "reason": "同类建议在1小时内已提出3次且未被采纳，自动冷却",
                    "requires_human_approval": False,
                    "cooldown_applied": True
                })

        if A > 0.7:
            if not self._check_cooldown("high_a"):
                suggestions.append({
                    "action": "increase_audit_depth",
                    "suggested_value": 5,
                    "reason": f"A={A:.2f} 过高，建议增加审计深度",
                    "requires_human_approval": True,
                    "cooldown_applied": False
                })
                self._record_suggestion("high_a")
            else:
                suggestions.append({
                    "action": "high_a_suggestion_blocked",
                    "reason": "同类建议在1小时内已提出3次且未被采纳，自动冷却",
                    "requires_human_approval": False,
                    "cooldown_applied": True
                })

        if U < 0.3:
            if not self._check_cooldown("low_u"):
                suggestions.append({
                    "action": "pause_contested_tasks",
                    "reason": f"U={U:.2f} 过低，建议暂停争议任务",
                    "requires_human_approval": True,
                    "cooldown_applied": False
                })
                self._record_suggestion("low_u")
            else:
                suggestions.append({
                    "action": "low_u_suggestion_blocked",
                    "reason": "同类建议在1小时内已提出3次且未被采纳，自动冷却",
                    "requires_human_approval": False,
                    "cooldown_applied": True
                })

        if H > 0.6:
            if A < 0.3:
                if not self._check_cooldown("high_h"):
                    suggestions.append({
                        "action": "decrease_temperature",
                        "current_value": self.temperature,
                        "suggested_value": max(0.5, self.temperature - 0.05),
                        "reason": f"H={H:.2f} 健康且A={A:.2f}较低，建议降低温度",
                        "requires_human_approval": True,
                        "cooldown_applied": False
                    })
                    self._record_suggestion("high_h")
                else:
                    suggestions.append({
                        "action": "high_h_suggestion_blocked",
                        "reason": "同类建议在1小时内已提出3次且未被采纳，自动冷却",
                        "requires_human_approval": False,
                        "cooldown_applied": True
                    })
            else:
                suggestions.append({
                    "action": "high_h_with_high_a",
                    "reason": f"H={H:.2f} 但A={A:.2f}仍较高，建议维持当前温度",
                    "requires_human_approval": False
                })

        self.pending_suggestions.extend(suggestions)
        self.tuning_history.append({
            "timestamp": time.time(),
            "field_state": field_state.copy(),
            "suggestions_count": len(suggestions)
        })
        return suggestions

    def apply_approved_suggestion(self, suggestion: Dict) -> bool:
        if suggestion.get("requires_human_approval", True):
            raise RuntimeError("SECURITY_VIOLATION: Unauthorized tuning operation blocked")

        action = suggestion.get("action", "")
        if action in ("increase_temperature", "decrease_temperature"):
            self.temperature = suggestion.get("suggested_value", self.temperature)
        elif action == "increase_verify_weight":
            pass
        elif action == "pause_contested_tasks":
            pass

        self.pending_suggestions = [s for s in self.pending_suggestions if s is not suggestion]
        self.tuning_history.append({
            "timestamp": time.time(),
            "action": "approved_apply",
            "suggestion": suggestion
        })
        self.applied_actions.append({
            "suggestion": suggestion,
            "applied_at": time.time()
        })
        return True

    def get_pending_suggestions(self) -> List[Dict]:
        return self.pending_suggestions

    def tune(self, field_state: Dict[str, float], phase_alerts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        suggestions = []
        actions = []
        H = field_state.get("H", 0.5)
        A = field_state.get("A", 0.0)
        U = field_state.get("U", 0.5)

        if H < 0.3:
            if not self._check_cooldown("low_h"):
                new_temp = min(2.0, self.temperature + 0.1)
                actions.append({
                    "action": "adjust_temperature",
                    "parameter": "temperature",
                    "value": new_temp,
                    "delta": new_temp - self.temperature,
                    "reason": f"场域失谐(H={H:.2f})，增加探索力度",
                    "requires_approval": False
                })
                suggestions.append(f"场域失谐(H={H:.2f})，提高温度至{new_temp:.2f}，增加探索力度。")
                if not self.sandbox_mode:
                    self.temperature = new_temp
                self._record_suggestion("low_h")
            else:
                suggestions.append(f"场域失谐(H={H:.2f})，但同类建议已在冷却期。")
        elif H > 0.6:
            if not self._check_cooldown("high_h") or A >= 0.3:
                new_temp = max(0.5, self.temperature - 0.05)
                actions.append({
                    "action": "adjust_temperature",
                    "parameter": "temperature",
                    "value": new_temp,
                    "delta": new_temp - self.temperature,
                    "reason": f"场域健康(H={H:.2f})，聚焦利用",
                    "requires_approval": False
                })
                suggestions.append(f"场域健康(H={H:.2f})，降低温度至{new_temp:.2f}，聚焦利用。")
                if not self.sandbox_mode:
                    self.temperature = new_temp
                if A < 0.3:
                    self._record_suggestion("high_h")
            else:
                suggestions.append(f"场域健康(H={H:.2f})，但同类建议已在冷却期。")

        if A > 0.6:
            if not self._check_cooldown("high_a"):
                actions.append({
                    "action": "adjust_verify_weight",
                    "parameter": "verify_weight",
                    "value": 1.5,
                    "delta": 0.5,
                    "reason": f"对抗性过高(A={A:.2f})，增加验证力度",
                    "requires_approval": True
                })
                suggestions.append(f"对抗性过高(A={A:.2f})，建议将高矛盾任务分配给验证Agent进行独立复现。")
                self._record_suggestion("high_a")
            else:
                suggestions.append(f"对抗性过高(A={A:.2f})，但同类建议已在冷却期。")

        if U < 0.3:
            if not self._check_cooldown("low_u"):
                actions.append({
                    "action": "pause_controversial_tasks",
                    "parameter": "task_status",
                    "value": "paused",
                    "delta": 0,
                    "reason": f"统一性过低(U={U:.2f})，暂停争议任务",
                    "requires_approval": True
                })
                suggestions.append(f"统一性过低(U={U:.2f})，建议暂停争议任务，等待人类专家介入。")
                self._record_suggestion("low_u")
            else:
                suggestions.append(f"统一性过低(U={U:.2f})，但同类建议已在冷却期。")

        if A < 0.1 and U > 0.7:
            actions.append({
                "action": "increase_exploration",
                "parameter": "exploration_rate",
                "value": 0.3,
                "delta": 0.1,
                "reason": f"场域过于一致(A={A:.2f}, U={U:.2f})，需要更多多样性",
                "requires_approval": False
            })
            suggestions.append(f"场域过于一致，建议增加探索性任务，引入更多多样性。")

        record = {
            "field_state": field_state,
            "suggestions": suggestions,
            "actions": actions,
            "temperature": self.temperature,
            "sandbox_mode": self.sandbox_mode
        }
        self.tuning_history.append(record)

        return record

    def apply_action(self, action: Dict[str, Any]) -> bool:
        if action.get("requires_approval", False):
            return False

        if action["action"] == "adjust_temperature":
            self.temperature = action["value"]
        elif action["action"] == "adjust_verify_weight":
            pass
        elif action["action"] == "pause_controversial_tasks":
            pass
        elif action["action"] == "increase_exploration":
            pass

        self.applied_actions.append({
            "action": action,
            "applied_at": time.time()
        })
        return True

    def enable_sandbox_mode(self):
        self.sandbox_mode = True

    def disable_sandbox_mode(self):
        self.sandbox_mode = False

    def record_sandbox_result(self, action: Dict[str, Any], h_before: float, h_after: float):
        self.sandbox_results.append({
            "action": action,
            "h_before": h_before,
            "h_after": h_after,
            "h_delta": h_after - h_before,
            "timestamp": time.time()
        })