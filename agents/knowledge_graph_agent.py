# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
知识图谱智能体 —— 关系本体论：将漏洞、CVE、攻击模式、修复方案组织为关系网络。
"""
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class KnowledgeGraphAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="knowledge_graph",
            capabilities=["cve_lookup", "attack_pattern", "remediation", "dependency_analysis"]
        )
        self.knowledge_base = {
            "sql_injection": {
                "cve": ["CVE-2023-1234", "CVE-2022-5678"],
                "attack_pattern": "CAPEC-66",
                "remediation": "使用参数化查询或预编译语句",
                "severity": "high"
            },
            "xss": {
                "cve": ["CVE-2023-4321"],
                "attack_pattern": "CAPEC-63",
                "remediation": "对所有用户输入进行HTML实体编码",
                "severity": "medium"
            },
            "command_injection": {
                "cve": ["CVE-2023-8765"],
                "attack_pattern": "CAPEC-88",
                "remediation": "避免将用户输入直接传递给系统命令",
                "severity": "critical"
            },
            "path_traversal": {
                "cve": ["CVE-2022-1111"],
                "attack_pattern": "CAPEC-126",
                "remediation": "使用白名单验证文件路径",
                "severity": "high"
            }
        }

    async def on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("task_type", "")
        query = task.get("query", "")

        findings = []

        if task_type == "cve_lookup":
            for vuln_type, info in self.knowledge_base.items():
                if vuln_type.lower() in query.lower() or query.lower() in vuln_type.lower():
                    findings.append({
                        "vuln_type": vuln_type,
                        "cve_list": info["cve"],
                        "severity": info["severity"]
                    })

        elif task_type == "attack_pattern":
            for vuln_type, info in self.knowledge_base.items():
                if vuln_type.lower() in query.lower():
                    findings.append({
                        "vuln_type": vuln_type,
                        "attack_pattern": info["attack_pattern"],
                        "severity": info["severity"]
                    })

        elif task_type == "remediation":
            for vuln_type, info in self.knowledge_base.items():
                if vuln_type.lower() in query.lower():
                    findings.append({
                        "vuln_type": vuln_type,
                        "remediation": info["remediation"],
                        "severity": info["severity"]
                    })

        elif task_type == "dependency_analysis":
            for vuln_type, info in self.knowledge_base.items():
                if vuln_type.lower() in query.lower():
                    findings.append({
                        "vuln_type": vuln_type,
                        "full_info": info
                    })

        confidence = min(0.9, 0.5 + len(findings) * 0.15) if findings else 0.2

        result = {
            "findings": findings,
            "finding_count": len(findings),
            "confidence": confidence,
            "contradiction_detected": False,
            "novelty": len(findings) > 0,
            "field": {
                "u": confidence,
                "d": 0.6 if findings else 0.1,
                "a": 0.1,
                "h": 0.4 * confidence + 0.2 * (0.6 if findings else 0.1) - 0.4 * 0.1
            }
        }
        return result

    async def validate(self, other_agent_result: Dict[str, Any]) -> Dict[str, Any]:
        other_findings = other_agent_result.get("findings", [])
        validated = []
        contradictions = []

        for finding in other_findings:
            vuln_type = finding.get("type", finding.get("vuln_type", ""))
            if vuln_type in self.knowledge_base:
                validated.append(finding)
            else:
                contradictions.append({
                    "finding": finding,
                    "reason": "未知漏洞类型，无法在知识库中找到匹配"
                })

        return {
            "validated_count": len(validated),
            "contradicted_count": len(contradictions),
            "validation_confidence": len(validated) / max(1, len(other_findings)),
            "contradiction_detected": len(contradictions) > 0,
            "field": {
                "u": len(validated) / max(1, len(other_findings)),
                "d": 0.2,
                "a": 0.7 if contradictions else 0.1,
                "h": 0.4 * (len(validated) / max(1, len(other_findings))) + 0.2 * 0.2 - 0.4 * (0.7 if contradictions else 0.1)
            }
        }