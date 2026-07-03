# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
审计日志模块 —— 实践介入论：每一次介入都必须透明可追溯。
"""
import json
import time
import os
from typing import Any, Dict
from config import settings


class AuditLogger:
    def __init__(self, log_path: str = None):
        self.log_path = log_path or settings.audit_log_path

    def log(self, event_type: str, source: str, details: Dict[str, Any]):
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "source": source,
            "details": details
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def read_logs(self, limit: int = 100) -> list:
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [json.loads(line) for line in lines[-limit:]]


audit = AuditLogger()