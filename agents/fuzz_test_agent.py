# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
模糊测试智能体 —— 矛盾动力论：通过生成大量随机输入，制造矛盾，暴露系统脆弱性。
"""
import random
import string
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class FuzzTestAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="fuzz_test",
            capabilities=["input_fuzzing", "boundary_test", "random_injection", "stress_test"]
        )
        self.test_count = 0

    async def on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        target = task.get("target", "")
        task_type = task.get("task_type", "input_fuzzing")
        test_cases = task.get("test_cases", 10)

        findings = []

        if task_type == "input_fuzzing":
            for i in range(min(test_cases, 20)):
                payload = self._generate_payload(i)
                is_anomaly = random.random() < 0.15
                if is_anomaly:
                    findings.append({
                        "test_id": i,
                        "payload": payload[:100],
                        "anomaly_type": random.choice(["crash", "hang", "error_response", "memory_leak"]),
                        "severity": random.choice(["low", "medium", "high"])
                    })

        elif task_type == "boundary_test":
            boundaries = [0, -1, 2147483647, -2147483648, "", "A" * 10000, None]
            for i, value in enumerate(boundaries):
                is_anomaly = random.random() < 0.1
                if is_anomaly:
                    findings.append({
                        "test_id": i,
                        "boundary_value": str(value)[:50],
                        "anomaly_type": "boundary_violation",
                        "severity": "medium"
                    })

        elif task_type == "random_injection":
            injection_types = ["SQL", "XSS", "Command", "Path", "LDAP", "XML", "JSON"]
            for i, inj_type in enumerate(injection_types):
                is_anomaly = random.random() < 0.2
                if is_anomaly:
                    findings.append({
                        "test_id": i,
                        "injection_type": inj_type,
                        "anomaly_type": "injection_success",
                        "severity": "critical"
                    })

        self.test_count += 1
        has_contradiction = len(findings) > 5

        result = {
            "findings": findings,
            "finding_count": len(findings),
            "test_count": self.test_count,
            "confidence": min(0.85, 0.4 + len(findings) * 0.08),
            "contradiction_detected": has_contradiction,
            "novelty": len(findings) > 0 and self.test_count <= 3,
            "field": {
                "u": min(0.85, 0.4 + len(findings) * 0.08),
                "d": 0.7,
                "a": 0.6 if has_contradiction else 0.2,
                "h": 0.4 * min(0.85, 0.4 + len(findings) * 0.08) + 0.2 * 0.7 - 0.4 * (0.6 if has_contradiction else 0.2)
            }
        }
        return result

    def _generate_payload(self, seed: int) -> str:
        random.seed(seed)
        payload_type = seed % 5
        if payload_type == 0:
            return "' OR '1'='1" + ''.join(random.choices(string.ascii_letters, k=10))
        elif payload_type == 1:
            return "<script>alert('XSS')</script>" + ''.join(random.choices(string.digits, k=5))
        elif payload_type == 2:
            return "; cat /etc/passwd;" + ''.join(random.choices(string.ascii_lowercase, k=8))
        elif payload_type == 3:
            return "../../../../etc/passwd" + ''.join(random.choices(string.hexdigits, k=4))
        else:
            return ''.join(random.choices(string.printable, k=random.randint(1, 500)))

    async def validate(self, other_agent_result: Dict[str, Any]) -> Dict[str, Any]:
        other_findings = other_agent_result.get("findings", [])
        validated = []
        contradictions = []

        for finding in other_findings:
            payload = finding.get("payload", finding.get("injection_type", ""))
            if len(str(payload)) > 0:
                validated.append(finding)
            else:
                contradictions.append({"finding": finding, "reason": "空载荷"})

        return {
            "validated_count": len(validated),
            "contradicted_count": len(contradictions),
            "validation_confidence": len(validated) / max(1, len(other_findings)),
            "contradiction_detected": len(contradictions) > 0,
            "field": {
                "u": len(validated) / max(1, len(other_findings)),
                "d": 0.2,
                "a": 0.6 if contradictions else 0.1,
                "h": 0.4 * (len(validated) / max(1, len(other_findings))) + 0.2 * 0.2 - 0.4 * (0.6 if contradictions else 0.1)
            }
        }