# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
消息类型定义 —— 实践介入论：所有操作都通过结构化消息传递，留下审计痕迹。
"""
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import time
import uuid


class MessageType(str, Enum):
    ASK = "ask"
    CONFIRM = "confirm"
    GEN = "gen"
    EXEC = "exec"
    APPROVE = "approve"
    REJECT = "reject"
    NOTIFY = "notify"
    REGISTER = "register"


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType
    source: str
    target: str
    payload: Dict[str, Any] = {}
    timestamp: float = Field(default_factory=time.time)
    requires_approval: bool = False
    approved: Optional[bool] = None