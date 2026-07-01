# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
智能体基类 —— 关系本体论：每个智能体的能力不由其内部代码决定，
而由它在协同网络中的位置、与其他智能体的通信模式决定。
"""
import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import websockets
from core.message_types import Message, MessageType
from config import settings


class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.ws = None
        self.running = False

        self.local_field = {"U": 0.5, "D": 0.5, "A": 0.0, "H": 0.5}

        self.task_history: List[Dict[str, Any]] = []

        self.audit_entries: List[Dict[str, Any]] = []

    def _audit(self, action: str, details: Dict[str, Any]):
        entry = {
            "timestamp": time.time(),
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "action": action,
            "details": details
        }
        self.audit_entries.append(entry)

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