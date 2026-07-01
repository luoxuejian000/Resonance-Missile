# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
知识库同步管理器 —— 从外部源同步最新的漏洞情报。
防范工具理性悖论：同步的数据只用于增强感知，不自动触发修复。
"""
import json
import time
import os
from typing import Dict, Any, List, Optional


class KnowledgeSyncManager:
    def __init__(self, local_db_path: str = "knowledge_base.json"):
        self.local_db_path = local_db_path
        self.local_db = self._load_local_db()
        self.sync_history: List[Dict[str, Any]] = []

    def _load_local_db(self) -> Dict[str, Any]:
        if os.path.exists(self.local_db_path):
            with open(self.local_db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "version": "1.0",
            "last_updated": None,
            "vulnerabilities": {},
            "attack_patterns": {},
            "remediations": {}
        }

    def _save_local_db(self):
        self.local_db["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.local_db_path, "w", encoding="utf-8") as f:
            json.dump(self.local_db, f, indent=2, ensure_ascii=False)

    def sync_from_cve(self, cve_data: List[Dict[str, Any]]) -> Dict[str, int]:
        added = 0
        updated = 0

        for entry in cve_data:
            cve_id = entry.get("cve_id", "")
            if not cve_id:
                continue

            vuln_info = {
                "cve_id": cve_id,
                "description": entry.get("description", ""),
                "severity": entry.get("severity", "medium"),
                "cvss_score": entry.get("cvss_score", 0.0),
                "affected_products": entry.get("affected_products", []),
                "remediation": entry.get("remediation", ""),
                "synced_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            if cve_id in self.local_db["vulnerabilities"]:
                self.local_db["vulnerabilities"][cve_id].update(vuln_info)
                updated += 1
            else:
                self.local_db["vulnerabilities"][cve_id] = vuln_info
                added += 1

        self._save_local_db()
        self.sync_history.append({
            "time": time.time(),
            "source": "CVE",
            "added": added,
            "updated": updated
        })

        return {"added": added, "updated": updated}

    def sync_from_attack_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, int]:
        added = 0
        for pattern in patterns:
            pattern_id = pattern.get("pattern_id", "")
            if pattern_id and pattern_id not in self.local_db["attack_patterns"]:
                self.local_db["attack_patterns"][pattern_id] = pattern
                added += 1

        self._save_local_db()
        return {"added": added, "updated": 0}

    def query_vulnerability(self, keyword: str) -> List[Dict[str, Any]]:
        results = []
        keyword_lower = keyword.lower()

        for cve_id, info in self.local_db["vulnerabilities"].items():
            if (keyword_lower in cve_id.lower() or
                keyword_lower in info.get("description", "").lower()):
                results.append(info)

        return results

    def query_remediation(self, vuln_type: str) -> Optional[str]:
        return self.local_db["remediations"].get(vuln_type)