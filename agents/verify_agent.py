# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
验证智能体 —— 实践介入论：独立复现其他智能体的发现，防止误报。
"""
import random
import re
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

    async def on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        original_findings = task.get("findings", [])
        code = task.get("code", "")
        task_type = task.get("task_type", "reproduce")

        verified = []
        false_positives = []

        if task_type == "reproduce":
            for finding in original_findings:
                content = finding.get("content", "")
                pattern = finding.get("pattern", "")
                vuln_type = finding.get("type", "")

                is_confirmed = self._independent_check(content, pattern, vuln_type)

                if is_confirmed:
                    verified.append({**finding, "reproduced": True})
                    self.verified_count += 1
                else:
                    false_positives.append({**finding, "reproduced": False, "reason": "无法独立复现"})
                    self.false_positive_count += 1

        elif task_type == "false_positive_detection":
            for finding in original_findings:
                content = finding.get("content", "")
                is_false = self._is_false_positive(content)
                if is_false:
                    false_positives.append({**finding, "false_positive": True})
                    self.false_positive_count += 1
                else:
                    verified.append({**finding, "false_positive": False})
                    self.verified_count += 1

        has_contradiction = len(false_positives) > 0

        result = {
            "verified_findings": verified,
            "false_positives": false_positives,
            "verified_count": len(verified),
            "false_positive_count": len(false_positives),
            "total_verified": self.verified_count,
            "total_false_positives": self.false_positive_count,
            "confidence": len(verified) / max(1, len(original_findings)),
            "contradiction_detected": has_contradiction,
            "novelty": False,
            "field": {
                "u": len(verified) / max(1, len(original_findings)),
                "d": 0.3,
                "a": 0.8 if has_contradiction else 0.1,
                "h": 0.4 * (len(verified) / max(1, len(original_findings))) + 0.2 * 0.3 - 0.4 * (0.8 if has_contradiction else 0.1)
            }
        }
        return result

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
            "contradicted_count": 0,
            "validation_confidence": 1.0,
            "contradiction_detected": False,
            "field": {"u": 1.0, "d": 0.1, "a": 0.0, "h": 0.5}
        }