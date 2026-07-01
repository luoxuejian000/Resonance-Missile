# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

#!/usr/bin/env python3
"""
Resonance-Missile 主程序入口
=============================
启动顺序：
1. 通信中枢 (Hub)
2. 协同调度器 (Orchestrator)
3. 各智能体 (Agents)
4. 场域监控仪表盘 (Dashboard)

基于晶脉哲学四重公理构建。
防范工具理性悖论：所有自动操作必须经人类审批。
"""
import asyncio
import sys
import os

from hub import start_hub
from agents.scheduler import Orchestrator
from agents.code_audit_agent import CodeAuditAgent
from agents.knowledge_graph_agent import KnowledgeGraphAgent
from agents.fuzz_test_agent import FuzzTestAgent
from agents.verify_agent import VerifyAgent
from agents.dependency_agent import DependencyAgent
from dashboard.field_monitor import monitor
from dashboard.api import app as dashboard_app
from config import settings


async def main():
    print("=" * 60)
    print("  Resonance-Missile 系统启动")
    print("  基于晶脉哲学四重公理构建")
    print("=" * 60)

    print("\n[1/5] 启动通信中枢...")
    hub_task = asyncio.create_task(asyncio.to_thread(start_hub))
    await asyncio.sleep(1)

    print("[2/5] 启动协同调度器...")
    orchestrator = Orchestrator()

    print("[3/5] 启动智能体集群...")
    agents = [
        CodeAuditAgent("code_audit_001"),
        CodeAuditAgent("code_audit_002"),
        KnowledgeGraphAgent("knowledge_graph_001"),
        FuzzTestAgent("fuzz_test_001"),
        VerifyAgent("verify_001"),
        DependencyAgent("dependency_001")
    ]

    agent_tasks = []
    for agent in agents:
        task = asyncio.create_task(agent.run())
        agent_tasks.append(task)
    await asyncio.sleep(2)

    print("[4/5] 启动场域监控仪表盘...")
    import uvicorn
    dashboard_config = uvicorn.Config(dashboard_app, host="0.0.0.0", port=8001, log_level="info")
    dashboard_server = uvicorn.Server(dashboard_config)
    dashboard_task = asyncio.create_task(dashboard_server.serve())
    await asyncio.sleep(1)

    print("[5/5] 连接调度器...")
    orchestrator_task = asyncio.create_task(orchestrator.run())

    print("\n" + "=" * 60)
    print("  [OK] 所有组件已启动")
    print(f"  通信中枢: ws://{settings.hub_host}:{settings.hub_port}")
    print(f"  仪表盘: http://localhost:8001")
    print(f"  智能体数量: {len(agents)}")
    print("=" * 60)
    print("\n按 Ctrl+C 停止系统\n")

    try:
        await asyncio.gather(
            orchestrator_task,
            dashboard_task,
            *agent_tasks,
            hub_task
        )
    except KeyboardInterrupt:
        print("\n正在停止系统...")
        for agent in agents:
            agent.running = False
        dashboard_server.should_exit = True
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())