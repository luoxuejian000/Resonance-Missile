# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
CodeAuditAgent — 漏洞挖掘智能体（升级版）
晶脉哲学映射：
  - 关系本体论：利用全局经验场，检测结果反馈回场域
  - 矛盾动力论：矛盾被显化而非压制
  - 悖论防护：置信度基于证据强度，非数量
"""
import re
import time
import random
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent


class CodeAuditAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="code_audit",
            capabilities=["static_analysis", "sql_injection", "xss", "command_injection", "path_traversal"]
        )
        self.experience = []
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

    def _calculate_confidence(self, findings: List[Dict], code_context: str) -> float:
        if not findings:
            return 0.0

        total_weight = 0.0
        for f in findings:
            pattern = f.get("pattern", "")
            if any(kw in pattern.upper() for kw in ["SELECT", "WHERE", "FROM", "INSERT", "UPDATE", "DELETE"]):
                precision = 0.8
            elif any(kw in pattern for kw in ["innerHTML", "eval", "document.write"]):
                precision = 0.75
            else:
                precision = 0.6

            line_num = f.get("line", 1)
            lines = code_context.split("\n")
            context_window = lines[max(0, line_num-2): min(len(lines), line_num+2)]
            danger_kw = ["user", "input", "query", "execute", "eval", "innerHTML"]
            context_score = 0.2 * sum(1 for kw in danger_kw if any(kw in l.lower() for l in context_window))

            pattern_key = f"{f.get('type', 'unknown')}:{pattern}"
            hot = self.get_effective_hotness(pattern_key)

            weight = precision + context_score + hot * 0.3
            total_weight += min(1.0, weight)

        return min(0.95, total_weight / len(findings) + 0.1)

    async def on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        code = task.get("code", "")
        task_type = task.get("task_type", "static_analysis")

        hot_patterns = self.get_hot_patterns(limit=10)
        hot_vuln_types = {p.split(":")[0] if ":" in p else p for p, _ in hot_patterns}

        if task_type in self.rules:
            rules_to_apply = {task_type: self.rules[task_type]}
        else:
            rules_to_apply = self.rules

        types_to_check = list(rules_to_apply.keys())
        if random.random() < 0.05:
            ordered = types_to_check
        else:
            ordered = [t for t in types_to_check if t in hot_vuln_types]
            ordered += [t for t in types_to_check if t not in hot_vuln_types]

        findings = []
        false_positive_records = self.shared_memory.get("false_positive_records", {})

        for vuln_type in ordered:
            for pattern in rules_to_apply.get(vuln_type, []):
                pattern_key = f"{vuln_type}:{pattern}"
                if pattern_key in false_positive_records:
                    self.update_pattern_hotness(pattern_key, hit=False)
                    continue

                matches = list(re.finditer(pattern, code))
                if matches:
                    for match in matches:
                        line_num = code[:match.start()].count('\n') + 1
                        line_content = (code.split('\n')[line_num - 1].strip() if line_num <= len(code.split('\n')) else "")

                        f = {
                            "type": vuln_type,
                            "line": line_num,
                            "content": line_content[:200],
                            "pattern": pattern,
                            "source": self.agent_id,
                            "raw_match": match.group()
                        }
                        findings.append(f)

                        self.update_pattern_hotness(pattern_key, hit=True)
                else:
                    self.update_pattern_hotness(pattern_key, hit=False)

        confidence = self._calculate_confidence(findings, code)
        types_found = set(f["type"] for f in findings)
        has_contra = len(types_found) > 1

        result = {
            "findings": findings,
            "finding_count": len(findings),
            "confidence": confidence,
            "contradiction_detected": has_contra,
            "novelty": len(findings) > 3,
            "field": {
                "u": confidence,
                "d": 0.5 if findings else 0.1,
                "a": 0.7 if has_contra else 0.1,
                "h": 0.4 * confidence + 0.3 * (0.5 if findings else 0.1),
            },
            "source": self.agent_id,
        }
        self.experience.append({"task": "audit", "result": result})
        return result

    def get_hot_patterns(self, limit: int = 10) -> List[tuple]:
        hotness = []
        all_keys = set(self.shared_memory["pattern_hotness"].keys()) | set(self.shared_memory["pattern_scanned"].keys())
        for key in all_keys:
            effective = self.get_effective_hotness(key)
            hotness.append((key, effective))
        hotness.sort(key=lambda x: x[1], reverse=True)
        return hotness[:limit]

    def check_global_health(self) -> Dict:
        now = time.time()
        recent_fp = [m for m in self.shared_memory["misclassification"]
                     if now - m.get("timestamp", 0) < 3600 and not m.get("human_confirmed")]
        total = max(1, len(self.shared_memory.get("_task_history", [])))
        fp_rate = len(recent_fp) / total

        issues = []
        status = "healthy"
        if fp_rate > 0.3:
            status = "unhealthy"
            issues.append({
                "type": "high_false_positive_rate",
                "value": round(fp_rate, 4),
                "suggested_action": "暂停该Agent任务分配，由人类审核近期审计结果",
                "human_decision_required": True
            })
        hotness_vals = [h for _, h in self.get_hot_patterns(10)]
        if len(hotness_vals) < 3:
            issues.append({
                "type": "hotness_sparse",
                "suggested_action": "热度表稀疏，建议检查扫描覆盖范围",
                "human_decision_required": False
            })

        return {
            "status": status,
            "agent_id": self.agent_id,
            "recent_fp_rate": round(fp_rate, 4),
            "hot_pattern_count": len(hotness_vals),
            "issues": issues,
            "timestamp": now,
            "disclaimer": "此诊断仅供人类参考，任何恢复操作必须由人类显式触发"
        }

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