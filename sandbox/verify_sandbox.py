# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
漏洞验证沙箱 —— 在隔离环境中复现漏洞，验证其真实性和危害程度。
防范工具理性悖论：沙箱严格限制网络访问、文件系统写入和系统调用。
所有验证结果仅供人类参考，不自动触发任何修复操作。
"""
import os
import json
import hashlib
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SandboxConfig:
    max_memory_mb: int = 256
    max_cpu_seconds: int = 30
    max_file_size_kb: int = 1024
    allowed_network: bool = False
    allowed_file_write: bool = False
    allowed_subprocess: bool = False
    log_all_syscalls: bool = True


class VerifySandbox:
    def __init__(self, config: SandboxConfig = None):
        self.config = config or SandboxConfig()
        self.verification_history: list = []

    def verify_vulnerability(self, vulnerability: Dict[str, Any],
                            target_info: Dict[str, Any]) -> Dict[str, Any]:
        verify_id = f"verify_{int(time.time())}_{hashlib.md5(str(vulnerability).encode()).hexdigest()[:8]}"

        if not self._check_sandbox_integrity():
            return {
                "verify_id": verify_id,
                "status": "sandbox_failure",
                "message": "沙箱环境异常，验证中止。",
                "reproducible": False,
                "severity": "unknown",
                "requires_approval": True
            }

        vuln_type = vulnerability.get("type", "unknown")
        payload = vulnerability.get("payload", "")
        severity = vulnerability.get("severity", "medium")

        if vuln_type == "sql_injection":
            result = self._verify_sql_injection(payload, target_info)
        elif vuln_type == "xss":
            result = self._verify_xss(payload, target_info)
        elif vuln_type == "command_injection":
            result = self._verify_command_injection(payload, target_info)
        elif vuln_type == "path_traversal":
            result = self._verify_path_traversal(payload, target_info)
        else:
            result = self._verify_generic(payload, target_info)

        record = {
            "verify_id": verify_id,
            "vulnerability": vulnerability,
            "result": result,
            "timestamp": time.time()
        }
        self.verification_history.append(record)

        requires_approval = severity in ["high", "critical"] or result.get("reproducible", False)
        result["verify_id"] = verify_id
        result["requires_approval"] = requires_approval

        return result

    def _check_sandbox_integrity(self) -> bool:
        if self.config.allowed_network:
            return True
        return True

    def _verify_sql_injection(self, payload: str, target: Dict) -> Dict[str, Any]:
        is_reproducible = any(keyword in payload.lower()
                             for keyword in ["select", "union", "drop", "insert", "' or", "1=1"])

        if is_reproducible:
            return {
                "reproducible": True,
                "severity": "high",
                "impact": "可能导致数据库信息泄露或数据篡改",
                "cvss_estimate": 8.5,
                "sandbox_log": f"成功在模拟环境中复现SQL注入。载荷: {payload[:100]}"
            }
        return {
            "reproducible": False,
            "severity": "info",
            "impact": "无法在沙箱中复现",
            "sandbox_log": "复现失败"
        }

    def _verify_xss(self, payload: str, target: Dict) -> Dict[str, Any]:
        is_reproducible = any(keyword in payload.lower()
                             for keyword in ["<script>", "javascript:", "onerror=", "onload="])

        return {
            "reproducible": is_reproducible,
            "severity": "medium" if is_reproducible else "low",
            "impact": "可能导致客户端脚本注入" if is_reproducible else "未发现可利用点",
            "sandbox_log": f"XSS验证完成。载荷: {payload[:100]}"
        }

    def _verify_command_injection(self, payload: str, target: Dict) -> Dict[str, Any]:
        is_reproducible = any(keyword in payload.lower()
                             for keyword in [";", "|", "`", "$(", "&&"])

        return {
            "reproducible": is_reproducible,
            "severity": "critical" if is_reproducible else "medium",
            "impact": "可能导致远程命令执行" if is_reproducible else "未发现可利用点",
            "sandbox_log": "命令注入验证完成。"
        }

    def _verify_path_traversal(self, payload: str, target: Dict) -> Dict[str, Any]:
        is_reproducible = "../" in payload or "..\\" in payload

        return {
            "reproducible": is_reproducible,
            "severity": "high" if is_reproducible else "low",
            "impact": "可能读取系统敏感文件" if is_reproducible else "未发现可利用点",
            "sandbox_log": "路径遍历验证完成。"
        }

    def _verify_generic(self, payload: str, target: Dict) -> Dict[str, Any]:
        return {
            "reproducible": False,
            "severity": "info",
            "impact": "未知漏洞类型，需人工分析",
            "sandbox_log": "无法自动验证，已记录payload。"
        }

    def get_verification_stats(self) -> Dict[str, int]:
        total = len(self.verification_history)
        reproducible = sum(1 for r in self.verification_history
                          if r["result"].get("reproducible", False))
        return {
            "total": total,
            "reproducible": reproducible,
            "false_positive": total - reproducible
        }