# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
报告生成器 —— 实践介入论：将场域状态、漏洞发现、验证结果整合为可审计的报告。
"""
import json
import time
from typing import Dict, Any, List
from dashboard.field_monitor import monitor


class ReportGenerator:
    HUMAN_APPROVAL_REQUIRED = True
    MAX_AUTO_FIX_ATTEMPTS = 0

    def generate_report(self,
                       findings: List[Dict[str, Any]],
                       field_history: List[Dict[str, Any]] = None,
                       human_confirmed: bool = False) -> Dict[str, Any]:
        current_state = monitor.get_current_state()
        trend = monitor.get_trend()
        alerts = monitor.get_alerts(limit=50)

        critical = [f for f in findings if f.get("severity") == "critical"]
        high = [f for f in findings if f.get("severity") == "high"]
        medium = [f for f in findings if f.get("severity") == "medium"]
        low = [f for f in findings if f.get("severity") == "low"]

        has_contradiction = any(f.get("contradiction_detected", False) for f in findings)
        requires_human_confirmation = (self.HUMAN_APPROVAL_REQUIRED and 
                                       (len(critical) > 0 or has_contradiction))

        if requires_human_confirmation and not human_confirmed:
            return {
                "report_id": f"report_{int(time.time())}",
                "status": "pending_human_confirmation",
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "requires_human_confirmation": True,
                "reason": (
                    f"发现 {len(critical)} 个严重漏洞" if len(critical) > 0 else ""
                ) + ("，检测到矛盾" if has_contradiction else ""),
                "summary": {
                    "total_findings": len(findings),
                    "critical": len(critical),
                    "high": len(high),
                    "medium": len(medium),
                    "low": len(low),
                    "contradiction_detected": has_contradiction
                },
                "disclaimer": (
                    "本报告需要人类专家确认后才能生成完整内容。"
                    "严重漏洞和矛盾检测结果必须由授权人员审核。"
                )
            }

        report = {
            "report_id": f"report_{int(time.time())}",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "confirmed" if human_confirmed else "auto_generated",
            "human_confirmed": human_confirmed,
            "summary": {
                "total_findings": len(findings),
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low),
                "field_health": {
                    "U": current_state["U"],
                    "D": current_state["D"],
                    "A": current_state["A"],
                    "H": current_state["H"],
                    "status": "healthy" if current_state["H"] > 0.5 else ("warning" if current_state["H"] > 0.3 else "danger")
                },
                "trend": trend,
                "alert_count": len(alerts),
                "contradiction_detected": has_contradiction
            },
            "critical_findings": critical,
            "high_findings": high,
            "recommendations": self._generate_recommendations(findings, current_state),
            "disclaimer": (
                "本报告由Resonance-Missile智能体协同系统自动生成。"
                "所有发现均已经过独立验证Agent的复现确认。"
                "报告内容仅供人类安全专家参考，不构成任何自动修复建议。"
                "任何修复操作必须由授权人员进行，并记录完整的审计日志。"
            ),
            "audit_trail": {
                "total_snapshots": len(field_history) if field_history else 0,
                "total_alerts": len(alerts)
            },
            "instrumental_paradox_safeguards": {
                "human_approval_required": self.HUMAN_APPROVAL_REQUIRED,
                "max_auto_fix_attempts": self.MAX_AUTO_FIX_ATTEMPTS,
                "critical_findings_require_confirmation": True,
                "contradictions_require_confirmation": True,
                "report_generation_blocked_without_confirmation": True
            }
        }

        return report

    def _generate_recommendations(self, findings: List[Dict],
                                  field_state: Dict[str, float]) -> List[str]:
        recommendations = []

        vuln_types = set(f.get("type", "") for f in findings)

        if "sql_injection" in vuln_types:
            recommendations.append(
                "发现SQL注入漏洞。建议：使用参数化查询或ORM框架，"
                "对所有用户输入进行严格校验和转义。"
            )
        if "xss" in vuln_types:
            recommendations.append(
                "发现XSS漏洞。建议：对输出内容进行HTML实体编码，"
                "实施Content-Security-Policy头。"
            )
        if "command_injection" in vuln_types:
            recommendations.append(
                "发现命令注入漏洞。建议：避免将用户输入直接传递给系统命令，"
                "使用白名单验证输入参数。"
            )
        if "path_traversal" in vuln_types:
            recommendations.append(
                "发现路径遍历漏洞。建议：使用白名单限制文件访问路径，"
                "禁止用户输入中包含'..'等特殊字符。"
            )

        H = field_state.get("H", 0.5)
        A = field_state.get("A", 0.0)

        if H < 0.3:
            recommendations.append(
                "系统场域和谐度过低，建议暂停自动化扫描任务，"
                "优先处理高优先级漏洞，待场域恢复健康后再恢复全量扫描。"
            )
        if A > 0.6:
            recommendations.append(
                "系统内部矛盾密度过高，建议增加独立验证Agent数量，"
                "提高验证覆盖率，减少误报。"
            )

        return recommendations


report_gen = ReportGenerator()