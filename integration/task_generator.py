# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
任务生成器 —— 谐振调谐论：根据场域状态自动生成最优任务序列。
注意：只生成任务建议，不自动执行。
"""
from typing import Dict, Any, List
from tasks.templates import TaskTemplate


class TaskGenerator:
    def generate_tasks(self, field_state: Dict[str, float],
                       available_code: Dict[str, str] = None) -> List[Dict[str, Any]]:
        tasks = []
        U = field_state.get("U", 0.5)
        D = field_state.get("D", 0.5)
        A = field_state.get("A", 0.0)
        H = field_state.get("H", 0.5)

        if U < 0.4:
            tasks.append({
                "priority": 9,
                "reason": "统一性过低，建议执行独立验证",
                "task_template": "verify_findings",
                "task_type": "cross_check"
            })

        if A > 0.5:
            tasks.append({
                "priority": 8,
                "reason": "对抗性过高，建议扩大扫描范围",
                "task_template": "code_audit",
                "task_type": "static_analysis"
            })

        if D < 0.3:
            tasks.append({
                "priority": 7,
                "reason": "发展性不足，建议启动模糊测试",
                "task_template": "fuzz_test",
                "task_type": "input_fuzzing"
            })

        if H > 0.5:
            tasks.append({
                "priority": 5,
                "reason": "场域健康，执行常规审计",
                "task_template": "code_audit",
                "task_type": "static_analysis"
            })
            tasks.append({
                "priority": 4,
                "reason": "场域健康，更新依赖检查",
                "task_template": "dependency_check",
                "task_type": "version_check"
            })

        return sorted(tasks, key=lambda x: x["priority"], reverse=True)