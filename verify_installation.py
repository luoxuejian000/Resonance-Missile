# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

#!/usr/bin/env python3
"""
安装验证脚本 —— 检查所有依赖和模块是否正常导入。
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verify_imports():
    modules = [
        "config",
        "core.message_types",
        "core.audit_logger",
        "hub",
        "agents.base_agent",
        "agents.code_audit_agent",
        "agents.verify_agent",
        "agents.knowledge_graph_agent",
        "agents.fuzz_test_agent",
        "agents.dependency_agent",
        "agents.scheduler",
        "resonance.field_perceiver",
        "resonance.phase_detector",
        "resonance.harmony_tuner",
        "dashboard.field_monitor",
        "tasks.task_queue",
        "tasks.human_approval",
        "tasks.templates",
        "sandbox.verify_sandbox",
        "sandbox.report_generator",
        "knowledge.sync_manager",
        "knowledge.security_policy",
        "integration.thinkcheck_adapter",
        "integration.task_generator",
        "stress_test.runner"
    ]

    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"  [OK] {module}")
        except ImportError as e:
            print(f"  [FAIL] {module}: {e}")
            failed.append(module)

    return failed


if __name__ == "__main__":
    print("=" * 50)
    print("  Resonance-Missile 安装验证")
    print("=" * 50)

    print(f"\nPython版本: {sys.version}")

    print("\n模块导入验证:")
    failed = verify_imports()

    print("\n" + "=" * 50)
    if failed:
        print(f"  [FAIL] 验证失败: {len(failed)} 个模块无法导入")
        print(f"  失败模块: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("  [OK] 所有模块验证通过！")
        print("  系统已准备就绪，可以运行 python main.py 启动。")
        sys.exit(0)