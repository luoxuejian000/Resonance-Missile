# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

#!/usr/bin/env python3
"""
Resonance-Missile 演示脚本
===========================
模拟一次完整的漏洞挖掘协同过程，展示多智能体协同和场域调谐。
"""
import asyncio
import json
import time
from agents.scheduler import Orchestrator
from agents.code_audit_agent import CodeAuditAgent
from agents.verify_agent import VerifyAgent
from agents.knowledge_graph_agent import KnowledgeGraphAgent
from dashboard.field_monitor import monitor
from config import settings


SAMPLE_CODE_SQL_INJECTION = """
def get_user(username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return database.execute(query)

def login(username, password):
    sql = f"SELECT * FROM users WHERE user='{username}' AND pass='{password}'"
    result = db.rawQuery(sql)
    return result
"""


SAMPLE_CODE_XSS = """
function displayMessage(msg) {
    document.getElementById('output').innerHTML = msg;
}

function processInput() {
    var userInput = document.getElementById('input').value;
    eval("processData(" + userInput + ")");
}
"""


async def demo():
    print("=" * 60)
    print("  Resonance-Missile 协同漏洞挖掘演示")
    print("  基于晶脉哲学四重公理")
    print("=" * 60)

    audit_agent = CodeAuditAgent("demo_audit")
    verify_agent = VerifyAgent("demo_verify")
    knowledge_agent = KnowledgeGraphAgent("demo_knowledge")

    print("\n[TASK] 任务1：对SQL注入样本进行静态审计")
    task1 = {
        "task_type": "static_analysis",
        "code": SAMPLE_CODE_SQL_INJECTION,
        "requires_approval": False
    }
    result1 = await audit_agent.on_task(task1)
    print(f"  发现漏洞数: {result1['finding_count']}")
    print(f"  置信度: {result1['confidence']:.2f}")
    for finding in result1['findings']:
        print(f"  - {finding['type']} (行 {finding['line']}): {finding['content'][:60]}...")

    monitor.record_snapshot(
        {"U": result1['field']['u'], "D": result1['field']['d'],
         "A": result1['field']['a'], "H": result1['field']['h']},
        agent_count=1, task_count=1
    )

    print("\n[TASK] 任务2：验证Agent独立复现审计结果")
    task2 = {
        "task_type": "reproduce",
        "findings": result1['findings'],
        "code": SAMPLE_CODE_SQL_INJECTION
    }
    result2 = await verify_agent.on_task(task2)
    print(f"  验证通过: {result2['verified_count']}")
    print(f"  误报数: {result2['false_positive_count']}")
    if result2['false_positives']:
        for fp in result2['false_positives']:
            print(f"  - 误报: {fp.get('type', 'unknown')} - {fp.get('reason', '')}")

    has_contradiction = result2['false_positive_count'] > 0
    monitor.record_snapshot(
        {"U": 0.7 if not has_contradiction else 0.4,
         "D": 0.5, "A": 0.8 if has_contradiction else 0.1,
         "H": 0.5 if not has_contradiction else 0.2},
        agent_count=2, task_count=2
    )

    print("\n[TASK] 任务3：查询SQL注入的CVE和修复方案")
    task3 = {
        "task_type": "remediation",
        "query": "sql_injection"
    }
    result3 = await knowledge_agent.on_task(task3)
    print(f"  查询结果数: {result3['finding_count']}")
    for finding in result3['findings']:
        print(f"  - {finding['vuln_type']}: {finding.get('remediation', finding.get('cve_list', []))}")

    print("\n" + "=" * 60)
    current_state = monitor.get_current_state()
    print(f"  最终场域状态:")
    print(f"  U (统一性): {current_state['U']:.2f}")
    print(f"  D (发展性): {current_state['D']:.2f}")
    print(f"  A (对抗性): {current_state['A']:.2f}")
    print(f"  H (和谐度): {current_state['H']:.2f}")
    print(f"  智能体数: {current_state['agent_count']}")
    print(f"  任务数: {current_state['task_count']}")

    trend = monitor.get_trend()
    print(f"  趋势: U={trend['U']}, D={trend['D']}, A={trend['A']}, H={trend['H']}")

    print("\n" + "=" * 60)
    print("  演示完成。")
    print("  完整的协同调度请运行 main.py")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo())