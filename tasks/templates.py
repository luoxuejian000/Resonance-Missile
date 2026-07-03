# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
任务模板 —— 关系本体论：将常见的漏洞挖掘任务结构化为标准模板，
使智能体可以基于模板快速理解任务意图。
"""
from typing import Dict, Any, List


class TaskTemplate:
    @staticmethod
    def code_audit(target_code: str, audit_types: List[str] = None) -> Dict[str, Any]:
        return {
            "task_type": "static_analysis",
            "code": target_code,
            "audit_types": audit_types or ["sql_injection", "xss", "command_injection", "path_traversal"],
            "requires_approval": False
        }

    @staticmethod
    def fuzz_test(target: str, test_type: str = "input_fuzzing", test_cases: int = 20) -> Dict[str, Any]:
        return {
            "task_type": test_type,
            "target": target,
            "test_cases": test_cases,
            "requires_approval": False
        }

    @staticmethod
    def verify_findings(original_findings: List[Dict], code: str) -> Dict[str, Any]:
        return {
            "task_type": "reproduce",
            "findings": original_findings,
            "code": code,
            "requires_approval": True
        }

    @staticmethod
    def dependency_check(dependencies: List[Dict]) -> Dict[str, Any]:
        return {
            "task_type": "version_check",
            "dependencies": dependencies,
            "requires_approval": False
        }

    @staticmethod
    def knowledge_query(query: str, query_type: str = "cve_lookup") -> Dict[str, Any]:
        return {
            "task_type": query_type,
            "query": query,
            "requires_approval": False
        }

    @staticmethod
    def high_risk_operation(operation: Dict[str, Any], reason: str) -> Dict[str, Any]:
        return {
            "task_type": "high_risk",
            "operation": operation,
            "reason": reason,
            "requires_approval": True,
            "risk_level": "high"
        }