# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
BaseAgent — 全局经验场基类
晶脉哲学映射：
  - 关系本体论：所有智能体共享同一片场域记忆
  - 实践介入论：所有修改强制审计留痕
  - 悖论防护：热度计算采用 hits/scans 消除幸存者偏差
"""
import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Set
from abc import ABC, abstractmethod
import websockets
from core.message_types import Message, MessageType
from config import settings


class BaseAgent(ABC):
    """全局经验场 —— 所有智能体共享的关系网络节点"""

    shared_memory: Dict[str, Any] = {
        "vulnerability_patterns": {},
        "audit_modes": {},
        "false_positive_records": {},
        "hot_patterns": [],
        "calibration_status": {},
        "core_rules": set(),
        "_core_rules_meta": {},
        "learned_patterns": {},
        "ephemeral_context": {},
        "pattern_hotness": {},
        "pattern_scanned": {},
        "misclassification": [],
        "agent_registry": {},
        "_task_history": [],
    }

    shared_memory_audit: List[Dict] = []

    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):

        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.ws = None
        self.running = False

        self.local_field = {"U": 0.5, "D": 0.5, "A": 0.0, "H": 0.5}

        self.task_history: List[Dict[str, Any]] = []

        self.audit_entries: List[Dict[str, Any]] = []

        self.false_positive_rate: float = 0.0
        self.recent_results: List[bool] = []
        self.needs_calibration: bool = False

        self.register_agent(agent_id, agent_type)

    def _audit(self, action: str, details: Dict[str, Any]):
        entry = {
            "timestamp": time.time(),
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "action": action,
            "details": details
        }
        self.audit_entries.append(entry)

    @classmethod
    def _audit_shared_memory(cls, action: str, key: str, value: Any = None) -> None:
        cls.shared_memory_audit.append({
            "timestamp": time.time(),
            "action": action,
            "key": key,
            "value_preview": str(value)[:200] if value is not None else None,
        })

    @classmethod
    def update_pattern_hotness(cls, pattern_key: str, hit: bool = True) -> None:
        scan_key = pattern_key
        cls.shared_memory["pattern_scanned"][scan_key] = \
            cls.shared_memory["pattern_scanned"].get(scan_key, 0) + 1

        if hit:
            cls.shared_memory["pattern_hotness"][pattern_key] = \
                cls.shared_memory["pattern_hotness"].get(pattern_key, 0) + 1

        cls._audit_shared_memory(
            "UPDATE_HOTNESS",
            pattern_key,
            f"hits:{cls.shared_memory['pattern_hotness'].get(pattern_key,0)}, "
            f"scans:{cls.shared_memory['pattern_scanned'].get(scan_key,0)}"
        )

    @classmethod
    def get_effective_hotness(cls, pattern_key: str) -> float:
        hits = cls.shared_memory["pattern_hotness"].get(pattern_key, 0)
        scans = cls.shared_memory["pattern_scanned"].get(pattern_key, 1)
        return hits / scans if scans > 0 else 0.0

    @classmethod
    def record_misclassification(cls, finding: Dict, agent_id: str) -> None:
        record = {
            "finding": finding,
            "timestamp": time.time(),
            "agent_id": agent_id,
            "human_confirmed": False,
        }
        cls.shared_memory["misclassification"].append(record)
        cls._audit_shared_memory("RECORD_MISCLASSIFICATION", finding.get("type"), record)

    @classmethod
    def confirm_misclassification(cls, index: int) -> None:
        if 0 <= index < len(cls.shared_memory["misclassification"]):
            cls.shared_memory["misclassification"][index]["human_confirmed"] = True
            record = cls.shared_memory["misclassification"][index]
            pattern_key = record["finding"].get("type", "unknown")
            cls.shared_memory["learned_patterns"][pattern_key] = {
                "confirmed_at": time.time(),
                "detail": record["finding"]
            }
            cls._audit_shared_memory("CONFIRM_MISCLASSIFICATION", pattern_key, "confirmed")

    @classmethod
    def register_agent(cls, agent_id: str, agent_type: str) -> None:
        cls.shared_memory["agent_registry"][agent_id] = {
            "type": agent_type,
            "status": "active",
            "registered_at": time.time()
        }
        cls._audit_shared_memory("REGISTER_AGENT", agent_id, agent_type)

    @classmethod
    def clear_ephemeral(cls) -> None:
        cls.shared_memory["ephemeral_context"].clear()
        cls._audit_shared_memory("CLEAR_EPHEMERAL", "ephemeral_context", None)

    @classmethod
    def get_field_health_report(cls) -> Dict:
        total_agents = len(cls.shared_memory["agent_registry"])
        total_tasks = len(cls.shared_memory["_task_history"])
        total_mis = len(cls.shared_memory["misclassification"])
        confirmed_mis = sum(1 for m in cls.shared_memory["misclassification"] if m.get("human_confirmed"))

        return {
            "agents_count": total_agents,
            "tasks_count": total_tasks,
            "misclassification_count": total_mis,
            "confirmed_rate": confirmed_mis / max(1, total_mis),
            "hotness_diversity": len(cls.shared_memory["pattern_hotness"]),
            "scanned_diversity": len(cls.shared_memory["pattern_scanned"]),
            "timestamp": time.time(),
            "disclaimer": "此报告仅供人类参考，不作为自动决策依据"
        }

    @abstractmethod
    async def on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def validate(self, other_agent_result: Dict[str, Any]) -> Dict[str, Any]:
        pass

    async def connect(self):
        connect_host = "localhost" if settings.hub_host == "0.0.0.0" else settings.hub_host
        hub_url = f"ws://{connect_host}:{settings.hub_port}/ws/{self.agent_id}"
        self.ws = await websockets.connect(hub_url)
        self._audit("CONNECTED", {"hub_url": hub_url})

        register_msg = Message(
            type=MessageType.REGISTER,
            source=self.agent_id,
            target="broadcast",
            payload={
                "agent_type": self.agent_type,
                "capabilities": self.capabilities
            }
        )
        await self.ws.send(register_msg.json())

    async def listen(self):
        self.running = True
        while self.running:
            try:
                data = await self.ws.recv()
                msg = Message(**json.loads(data))
                await self._handle_message(msg)
            except websockets.ConnectionClosed:
                self.running = False
                break
            except Exception as e:
                self._audit("LISTEN_ERROR", {"error": str(e)})

    async def _handle_message(self, msg: Message):
        self._audit("MESSAGE_HANDLED", {"msg_id": msg.id, "type": msg.type})

        if msg.type == MessageType.ASK:
            response = Message(
                type=MessageType.NOTIFY,
                source=self.agent_id,
                target=msg.source,
                payload={"field": self.local_field, "task_count": len(self.task_history)}
            )
            await self.ws.send(response.json())

        elif msg.type == MessageType.GEN:
            task = msg.payload.get("task", {})
            self._audit("TASK_STARTED", {"task_id": msg.id, "task": task})

            result = await self.on_task(task)
            self.task_history.append({"task": task, "result": result, "time": time.time()})
            self.local_field = self._estimate_local_field(result)

            self._audit("TASK_COMPLETED", {"task_id": msg.id, "result": result})

            if task.get("requires_approval", False):
                confirm_msg = Message(
                    type=MessageType.CONFIRM,
                    source=self.agent_id,
                    target="human_operator",
                    payload={"task": task, "result": result, "task_id": msg.id},
                    requires_approval=True
                )
                await self.ws.send(confirm_msg.json())
            else:
                response = Message(
                    type=MessageType.NOTIFY,
                    source=self.agent_id,
                    target=msg.source,
                    payload={"task_id": msg.id, "result": result, "agent_id": self.agent_id}
                )
                await self.ws.send(response.json())

        elif msg.type == MessageType.CONFIRM:
            other_result = msg.payload.get("result", {})
            validation = await self.validate(other_result)
            response = Message(
                type=MessageType.NOTIFY,
                source=self.agent_id,
                target=msg.source,
                payload={"validation": validation, "agent_id": self.agent_id}
            )
            await self.ws.send(response.json())

    def _estimate_local_field(self, task_result: Dict[str, Any]) -> Dict[str, float]:
        confidence = task_result.get("confidence", 0.5)
        is_contradiction = task_result.get("contradiction_detected", False)

        U = confidence
        D = 0.5 if task_result.get("novelty", False) else 0.2
        A = 0.7 if is_contradiction else 0.1
        H = 0.4 * U + 0.2 * D - 0.4 * A
        H = max(0.0, min(1.0, H))

        return {"U": round(U, 3), "D": round(D, 3), "A": round(A, 3), "H": round(H, 3)}

    async def run(self):
        await self.connect()
        self._audit("AGENT_STARTED", {"capabilities": self.capabilities})
        await self.listen()