# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
代码审计智能体 —— 关系本体论：漏洞不是代码的内在属性，而是代码与安全规则之间的“关系断裂”。
"""
import re
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class CodeAuditAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="code_audit",
            capabilities=["static_analysis", "sql_injection", "xss", "command_injection", "path_traversal"]
        )
        self.rules = {
            "sql_injection": [
                r"(?i)(select|insert|update|delete)\s+.*\s+(from|into|set)\s+.*\s*\+",
                r"(?i)execute\s*\(\s*[\"'].*\+",
                r"(?i)rawQuery|execSQL|executeQuery"
            ],
            "xss": [
                r"(?i)innerHTML\s*=|document\.write\s*\(",
                r"(?i)eval\s*\(|setTimeout\s*\(\s*[\"']",
                r"(?i)dangerouslySetInnerHTML"
            ],
            "command_injection": [
                r"(?i)(system|exec|popen|subprocess)\s*\(",
                r"(?i)os\.system|shell_exec|passthru"
            ],
            "path_traversal": [
                r"(?i)\.\.\/|\.\.\\\\",
                r"(?i)file_get_contents|open\s*\(\s*.*\.\.\/"
            ]
        }

    async def on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        code = task.get("code", "")
        task_type = task.get("task_type", "static_analysis")

        findings = []
        confidence = 0.5
        contradictions = []

        if task_type in self.rules:
            rules_to_apply = {task_type: self.rules[task_type]}
        else:
            rules_to_apply = self.rules

        for vuln_type, patterns in rules_to_apply.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    line_content = code.split('\n')[line_num - 1].strip()
                    findings.append({
                        "type": vuln_type,
                        "line": line_num,
                        "content": line_content[:200],
                        "pattern": pattern,
                        "confidence": 0.7
                    })

        if findings:
            confidence = min(0.9, 0.5 + len(findings) * 0.1)
            types_found = set(f["type"] for f in findings)
            has_contradiction = len(types_found) > 1
        else:
            confidence = 0.3
            has_contradiction = False

        result = {
            "findings": findings,
            "finding_count": len(findings),
            "confidence": confidence,
            "contradiction_detected": has_contradiction,
            "novelty": len(findings) > 3,
            "field": {
                "u": confidence,
                "d": 0.5 if len(findings) > 0 else 0.1,
                "a": 0.7 if has_contradiction else 0.1,
                "h": 0.4 * confidence + 0.2 * (0.5 if len(findings) > 0 else 0.1) - 0.4 * (0.7 if has_contradiction else 0.1)
            }
        }
        return result

    async def validate(self, other_agent_result: Dict[str, Any]) -> Dict[str, Any]:
        other_findings = other_agent_result.get("findings", [])

        validated_findings = []
        contradictions = []

        for finding in other_findings:
            line_content = finding.get("content", "")
            pattern = finding.get("pattern", "")
            vuln_type = finding.get("type", "")

            is_valid = False
            if vuln_type in self.rules:
                for p in self.rules[vuln_type]:
                    if re.search(p, line_content):
                        is_valid = True
                        break

            if is_valid:
                validated_findings.append(finding)
            else:
                contradictions.append({
                    "original": finding,
                    "reason": "规则无法复现该漏洞"
                })

        validation_confidence = len(validated_findings) / max(1, len(other_findings))
        has_contradiction = len(contradictions) > 0

        return {
            "validated_count": len(validated_findings),
            "contradicted_count": len(contradictions),
            "validation_confidence": validation_confidence,
            "contradiction_detected": has_contradiction,
            "field": {
                "u": validation_confidence,
                "d": 0.3,
                "a": 0.8 if has_contradiction else 0.1,
                "h": 0.4 * validation_confidence + 0.2 * 0.3 - 0.4 * (0.8 if has_contradiction else 0.1)
            }
        }