# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
任务队列管理器 —— 谐振调谐论：根据场域状态动态调整任务优先级。
"""
import time
import uuid
from typing import Dict, Any, List, Optional
from collections import deque


class TaskQueue:
    def __init__(self, max_size: int = 1000):
        self.pending: deque = deque(maxlen=max_size)
        self.processing: Dict[str, Dict[str, Any]] = {}
        self.completed: Dict[str, Dict[str, Any]] = {}
        self.failed: Dict[str, Dict[str, Any]] = {}

    def add_task(self, task: Dict[str, Any], priority: int = 5) -> str:
        task_id = f"task_{int(time.time())}_{len(self.pending)}_{uuid.uuid4().hex[:6]}"
        task_entry = {
            "task_id": task_id,
            "task": task,
            "priority": priority,
            "status": "pending",
            "created_at": time.time(),
            "assigned_agent": None
        }
        self.pending.append(task_entry)
        return task_id

    def get_next(self) -> Optional[Dict[str, Any]]:
        if not self.pending:
            return None
        sorted_tasks = sorted(self.pending, key=lambda x: x["priority"], reverse=True)
        task = sorted_tasks[0]
        self.pending.remove(task)
        task["status"] = "processing"
        task["started_at"] = time.time()
        self.processing[task["task_id"]] = task
        return task

    def complete_task(self, task_id: str, result: Dict[str, Any]):
        if task_id in self.processing:
            task = self.processing.pop(task_id)
            task["status"] = "completed"
            task["completed_at"] = time.time()
            task["result"] = result
            self.completed[task_id] = task

    def fail_task(self, task_id: str, error: str):
        if task_id in self.processing:
            task = self.processing.pop(task_id)
            task["status"] = "failed"
            task["failed_at"] = time.time()
            task["error"] = error
            self.failed[task_id] = task

    def get_stats(self) -> Dict[str, int]:
        return {
            "pending": len(self.pending),
            "processing": len(self.processing),
            "completed": len(self.completed),
            "failed": len(self.failed)
        }

    def adjust_priorities_by_field(self, field_state: Dict[str, float]):
        H = field_state.get("H", 0.5)
        A = field_state.get("A", 0.0)

        for task in self.pending:
            task_type = task["task"].get("task_type", "")
            if A > 0.5 and task_type in ["reproduce", "cross_check", "false_positive_detection"]:
                task["priority"] += 2
            if H < 0.3 and task_type in ["static_analysis", "dependency_analysis"]:
                task["priority"] += 1