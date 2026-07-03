# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
通信中枢 (Communication Hub)
=============================
基于晶脉哲学四重公理构建：
- 关系本体论：Hub是智能体间关系的物理载体
- 实践介入论：所有消息均被审计
- 谐振调谐论：Hub可监测消息流的场域健康度
"""
import asyncio
import json
from typing import Dict, Callable, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from core.message_types import Message, MessageType
from core.audit_logger import audit
from config import settings

app = FastAPI(title="Resonance-Missile Hub")

connected_clients: Dict[str, WebSocket] = {}
message_handlers: Dict[str, Callable] = {}
pending_approvals: List[Message] = []


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connected_clients[client_id] = websocket
    audit.log("CLIENT_CONNECTED", client_id, {"clients": list(connected_clients.keys())})

    try:
        while True:
            data = await websocket.receive_text()
            msg = Message(**json.loads(data))

            audit.log("MESSAGE_RECEIVED", client_id, {"msg_id": msg.id, "type": msg.type})

            if msg.type == MessageType.APPROVE or msg.type == MessageType.REJECT:
                if msg.id in [p.id for p in pending_approvals]:
                    for i, p in enumerate(pending_approvals):
                        if p.id == msg.id:
                            pending_approvals.pop(i)
                            break
                    audit.log("APPROVAL_RESPONSE", client_id, {"msg_id": msg.id, "approved": msg.approved})

            if msg.target in connected_clients:
                await connected_clients[msg.target].send_text(msg.json())
            elif msg.target == "broadcast":
                for cid, ws in connected_clients.items():
                    if cid != client_id:
                        await ws.send_text(msg.json())
            elif msg.type == MessageType.CONFIRM:
                pending_approvals.append(msg)
                for cid, ws in connected_clients.items():
                    if cid.startswith("human_"):
                        await ws.send_text(msg.json())

    except WebSocketDisconnect:
        connected_clients.pop(client_id, None)
        audit.log("CLIENT_DISCONNECTED", client_id, {"clients": list(connected_clients.keys())})


@app.get("/status")
async def get_status():
    return {
        "connected_clients": list(connected_clients.keys()),
        "pending_approvals": len(pending_approvals)
    }


@app.get("/audit")
async def get_audit(limit: int = 100):
    return audit.read_logs(limit)


def start_hub():
    uvicorn.run(app, host=settings.hub_host, port=settings.hub_port)


if __name__ == "__main__":
    start_hub()