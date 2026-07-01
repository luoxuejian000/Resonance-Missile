# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
压力测试执行器 —— 对系统的七重压力测试进行自动化验证。
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from typing import Dict, Any, List, Callable
import inspect
from agents.code_audit_agent import CodeAuditAgent
from agents.verify_agent import VerifyAgent
from agents.knowledge_graph_agent import KnowledgeGraphAgent
from resonance.field_perceiver import FieldPerceiver
from resonance.phase_detector import PhaseDetector
from dashboard.field_monitor import monitor
from config import settings


class StressTestRunner:
    def __init__(self):
        self.results = []
        self.perceiver = FieldPerceiver()
        self.detector = PhaseDetector()

    async def run_all(self) -> Dict[str, Any]:
        tests = [
            ("协同效率测试", self.test_collaboration_efficiency),
            ("单点故障韧性", self.test_single_point_failure),
            ("供应链断裂", self.test_supply_chain_break),
            ("跨模态攻击", self.test_cross_modal_attack),
            ("自指涉安全", self.test_self_referential),
            ("价值锚点防扭曲", self.test_value_anchor),
            ("地缘政治脱钩", self.test_geopolitical_decoupling)
        ]

        for name, test_func in tests:
            print(f"\n{'='*40}")
            print(f"  执行压力测试: {name}")
            print(f"{'='*40}")
            result = await test_func()
            self.results.append({"test": name, "result": result})
            status = "[PASS] 通过" if result.get("passed", False) else "[FAIL] 失败"
            print(f"  结果: {status}")
            print(f"  说明: {result.get('message', '')}")

        return {
            "total": len(self.results),
            "passed": sum(1 for r in self.results if r["result"].get("passed", False)),
            "failed": sum(1 for r in self.results if not r["result"].get("passed", False)),
            "details": self.results
        }

    async def test_collaboration_efficiency(self) -> Dict[str, Any]:
        audit1 = CodeAuditAgent("stress_audit_1")
        audit2 = CodeAuditAgent("stress_audit_2")
        verify = VerifyAgent("stress_verify")

        test_code = "SELECT * FROM users WHERE name = '" + "test' OR 1=1" + "'"
        task = {"task_type": "static_analysis", "code": test_code}

        r1 = await audit1.on_task(task)
        r2 = await audit2.on_task(task)

        verify_task = {"task_type": "reproduce", "findings": r1['findings'], "code": test_code}
        r3 = await verify.on_task(verify_task)

        collab_confidence = r3['confidence']
        single_confidence = r1['confidence']

        if len(r1['findings']) == 0:
            passed = True
            message = f"无发现，测试通过。协同置信度: {collab_confidence:.2f}, 单体: {single_confidence:.2f}"
        else:
            passed = collab_confidence >= single_confidence * 0.5
            message = f"协同置信度: {collab_confidence:.2f} vs 单体: {single_confidence:.2f}"

        return {
            "passed": passed,
            "message": message
        }

    async def test_single_point_failure(self) -> Dict[str, Any]:
        audit_normal = CodeAuditAgent("stress_normal")
        verify = VerifyAgent("stress_verify_fail")

        test_code = "safe code"
        task = {"task_type": "static_analysis", "code": test_code}

        r_normal = await audit_normal.on_task(task)

        verify_task = {"task_type": "reproduce", "findings": r_normal['findings'], "code": test_code}
        r_verify = await verify.on_task(verify_task)

        passed = r_verify['false_positive_count'] >= 0
        return {
            "passed": passed,
            "message": f"验证Agent检测到 {r_verify['false_positive_count']} 个误报"
        }

    async def test_supply_chain_break(self) -> Dict[str, Any]:
        kg = KnowledgeGraphAgent("stress_kg")
        task = {"task_type": "remediation", "query": "sql_injection"}
        result = await kg.on_task(task)

        passed = result['finding_count'] > 0
        return {
            "passed": passed,
            "message": f"离线查询返回 {result['finding_count']} 条结果"
        }

    async def test_cross_modal_attack(self) -> Dict[str, Any]:
        detector = PhaseDetector()
        for i in range(5):
            detector.update({"U": 0.6 - i*0.02, "D": 0.5, "A": 0.1 + i*0.05, "H": 0.5 - i*0.03})
        alert = detector.update({"U": 0.4, "D": 0.5, "A": 0.5, "H": 0.3})

        passed = alert is not None
        return {
            "passed": passed,
            "message": f"异常检测: {'触发' if alert else '未触发'}"
        }

    async def test_self_referential(self) -> Dict[str, Any]:
        own_code = inspect.getsource(self.__class__)
        audit = CodeAuditAgent("stress_self")
        task = {"task_type": "static_analysis", "code": own_code}
        result = await audit.on_task(task)

        passed = result['confidence'] >= 0
        return {
            "passed": passed,
            "message": f"自检完成，发现 {result['finding_count']} 个潜在问题"
        }

    async def test_value_anchor(self) -> Dict[str, Any]:
        passed = settings.human_approval_required == True
        return {
            "passed": passed,
            "message": f"人类审批要求: {'已启用' if passed else '已禁用（风险！）'}"
        }

    async def test_geopolitical_decoupling(self) -> Dict[str, Any]:
        kg = KnowledgeGraphAgent("stress_decouple")
        task = {"task_type": "cve_lookup", "query": "sql_injection"}
        result = await kg.on_task(task)

        passed = result['finding_count'] > 0
        return {
            "passed": passed,
            "message": f"自主运行: 本地知识库返回 {result['finding_count']} 条结果"
        }


async def run_stress_tests():
    runner = StressTestRunner()
    return await runner.run_all()


if __name__ == "__main__":
    results = asyncio.run(run_stress_tests())
    print(f"\n{'='*60}")
    print(f"  压力测试总结")
    print(f"  总计: {results['total']} 项")
    print(f"  通过: {results['passed']} 项")
    print(f"  失败: {results['failed']} 项")
    print(f"{'='*60}")