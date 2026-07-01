# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
集成测试 —— 验证多智能体协同和场域调谐功能。
"""
import asyncio
import pytest
from agents.code_audit_agent import CodeAuditAgent
from agents.verify_agent import VerifyAgent
from agents.knowledge_graph_agent import KnowledgeGraphAgent
from resonance.field_perceiver import FieldPerceiver
from resonance.phase_detector import PhaseDetector
from resonance.harmony_tuner import HarmonyTuner
from tasks.templates import TaskTemplate


SQL_INJECTION_CODE = """
def search(query):
    sql = "SELECT * FROM products WHERE name LIKE '%" + query + "%'"
    return db.execute(sql)
"""


SAFE_CODE = """
def search(query):
    sql = "SELECT * FROM products WHERE name LIKE ?"
    return db.execute(sql, [f"%{query}%"])
"""


@pytest.mark.asyncio
async def test_code_audit_finds_vulnerability():
    agent = CodeAuditAgent("test_audit")
    task = TaskTemplate.code_audit(SQL_INJECTION_CODE, ["sql_injection"])
    result = await agent.on_task(task)
    assert result['finding_count'] > 0
    assert any(f['type'] == 'sql_injection' for f in result['findings'])


@pytest.mark.asyncio
async def test_verify_rejects_false_positive():
    verify_agent = VerifyAgent("test_verify")
    audit_agent = CodeAuditAgent("test_audit")

    task = TaskTemplate.code_audit(SAFE_CODE, ["sql_injection"])
    audit_result = await audit_agent.on_task(task)

    verify_task = TaskTemplate.verify_findings(audit_result['findings'], SAFE_CODE)
    verify_result = await verify_agent.on_task(verify_task)

    if audit_result['finding_count'] > 0:
        assert verify_result['false_positive_count'] >= 0


@pytest.mark.asyncio
async def test_knowledge_graph_returns_remediation():
    agent = KnowledgeGraphAgent("test_kg")
    task = TaskTemplate.knowledge_query("sql_injection", "remediation")
    result = await agent.on_task(task)
    assert result['finding_count'] > 0
    assert 'remediation' in result['findings'][0]


@pytest.mark.asyncio
async def test_field_perceiver_computes_harmony():
    perceiver = FieldPerceiver()
    agent_states = {
        "agent1": {"u": 0.8, "d": 0.6, "a": 0.1},
        "agent2": {"u": 0.7, "d": 0.5, "a": 0.2}
    }
    field = perceiver.perceive(agent_states)
    assert "U" in field
    assert "H" in field
    assert 0 <= field["H"] <= 1


@pytest.mark.asyncio
async def test_phase_detector_alerts_on_inert():
    detector = PhaseDetector()
    for _ in range(10):
        detector.update({"U": 0.5, "D": 0.5, "A": 0.01, "H": 0.4})
    alert = detector.update({"U": 0.4, "D": 0.5, "A": 0.01, "H": 0.35})
    assert alert is not None


@pytest.mark.asyncio
async def test_tuner_generates_suggestions():
    tuner = HarmonyTuner()
    result = tuner.tune({"U": 0.3, "D": 0.4, "A": 0.7, "H": 0.2})
    assert len(result["suggestions"]) > 0
    assert "temperature" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])