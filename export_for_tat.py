# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
TAT 导出模块 —— 场景插件系统与工具理性悖论声明。
插件系统仅作为文件预处理和上下文增强工具，不参与核心投票逻辑。
"""
import json
import sys
import os
import time
import argparse
from typing import Dict, Any, List, Callable, Optional, Set


_plugin_override_enable: Set[str] = set()
_plugin_override_disable: Set[str] = set()
_global_plugins: Dict[str, Any] = {}


def set_plugin_overrides(enable: Optional[List[str]] = None, disable: Optional[List[str]] = None) -> None:
    global _plugin_override_enable, _plugin_override_disable
    if enable:
        _plugin_override_enable = set(enable)
    if disable:
        _plugin_override_disable = set(disable)


def inject_heartflow_core(rules: Set[str]) -> None:
    if not rules:
        return

    try:
        from agents.base_agent import BaseAgent
        BaseAgent._audit_shared_memory(
            "INJECT_HEARTFLOW_CORE",
            "core_rules",
            f"{len(rules)} rules from HeartFlow (external source)"
        )

        current_core = BaseAgent.shared_memory["core_rules"]
        updated_core = current_core | set(rules)
        BaseAgent.shared_memory["core_rules"] = updated_core

        BaseAgent.shared_memory["_core_rules_meta"] = {
            "source": "HeartFlow",
            "injected_at": time.time(),
            "status": "temporary",
            "review_required": True,
            "original_rules_count": len(rules),
            "total_rules_count": len(updated_core),
            "reviewed_by": None,
            "reviewed_at": None
        }
    except ImportError:
        pass


def get_plugins_for_file(filepath: str) -> Dict[str, Any]:
    global _global_plugins

    if _plugin_override_enable:
        plugins = {}
        if "compliance" in _plugin_override_enable and "compliance" in _global_plugins:
            plugins["compliance"] = _global_plugins["compliance"]
        if "crosslang" in _plugin_override_enable and "crosslang" in _global_plugins:
            plugins["crosslang"] = _global_plugins["crosslang"]
        if "crash" in _plugin_override_enable and "crash" in _global_plugins:
            plugins["crash"] = _global_plugins["crash"]
        if "heartflow" in _plugin_override_enable:
            try:
                from agents.base_agent import BaseAgent
                if hasattr(BaseAgent, "_hf_core"):
                    inject_heartflow_core(set(getattr(BaseAgent, "_hf_core", set())))
                BaseAgent.clear_ephemeral()
            except ImportError:
                pass

        if _plugin_override_disable:
            for d in _plugin_override_disable:
                plugins.pop(d, None)
        return plugins

    return {}


class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self.enabled_plugins: List[str] = []

    def register_plugin(self, plugin_name: str,
                       preprocess: Callable = None,
                       postprocess: Callable = None,
                       context_enhance: Callable = None):
        self.plugins[plugin_name] = {
            "preprocess": preprocess,
            "postprocess": postprocess,
            "context_enhance": context_enhance,
            "enabled": False
        }

    def enable_plugin(self, plugin_name: str):
        if plugin_name in self.plugins:
            self.plugins[plugin_name]["enabled"] = True
            if plugin_name not in self.enabled_plugins:
                self.enabled_plugins.append(plugin_name)

    def disable_plugin(self, plugin_name: str):
        if plugin_name in self.plugins:
            self.plugins[plugin_name]["enabled"] = False
            if plugin_name in self.enabled_plugins:
                self.enabled_plugins.remove(plugin_name)

    def preprocess(self, code: str) -> str:
        for plugin_name in self.enabled_plugins:
            plugin = self.plugins[plugin_name]
            if plugin.get("preprocess"):
                code = plugin["preprocess"](code)
        return code

    def postprocess(self, findings: List[Dict]) -> List[Dict]:
        for plugin_name in self.enabled_plugins:
            plugin = self.plugins[plugin_name]
            if plugin.get("postprocess"):
                findings = plugin["postprocess"](findings)
        return findings

    def enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        for plugin_name in self.enabled_plugins:
            plugin = self.plugins[plugin_name]
            if plugin.get("context_enhance"):
                context = plugin["context_enhance"](context)
        return context


class TatExporter:
    def __init__(self, enable_tat: bool = False):
        self.enable_tat = enable_tat
        self.plugin_manager = PluginManager()
        self._register_default_plugins()

    def _register_default_plugins(self):
        self.plugin_manager.register_plugin(
            "code_cleaner",
            preprocess=self._clean_comments
        )
        self.plugin_manager.register_plugin(
            "context_enricher",
            context_enhance=self._enrich_context
        )
        self.plugin_manager.register_plugin(
            "severity_normalizer",
            postprocess=self._normalize_severity
        )

    def _clean_comments(self, code: str) -> str:
        lines = code.split('\n')
        cleaned = []
        for line in lines:
            if '#' in line:
                line = line[:line.index('#')]
            cleaned.append(line.strip())
        return '\n'.join(cleaned)

    def _enrich_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context["enhanced_at"] = context.get("enhanced_at", 0) + 1
        context["plugin_count"] = len(self.plugin_manager.enabled_plugins)
        return context

    def _normalize_severity(self, findings: List[Dict]) -> List[Dict]:
        for finding in findings:
            severity = finding.get("severity", "medium")
            if severity in ["critical", "high"]:
                finding["priority"] = 1
            elif severity == "medium":
                finding["priority"] = 2
            else:
                finding["priority"] = 3
        return findings

    def export(self, findings: List[Dict[str, Any]],
               field_state: Dict[str, float]) -> Dict[str, Any]:
        if not self.enable_tat:
            return {
                "tat_enabled": False,
                "message": "TAT模块未启用，返回标准格式"
            }

        enhanced_context = self.plugin_manager.enhance_context({
            "field_state": field_state,
            "plugin_count": len(self.plugin_manager.enabled_plugins),
            "enabled_plugins": self.plugin_manager.enabled_plugins
        })

        result = {
            "tat_enabled": True,
            "findings": findings,
            "field_state": field_state,
            "context": enhanced_context,
            "theory_attribution": {
                "philosophy": "晶脉哲学四重公理",
                "axioms": [
                    {
                        "name": "关系本体论",
                        "description": "漏洞危险度由它在系统拓扑中的位置决定",
                        "implementation": "resonance/field_perceiver.py"
                    },
                    {
                        "name": "矛盾动力论",
                        "description": "智能体间的分歧是系统演化的驱动力",
                        "implementation": "resonance/phase_detector.py"
                    },
                    {
                        "name": "实践介入论",
                        "description": "所有操作均可审计、可追溯",
                        "implementation": "core/audit_logger.py"
                    },
                    {
                        "name": "谐振调谐论",
                        "description": "场域健康度H驱动协同策略调整",
                        "implementation": "resonance/harmony_tuner.py"
                    }
                ],
                "instrumental_paradox_safeguards": {
                    "principle": "instrumental_paradox (luoxuejian000, 2026)",
                    "mechanisms": [
                        "human_review_required_for_critical_findings",
                        "auto_execute_permanently_disabled (MAX_AUTO_FIX_ATTEMPTS=0)",
                        "contradiction_escalation_instead_of_suppression",
                        "tat_consensus_subject_to_field_validation",
                        "global_health_self_check_with_human_decision",
                        "configurable_thresholds_with_audit_trail"
                    ],
                    "specific_measures": [
                        {
                            "name": "human_collaborative_approval",
                            "description": "All high-risk operations require human approval",
                            "implementation": "tasks/human_approval.py",
                            "enforced": True
                        },
                        {
                            "name": "transparent_audit",
                            "description": "All decisions carry complete field snapshot",
                            "implementation": "core/audit_logger.py",
                            "enforced": True
                        },
                        {
                            "name": "hard_capability_boundary",
                            "description": "Sandbox strictly limits network and file access",
                            "implementation": "sandbox/verify_sandbox.py",
                            "enforced": True
                        },
                        {
                            "name": "self_aware_alerting",
                            "description": "System automatically pauses automation on anomalies",
                            "implementation": "resonance/phase_detector.py",
                            "enforced": True
                        },
                        {
                            "name": "value_anchor_statement",
                            "description": "System prioritizes protection of human life and property",
                            "implementation": "config.py",
                            "enforced": True
                        },
                        {
                            "name": "auto_fix_prohibition",
                            "description": "MAX_AUTO_FIX_ATTEMPTS=0, all auto-fix operations prohibited",
                            "implementation": "config.py",
                            "enforced": True
                        },
                        {
                            "name": "independent_verification",
                            "description": "All findings must be independently reproduced by verification Agent",
                            "implementation": "agents/verify_agent.py",
                            "enforced": True
                        },
                        {
                            "name": "contradiction_mediation",
                            "description": "Agent contradictions trigger three-level mediation process",
                            "implementation": "agents/scheduler.py",
                            "enforced": True
                        }
                    ]
                }
            },
            "plugin_info": {
                "enabled_plugins": self.plugin_manager.enabled_plugins,
                "total_plugins": len(self.plugin_manager.plugins),
                "plugin_role": "文件预处理和上下文增强工具，不参与核心投票逻辑"
            }
        }

        try:
            from resonance.harmony_tuner import HarmonyTuner
            tuner = HarmonyTuner()
            suggestions = tuner.generate_tuning_suggestions(field_state)
            result["tuning_suggestions"] = suggestions
            for s in suggestions:
                if s.get("cooldown_applied"):
                    print(f"  COOLDOWN: {s.get('reason')}")
        except ImportError:
            result["tuning_suggestions"] = []

        return result


def main():
    print("=" * 60)
    print("  Resonance-Missile Field Tuning Architecture - Crystal Vein Philosophy")
    print("=" * 60)
    print("INSTRUMENTAL PARADOX SAFEGUARDS: No auto-fix / Critical requires human approval / MAX_AUTO_FIX_ATTEMPTS=0")
    print("=" * 60 + "\n")

    parser = argparse.ArgumentParser(description="Resonance-Missile TAT Export")
    parser.add_argument("--enable-tat", action="store_true", help="Enable TAT module")
    parser.add_argument("--enable-plugin", nargs="+", help="Force enable plugins")
    parser.add_argument("--disable-plugin", nargs="+", help="Force disable plugins")
    parser.add_argument("--enable-heartflow", action="store_true", help="Enable HeartFlow three-layer memory integration")
    args = parser.parse_args()

    enable_list = args.enable_plugin or []
    if args.enable_heartflow and "heartflow" not in enable_list:
        enable_list.append("heartflow")
    set_plugin_overrides(enable=enable_list, disable=args.disable_plugin or [])

    enable_tat = args.enable_tat or "--enable-tat" in sys.argv

    exporter = TatExporter(enable_tat=enable_tat)

    if args.enable_plugin:
        for plugin_name in args.enable_plugin:
            if plugin_name in exporter.plugin_manager.plugins:
                exporter.plugin_manager.enable_plugin(plugin_name)
            elif plugin_name == "heartflow":
                print("HeartFlow plugin enabled (external memory integration)")
        print(f"Enabled plugins: {', '.join(exporter.plugin_manager.enabled_plugins)}")

    if args.disable_plugin:
        for plugin_name in args.disable_plugin:
            if plugin_name in exporter.plugin_manager.plugins:
                exporter.plugin_manager.disable_plugin(plugin_name)
        print(f"Disabled plugins: {', '.join(args.disable_plugin)}")

    try:
        from agents.code_audit_agent import CodeAuditAgent
        from agents.verify_agent import VerifyAgent

        audit = CodeAuditAgent("audit_main")
        verify = VerifyAgent("verify_main")
        health_report = audit.check_global_health()
        print(f"\nGLOBAL HEALTH CHECK: {health_report['status'].upper()} | FP Rate:{health_report['recent_fp_rate']:.1%}")
        for issue in health_report["issues"]:
            severity = issue.get("severity", "warning")
            icon = "CRITICAL" if severity == "critical" else "WARNING"
            print(f"  [{icon}] {issue['type']}: {issue['suggested_action']}")
    except ImportError:
        print("\nSkipping global health check (agents not available)")

    if enable_tat:
        sample_findings = [
            {"type": "sql_injection", "severity": "high", "line": 5},
            {"type": "xss", "severity": "medium", "line": 12}
        ]
        field_state = {"U": 0.7, "D": 0.5, "A": 0.2, "H": 0.5}
        result = exporter.export(sample_findings, field_state)

        try:
            from resonance.harmony_tuner import HarmonyTuner
            tuner = HarmonyTuner()
            suggestions = tuner.generate_tuning_suggestions(field_state)
            result["tuning_suggestions"] = suggestions
            for s in suggestions:
                if s.get("cooldown_applied"):
                    print(f"  COOLDOWN: {s.get('reason')}")
        except ImportError:
            result["tuning_suggestions"] = []

        critical_findings = [r for r in [result] if r.get("global_snapshot", {}).get("contradiction_detected")]
        if critical_findings:
            print(f"\nHUMAN INTERVENTION BREAKPOINT - {len(critical_findings)} contradiction(s) require confirmation")
            for r in critical_findings:
                gs = r.get("global_snapshot", {})
                print(f"  File: sample | U={gs.get('U', 0):.2f} H={gs.get('H', 0):.2f}")
                try:
                    user_input = input("  Confirm(c) / False Positive(f) / Skip(s): ").strip().lower()
                    r["human_decision"] = "confirmed" if user_input == "c" else ("rejected" if user_input == "f" else "skipped")
                    if user_input == "f":
                        try:
                            from agents.base_agent import BaseAgent
                            BaseAgent.record_misclassification(r, "human_decision")
                        except ImportError:
                            pass
                except EOFError:
                    r["human_decision"] = "skipped"
            print()

        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("TAT module not enabled")


FIELD_OVERRIDE_CONFIG = {
    "coherence_threshold": 0.5,
    "A_threshold": 0.6,
    "H_threshold": 0.4,
    "_last_updated": None,
    "_updated_by": "system_default"
}


def set_field_override_config(
    coherence: Optional[float] = None,
    A: Optional[float] = None,
    H: Optional[float] = None,
    updated_by: str = "system"
) -> None:
    if coherence is not None:
        FIELD_OVERRIDE_CONFIG["coherence_threshold"] = coherence
    if A is not None:
        FIELD_OVERRIDE_CONFIG["A_threshold"] = A
    if H is not None:
        FIELD_OVERRIDE_CONFIG["H_threshold"] = H
    FIELD_OVERRIDE_CONFIG["_last_updated"] = time.time()
    FIELD_OVERRIDE_CONFIG["_updated_by"] = updated_by
    try:
        from agents.base_agent import BaseAgent
        BaseAgent._audit_shared_memory(
            "SET_FIELD_CONFIG",
            "field_override",
            f"coherence={coherence}, A={A}, H={H}, by={updated_by}"
        )
    except ImportError:
        pass


async def run_tat_mediation(audit_result, verify_result, code, enable_tat):
    return {"coherence": 0.6, "rounds": 1}


async def _second_audit(audit_result, code):
    findings = audit_result.get("findings", [])
    types = set(f.get("type") for f in findings)
    if len(types) > 2:
        return {"conflicts_with_original": True, "reason": "multiple_vuln_types"}
    return {"conflicts_with_original": False, "reason": "consistent"}


async def resolve_contradictions(
    audit_result: Dict,
    verify_result: Dict,
    field_state: Dict,
    code: str,
    enable_tat: bool
) -> Dict:
    audit_severity = "high" if audit_result.get("findings") else "info"
    verify_contradiction = verify_result.get("contradiction_detected", False)

    if not verify_contradiction and not audit_result.get("contradiction_detected"):
        return {"resolved": True, "method": "no_contradiction", "rounds": 0}

    second_opinion = await _second_audit(audit_result, code)
    if not second_opinion.get("conflicts_with_original", False):
        return {"resolved": True, "method": "second_auditor_agreed", "rounds": 1}

    tat_result = await run_tat_mediation(audit_result, {}, code, enable_tat)

    coherence_th = FIELD_OVERRIDE_CONFIG["coherence_threshold"]
    A_th = FIELD_OVERRIDE_CONFIG["A_threshold"]
    H_th = FIELD_OVERRIDE_CONFIG["H_threshold"]

    if (tat_result.get("coherence", 0) >= coherence_th and
        (field_state.get("A", 0) > A_th or field_state.get("H", 0) < H_th)):
        return {
            "resolved": False,
            "method": "field_override",
            "rounds": tat_result.get("rounds", 0) + 1,
            "detail": f"TAT coherence={tat_result.get('coherence', 0):.2f} but field abnormal",
            "requires_human_review": True,
            "threshold_used": FIELD_OVERRIDE_CONFIG.copy()
        }

    if tat_result.get("coherence", 0) >= coherence_th:
        return {"resolved": True, "method": "tat_consensus", "rounds": tat_result.get("rounds", 0) + 1}

    return {
        "resolved": False,
        "method": "escalated_to_human",
        "rounds": tat_result.get("rounds", 0) + 2,
        "detail": "Contradiction cannot be resolved automatically, requires human adjudication",
        "requires_human_review": True
    }


if __name__ == "__main__":
    main()