# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
安全策略管理器 —— 定义系统的安全扫描策略和规则。
"""
import json
import os
from typing import Dict, Any, List


class PolicyManager:
    def __init__(self, policy_path: str = "security_policy.json"):
        self.policy_path = policy_path
        self.policies = self._load_policies()

    def _load_policies(self) -> Dict[str, Any]:
        if os.path.exists(self.policy_path):
            with open(self.policy_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._get_default_policies()

    def _get_default_policies(self) -> Dict[str, Any]:
        return {
            "version": "1.0",
            "scan_depth": {
                "quick": {"max_files": 100, "timeout": 60},
                "normal": {"max_files": 1000, "timeout": 300},
                "deep": {"max_files": 5000, "timeout": 1800}
            },
            "severity_threshold": {
                "auto_verify": ["critical", "high"],
                "human_approval_required": ["critical", "high"],
                "ignore_types": []
            },
            "scan_rules": {
                "sql_injection": {"enabled": True, "patterns": ["' OR", "1=1", "UNION SELECT"]},
                "xss": {"enabled": True, "patterns": ["<script>", "onerror=", "javascript:"]},
                "command_injection": {"enabled": True, "patterns": [";", "|", "&&", "$("]},
                "path_traversal": {"enabled": True, "patterns": ["../", "..\\", "%2e%2e"]},
                "buffer_overflow": {"enabled": False, "patterns": []},
                "authentication_bypass": {"enabled": True, "patterns": ["admin'--", "OR 1=1"]}
            },
            "rate_limits": {
                "max_scans_per_minute": 10,
                "max_concurrent_scans": 5,
                "cooldown_period_seconds": 60
            },
            "data_retention": {
                "scan_results_days": 30,
                "audit_logs_days": 90,
                "field_snapshots_days": 7
            },
            "notification_rules": {
                "critical_vulnerability": {"slack": True, "email": True, "sms": False},
                "field_health_warning": {"slack": True, "email": False, "sms": False},
                "system_error": {"slack": True, "email": True, "sms": True}
            }
        }

    def save_policies(self):
        with open(self.policy_path, "w", encoding="utf-8") as f:
            json.dump(self.policies, f, indent=2, ensure_ascii=False)

    def get_scan_config(self, mode: str = "normal") -> Dict[str, Any]:
        return self.policies.get("scan_depth", {}).get(mode, self.policies["scan_depth"]["normal"])

    def should_auto_verify(self, severity: str) -> bool:
        return severity in self.policies.get("severity_threshold", {}).get("auto_verify", [])

    def requires_human_approval(self, severity: str) -> bool:
        return severity in self.policies.get("severity_threshold", {}).get("human_approval_required", [])

    def is_rule_enabled(self, rule_type: str) -> bool:
        return self.policies.get("scan_rules", {}).get(rule_type, {}).get("enabled", False)

    def get_rule_patterns(self, rule_type: str) -> List[str]:
        return self.policies.get("scan_rules", {}).get(rule_type, {}).get("patterns", [])

    def update_policy(self, section: str, key: str, value: Any):
        if section in self.policies:
            self.policies[section][key] = value
            self.save_policies()


if __name__ == "__main__":
    pm = PolicyManager()
    print("PolicyManager initialized")
    print("Scan config:", pm.get_scan_config("quick"))
    print("Auto verify critical:", pm.should_auto_verify("critical"))
    print("SQL injection enabled:", pm.is_rule_enabled("sql_injection"))