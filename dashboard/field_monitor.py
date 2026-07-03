# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
场域监控器 —— 实践介入论：持续采集智能体团队的场域状态，生成趋势报告。
"""
import time
import json
from typing import Dict, List, Optional
from collections import deque
from config import settings


class FieldMonitor:
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.snapshots: deque = deque(maxlen=max_history)
        self.alerts: List[Dict] = []
        self.start_time = time.time()

    def record_snapshot(self, field_state: Dict[str, float],
                        agent_count: int, task_count: int,
                        phase_alerts: Optional[Dict] = None):
        snapshot = {
            "timestamp": time.time(),
            "field": field_state,
            "agent_count": agent_count,
            "task_count": task_count,
            "alerts": phase_alerts.get("alerts", []) if phase_alerts else []
        }
        self.snapshots.append(snapshot)

        if phase_alerts:
            self.alerts.append({
                "timestamp": time.time(),
                "alerts": phase_alerts.get("alerts", []),
                "field": field_state
            })

    def get_current_state(self) -> Dict:
        if not self.snapshots:
            return {
                "U": 0.5, "D": 0.5, "A": 0.0, "H": 0.5,
                "agent_count": 0, "task_count": 0,
                "uptime": time.time() - self.start_time
            }

        latest = self.snapshots[-1]
        return {
            "U": latest["field"]["U"],
            "D": latest["field"]["D"],
            "A": latest["field"]["A"],
            "H": latest["field"]["H"],
            "agent_count": latest["agent_count"],
            "task_count": latest["task_count"],
            "uptime": time.time() - self.start_time
        }

    def get_history(self, limit: int = 100) -> List[Dict]:
        return list(self.snapshots)[-limit:]

    def get_alerts(self, limit: int = 50) -> List[Dict]:
        return self.alerts[-limit:]

    def get_trend(self, window: int = 20) -> Dict[str, str]:
        if len(self.snapshots) < window:
            return {"U": "unknown", "D": "unknown", "A": "unknown", "H": "unknown"}

        recent = list(self.snapshots)[-window:]
        current = recent[-1]["field"]
        past = recent[0]["field"]

        def trend_str(curr, past):
            diff = curr - past
            if diff > 0.05:
                return "rising"
            elif diff < -0.05:
                return "falling"
            else:
                return "stable"

        return {
            "U": trend_str(current["U"], past["U"]),
            "D": trend_str(current["D"], past["D"]),
            "A": trend_str(current["A"], past["A"]),
            "H": trend_str(current["H"], past["H"])
        }


monitor = FieldMonitor()