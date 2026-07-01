# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
人类审批接口 —— 防范工具理性悖论：所有高危操作必须经人类审批。
"""
import time
from typing import Dict, Any, List, Optional
from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class HumanApproval:
    def __init__(self, timeout_seconds: int = 3600):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approval_history: List[Dict[str, Any]] = []
        self.timeout = timeout_seconds

    def request_approval(self, operation: Dict[str, Any], reason: str, risk_level: str) -> str:
        approval_id = f"approval_{int(time.time())}_{len(self.pending_approvals)}"
        entry = {
            "approval_id": approval_id,
            "operation": operation,
            "reason": reason,
            "risk_level": risk_level,
            "status": ApprovalStatus.PENDING,
            "created_at": time.time(),
            "responded_at": None,
            "operator": None
        }
        self.pending_approvals[approval_id] = entry
        return approval_id

    def approve(self, approval_id: str, operator: str = "human") -> bool:
        if approval_id in self.pending_approvals:
            entry = self.pending_approvals.pop(approval_id)
            entry["status"] = ApprovalStatus.APPROVED
            entry["responded_at"] = time.time()
            entry["operator"] = operator
            self.approval_history.append(entry)
            return True
        return False

    def reject(self, approval_id: str, operator: str = "human", reason: str = "") -> bool:
        if approval_id in self.pending_approvals:
            entry = self.pending_approvals.pop(approval_id)
            entry["status"] = ApprovalStatus.REJECTED
            entry["responded_at"] = time.time()
            entry["operator"] = operator
            entry["rejection_reason"] = reason
            self.approval_history.append(entry)
            return True
        return False

    def check_expired(self):
        now = time.time()
        expired_ids = []
        for aid, entry in self.pending_approvals.items():
            if now - entry["created_at"] > self.timeout:
                expired_ids.append(aid)
        for aid in expired_ids:
            entry = self.pending_approvals.pop(aid)
            entry["status"] = ApprovalStatus.EXPIRED
            self.approval_history.append(entry)

    def get_pending(self) -> List[Dict[str, Any]]:
        self.check_expired()
        return list(self.pending_approvals.values())

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.approval_history[-limit:]