# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
协同调度器 —— 谐振调谐论：根据场域状态动态分配任务，协调多智能体协同。
"""
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from collections import defaultdict
import websockets
from core.message_types import Message, MessageType
from resonance.field_perceiver import FieldPerceiver
from resonance.phase_detector import PhaseDetector
from resonance.harmony_tuner import HarmonyTuner
from config import settings


class Orchestrator:
    def __init__(self, orchestrator_id: str = "orchestrator", enable_tat: bool = False):
        self.orchestrator_id = orchestrator_id
        self.ws = None
        self.enable_tat = enable_tat

        self.registered_agents: Dict[str, Dict[str, Any]] = {}

        self.task_queue: List[Dict[str, Any]] = []

        self.global_field: Dict[str, float] = {"U": 0.5, "D": 0.5, "A": 0.0, "H": 0.5}

        self.perceiver = FieldPerceiver()
        self.detector = PhaseDetector()
        self.tuner = HarmonyTuner()

        self.audit_entries: List[Dict[str, Any]] = []

        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

        self.contradiction_history: List[Dict[str, Any]] = []

        self.calibration_requests: List[Dict[str, Any]] = []

    def _audit(self, action: str, details: Dict[str, Any]):
        entry = {
            "timestamp": time.time(),
            "orchestrator_id": self.orchestrator_id,
            "action": action,
            "details": details
        }
        self.audit_entries.append(entry)

    async def connect(self):
        connect_host = "localhost" if settings.hub_host == "0.0.0.0" else settings.hub_host
        hub_url = f"ws://{connect_host}:{settings.hub_port}/ws/{self.orchestrator_id}"
        self.ws = await websockets.connect(hub_url)
        self._audit("CONNECTED", {"hub_url": hub_url})

    async def listen(self):
        while True:
            try:
                data = await self.ws.recv()
                msg = Message(**json.loads(data))

                if msg.type == MessageType.REGISTER:
                    agent_id = msg.source
                    self.registered_agents[agent_id] = {
                        "type": msg.payload.get("agent_type"),
                        "capabilities": msg.payload.get("capabilities", []),
                        "registered_at": time.time()
                    }
                    self._audit("AGENT_REGISTERED", {"agent_id": agent_id, "info": self.registered_agents[agent_id]})

                elif msg.type == MessageType.NOTIFY:
                    if "result" in msg.payload:
                        self._handle_task_result(msg)

            except websockets.ConnectionClosed:
                break
            except Exception as e:
                self._audit("LISTEN_ERROR", {"error": str(e)})

    def _handle_task_result(self, msg: Message):
        agent_id = msg.source
        result = msg.payload.get("result", {})

        if result.get("needs_calibration", False):
            self.calibration_requests.append({
                "agent_id": agent_id,
                "false_positive_rate": result.get("false_positive_rate", 0),
                "timestamp": time.time()
            })
            self._audit("CALIBRATION_REQUESTED", {"agent_id": agent_id})

        local_field = result.get("field", {})
        if local_field:
            self.registered_agents[agent_id]["last_field"] = local_field

        if result.get("contradiction_detected", False):
            contradiction_info = {
                "agent_id": agent_id,
                "result": result,
                "timestamp": time.time(),
                "status": "detected"
            }
            self.contradiction_history.append(contradiction_info)
            self._resolve_contradictions(contradiction_info)

        agent_states = {}
        for aid, info in self.registered_agents.items():
            if "last_field" in info:
                agent_states[aid] = info["last_field"]

        if agent_states:
            self.global_field = self.perceiver.perceive(agent_states)
            self._audit("FIELD_UPDATED", {"field": self.global_field})

            phase_alert = self.detector.update(self.global_field)
            if phase_alert:
                self._audit("PHASE_ALERT", phase_alert)

                tuning = self.tuner.tune(self.global_field, phase_alert)
                self._audit("TUNING_SUGGESTION", tuning)

    def _resolve_contradictions(self, contradiction_info: Dict[str, Any]):
        agent_id = contradiction_info["agent_id"]
        result = contradiction_info["result"]

        idle_auditors = [
            aid for aid, info in self.registered_agents.items()
            if info.get("type") == "code_audit" and aid != agent_id
        ]

        if idle_auditors:
            self._audit("LEVEL_1_MEDIATION", {"agent_id": agent_id, "auditors": idle_auditors})
            findings = result.get("findings", [])
            for auditor_id in idle_auditors[:2]:
                retry_task = Message(
                    type=MessageType.GEN,
                    source=self.orchestrator_id,
                    target=auditor_id,
                    payload={
                        "task": {"task_type": "static_analysis", "code": ""},
                        "findings_to_verify": findings,
                        "mediation_level": 1
                    }
                )
                asyncio.ensure_future(self.ws.send(retry_task.json()))
        else:
            self._audit("LEVEL_2_MEDIATION", {"agent_id": agent_id, "reason": "no_auditors_available"})
            confirm_msg = Message(
                type=MessageType.CONFIRM,
                source=self.orchestrator_id,
                target="human_operator",
                payload={
                    "contradiction": contradiction_info,
                    "mediation_level": 2,
                    "evidence": {
                        "code_context": "",
                        "audit_basis": result.get("findings", []),
                        "verification_result": result
                    }
                },
                requires_approval=True
            )
            asyncio.ensure_future(self.ws.send(confirm_msg.json()))

        contradiction_info["status"] = "mediating"

    def _pre_execution_check(self, task: Dict[str, Any]) -> bool:
        if task.get("requires_approval", False):
            task_id = task.get("task_id", "")
            if task_id in self.pending_approvals:
                return self.pending_approvals[task_id].get("approved", False)
            return False
        return True

    async def submit_task(self, task: Dict[str, Any], priority: int = 5):
        task_entry = {
            "task": task,
            "priority": priority,
            "submitted_at": time.time(),
            "task_id": f"task_{int(time.time())}_{len(self.task_queue)}"
        }
        self.task_queue.append(task_entry)
        self._audit("TASK_SUBMITTED", task_entry)

        self.task_queue.sort(key=lambda x: x["priority"], reverse=True)

    async def dispatch_next_task(self):
        if not self.task_queue:
            return

        next_task = self.task_queue.pop(0)
        task = next_task["task"]
        task_type = task.get("task_type", "")

        if not self._pre_execution_check(task):
            self.task_queue.insert(0, next_task)
            self._audit("TASK_BLOCKED_PENDING_APPROVAL", {"task_id": next_task["task_id"]})
            return

        best_agent = self._find_best_agent(task_type)
        if best_agent is None:
            self.task_queue.insert(0, next_task)
            self._audit("NO_AGENT_AVAILABLE", {"task": task})
            return

        agent_info = self.registered_agents.get(best_agent, {})
        if agent_info.get("calibration_status") == "needs_calibration":
            self.task_queue.insert(0, next_task)
            self._audit("AGENT_NEEDS_CALIBRATION", {"agent_id": best_agent})
            return

        task_msg = Message(
            type=MessageType.GEN,
            source=self.orchestrator_id,
            target=best_agent,
            payload={
                "task": task,
                "task_id": next_task["task_id"],
                "field": self.global_field
            }
        )
        await self.ws.send(task_msg.json())
        self._audit("TASK_DISPATCHED", {"task_id": next_task["task_id"], "agent": best_agent})

    def _find_best_agent(self, task_type: str) -> Optional[str]:
        candidates = []
        for agent_id, info in self.registered_agents.items():
            capabilities = info.get("capabilities", [])
            if task_type in capabilities:
                last_field = info.get("last_field", {"H": 0.5})
                candidates.append((agent_id, last_field.get("H", 0.5)))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    async def run(self, dispatch_interval: float = 2.0):
        await self.connect()
        self._audit("ORCHESTRATOR_STARTED", {})

        asyncio.create_task(self.listen())

        while True:
            await self.dispatch_next_task()
            await asyncio.sleep(dispatch_interval)