# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
依赖分析智能体 —— 关系本体论：分析代码库的依赖关系，检测供应链风险。
"""
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class DependencyAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="dependency_analysis",
            capabilities=["supply_chain", "version_check", "license_audit", "dependency_graph"]
        )
        self.known_vulnerable = {
            "log4j": {"versions": ["2.0-2.14.1"], "cve": "CVE-2021-44228"},
            "struts2": {"versions": ["2.0-2.5.26"], "cve": "CVE-2020-17530"},
            "spring": {"versions": ["5.3.0-5.3.17"], "cve": "CVE-2022-22965"},
            "fastjson": {"versions": ["1.2.0-1.2.80"], "cve": "CVE-2022-25845"}
        }

    async def on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        dependencies = task.get("dependencies", [])
        task_type = task.get("task_type", "version_check")

        findings = []

        if task_type == "version_check":
            for dep in dependencies:
                name = dep.get("name", "").lower()
                version = dep.get("version", "")
                if name in self.known_vulnerable:
                    vuln_info = self.known_vulnerable[name]
                    findings.append({
                        "dependency": name,
                        "current_version": version,
                        "vulnerable_versions": vuln_info["versions"],
                        "cve": vuln_info["cve"],
                        "severity": "critical" if "log4j" in name else "high"
                    })

        elif task_type == "supply_chain":
            for dep in dependencies:
                source = dep.get("source", "")
                if any(unsafe in source.lower() for unsafe in ["untrusted", "unknown", "third-party"]):
                    findings.append({
                        "dependency": dep.get("name", ""),
                        "source": source,
                        "risk": "untrusted_source",
                        "severity": "high"
                    })

        has_risk = len(findings) > 0

        result = {
            "findings": findings,
            "finding_count": len(findings),
            "confidence": min(0.9, 0.5 + len(findings) * 0.2),
            "contradiction_detected": has_risk,
            "novelty": len(findings) > 0,
            "field": {
                "u": min(0.9, 0.5 + len(findings) * 0.2),
                "d": 0.5 if findings else 0.1,
                "a": 0.7 if has_risk else 0.1,
                "h": 0.4 * min(0.9, 0.5 + len(findings) * 0.2) + 0.2 * (0.5 if findings else 0.1) - 0.4 * (0.7 if has_risk else 0.1)
            }
        }
        return result

    async def validate(self, other_agent_result: Dict[str, Any]) -> Dict[str, Any]:
        findings = other_agent_result.get("findings", [])
        validated = [f for f in findings if f.get("dependency", "") in self.known_vulnerable]

        return {
            "validated_count": len(validated),
            "contradicted_count": len(findings) - len(validated),
            "validation_confidence": len(validated) / max(1, len(findings)),
            "contradiction_detected": len(findings) != len(validated),
            "field": {
                "u": len(validated) / max(1, len(findings)),
                "d": 0.2,
                "a": 0.6 if len(findings) != len(validated) else 0.1,
                "h": 0.4 * (len(validated) / max(1, len(findings))) + 0.2 * 0.2 - 0.4 * (0.6 if len(findings) != len(validated) else 0.1)
            }
        }