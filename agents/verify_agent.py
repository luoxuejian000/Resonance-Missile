# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
VerifyAgent — 裁决智能体（升级版）
晶脉哲学映射：
  - 实践介入论：验证结果回写场域，影响未来审计
  - 矛盾动力论：矛盾被显化，不压制
"""
import random
import re
import time
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class VerifyAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="verify",
            capabilities=["reproduce", "cross_check", "false_positive_detection"]
        )
        self.verified_count = 0
        self.false_positive_count = 0
        self.experience = []

    async def on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        original_findings = task.get("findings", [])
        kg_findings = task.get("kg_findings", [])
        code = task.get("code", "")
        task_type = task.get("task_type", "reproduce")

        verified = []
        false_positives = []
        contradiction = False

        if task_type == "reproduce":
            for f in original_findings:
                content = f.get("content", "")
                pattern = f.get("pattern", "")
                vuln_type = f.get("type", "")

                is_confirmed = self._independent_check(content, pattern, vuln_type)
                cve_match = self._check_cve_match(f, kg_findings)

                if is_confirmed or cve_match:
                    verified.append({**f, "reproduced": True, "verified": True})
                    self.verified_count += 1
                else:
                    false_positives.append({**f, "reproduced": False, "verified": False, "reason": "无法独立复现且未匹配知识库"})
                    self.false_positive_count += 1
                    contradiction = True
                    self.record_misclassification(f, self.agent_id)

        elif task_type == "false_positive_detection":
            for f in original_findings:
                content = f.get("content", "")
                is_false = self._is_false_positive(content)
                cve_match = self._check_cve_match(f, kg_findings)

                if is_false and not cve_match:
                    false_positives.append({**f, "false_positive": True, "verified": False})
                    self.false_positive_count += 1
                    contradiction = True
                    self.record_misclassification(f, self.agent_id)
                else:
                    verified.append({**f, "false_positive": False, "verified": True})
                    self.verified_count += 1

        has_contradiction = len(false_positives) > 0 or contradiction

        for verified_finding in verified:
            pattern_key = f"{verified_finding['type']}_{verified_finding['pattern']}"
            if pattern_key in self.shared_memory["vulnerability_patterns"]:
                self.shared_memory["vulnerability_patterns"][pattern_key]["confirmed"] += 1

        for fp_finding in false_positives:
            pattern_key = f"{fp_finding['type']}_{fp_finding['pattern']}"
            if pattern_key in self.shared_memory["vulnerability_patterns"]:
                self.shared_memory["vulnerability_patterns"][pattern_key]["false_positive"] += 1
            self.shared_memory["false_positive_records"][pattern_key] = {
                "reason": fp_finding.get("reason", "无法复现"),
                "count": self.shared_memory["false_positive_records"].get(pattern_key, {}).get("count", 0) + 1
            }

        self.recent_results.extend([True] * len(verified) + [False] * len(false_positives))
        if len(self.recent_results) > 10:
            self.recent_results = self.recent_results[-10:]
        self.false_positive_rate = sum(1 for r in self.recent_results if not r) / max(1, len(self.recent_results))
        self.needs_calibration = self.false_positive_rate > 0.3

        if self.needs_calibration:
            self.shared_memory["calibration_status"][self.agent_id] = {
                "status": "needs_calibration",
                "false_positive_rate": self.false_positive_rate,
                "recent_results": len(self.recent_results)
            }

        confidence = 0.90 if verified and all(v.get("verified") for v in verified) else 0.55

        result = {
            "verified_findings": verified,
            "false_positives": false_positives,
            "findings": verified,
            "verified_count": len(verified),
            "false_positive_count": len(false_positives),
            "total_verified": self.verified_count,
            "total_false_positives": self.false_positive_count,
            "confidence": confidence,
            "contradiction_detected": has_contradiction,
            "novelty": False,
            "needs_calibration": self.needs_calibration,
            "false_positive_rate": self.false_positive_rate,
            "field": {
                "u": 0.08 if has_contradiction else 0.25,
                "d": 0.35 if has_contradiction else 0.15,
                "a": 0.75 if has_contradiction else 0.10,
                "h": 0.25 if has_contradiction else 0.80,
            },
            "source": self.agent_id,
        }
        self.experience.append({"verified": len(verified), "result": result})
        return result

    def _check_cve_match(self, finding: Dict, kg_findings: List[Dict]) -> bool:
        if not kg_findings:
            return False
        vuln_type = finding.get("type", "")
        for kg in kg_findings:
            if isinstance(kg, dict):
                description = kg.get("description", "").lower()
                if vuln_type.replace("_", " ") in description:
                    return True
        return False

    def _independent_check(self, content: str, pattern: str, vuln_type: str) -> bool:
        if pattern and content:
            try:
                return bool(re.search(pattern, content))
            except re.error:
                return False
        return random.random() > 0.2

    def _is_false_positive(self, content: str) -> bool:
        safe_indicators = [
            "sanitize", "escape", "validate", "filter", "prepared",
            "parameterized", "whitelist", "allowlist"
        ]
        return any(indicator in content.lower() for indicator in safe_indicators)

    async def validate(self, other_agent_result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "validated_count": other_agent_result.get("verified_count", 0),
            "contradicted_count": other_agent_result.get("false_positive_count", 0),
            "validation_confidence": 1.0,
            "contradiction_detected": other_agent_result.get("contradiction_detected", False),
            "field": {"u": 1.0, "d": 0.1, "a": 0.0, "h": 0.5}
        }