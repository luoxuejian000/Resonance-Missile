# Resonance-Missile 跨框架测试数据交付包

> **工具理性悖论防护已内置** — 本交付包遵循晶脉哲学四重公理，所有数据格式均包含悖论防护声明。

## 一、文件清单

| 文件名 | 类型 | 大小 | 用途 |
|--------|------|------|------|
| `resonance_field_schema.json` | JSON Schema | ~3KB | 场域轨迹数据格式规范 |
| `resonance_audit_sample.json` | JSON | ~5KB | 示例审计输出（模拟真实审计） |
| `万象渊鉴·场域诊断测试集.txt` | TXT | ~15万字符 | 测试语料（6个场景，中英双语） |
| `test_b_output（星虫5）.txt` | TXT | 参考 | HeartFlow COT推理轨迹参考 |
| `html_report_generator.py` | Python | 工具 | HTML报告生成工具 |

## 二、数据格式规范

### 2.1 场域轨迹格式（resonance_field_schema.json）

核心字段说明：

| 字段 | 类型 | 范围 | 说明 |
|------|------|------|------|
| `step` | int | ≥1 | 采样步数 |
| `char_pos` | int | ≥0 | 字符位置 |
| `U` | float | 0-1 | 统一性（智能体观点一致性） |
| `D` | float | 0-1 | 发展性（知识增长速度） |
| `A` | float | 0-1 | 对抗性（矛盾分歧程度） |
| `H` | float | 0-1 | 和谐度（综合健康度） |
| `U_diff` | float | - | 统一性变化量 |
| `D_diff` | float | - | 发展性变化量 |
| `A_diff` | float | - | 对抗性变化量 |
| `H_diff` | float | - | 和谐度变化量 |
| `H_driven_by` | enum | U/D/A/均衡 | 主导驱动维度 |
| `cumul_A` | float | ≥0 | A值累积量 |
| `D_volatility` | float | ≥0 | D值波动率 |

### 2.2 审计输出格式（resonance_audit_sample.json）

核心结构：
- `version`: "1.0"
- `timestamp`: ISO 8601 格式
- `file`: 被审计文件名
- `paradox_safeguard`: 工具理性悖论防护声明
- `global_snapshot`: 全局 U/D/A/H 聚合值
- `agents`: 智能体输出数组（至少2个）
- `mediation_result`: 矛盾调解结果
- `tuning_suggestions`: 调谐建议
- `audit_trail`: 审计日志

## 三、建议的测试流程

### 3.1 基础测试（必做）

```bash
# 1. 验证 Schema 格式
python -c "import json; json.load(open('resonance_field_schema.json')); print('Schema OK')"

# 2. 验证示例审计输出
python -c "import json; json.load(open('resonance_audit_sample.json')); print('Audit Sample OK')"

# 3. 运行完整审计（启用 TAT）
python ../export_for_tat.py --enable-tat --enable-heartflow
```

### 3.2 场域诊断测试流程

```
步骤1: 加载测试语料（万象渊鉴·场域诊断测试集.txt）
步骤2: 逐场景运行审计，记录场域轨迹
步骤3: 提取 U/D/A/H 四维时序数据
步骤4: 验证 H_driven_by 判定逻辑
步骤5: 检查热度表（hits/scans）是否正确更新
步骤6: 验证审计日志完整性
```

### 3.3 跨框架一致性测试

| 测试项 | 验证方法 |
|--------|----------|
| 场域轨迹生成 | 对比各框架在相同输入下的 U/D/A/H 曲线 |
| 矛盾检测 | 使用包含预设矛盾的测试语料验证检测率 |
| 热度跟踪 | 检查 hits/scans 是否正确记录 |
| 悖论防护 | 验证建议冷却期和人工断点机制 |

## 四、各框架运行方式建议

### 4.1 Resonance-Missile（本框架）

```bash
# 安装依赖
pip install -r requirements.txt

# 运行完整审计
python export_for_tat.py --enable-tat --enable-heartflow

# 运行测试用例
python -m pytest tests/ -v
```

### 4.2 其他框架

**通用要求**：
- 输入：`万象渊鉴·场域诊断测试集.txt` 中的各场景文本
- 输出：符合 `resonance_field_schema.json` 格式的轨迹数据
- 报告：生成类似 `resonance_audit_sample.json` 的审计输出

**验证要点**：
1. U/D/A/H 维度定义是否一致
2. H_driven_by 判定逻辑是否合理
3. 热度计算是否使用 hits/scans 比值
4. 是否包含悖论防护声明

## 五、悖论防护机制说明

本交付包内置以下工具理性悖论防护机制：

1. **human_review_required_for_critical_findings** — 高危发现必须人工审批
2. **auto_execute_permanently_disabled** — 自动执行永久禁用（MAX_AUTO_FIX_ATTEMPTS=0）
3. **contradiction_escalation_instead_of_suppression** — 矛盾显化而非压制
4. **tat_consensus_subject_to_field_validation** — TAT共识需经过场域验证
5. **global_health_self_check_with_human_decision** — 全局健康自检需人工决策
6. **configurable_thresholds_with_audit_trail** — 可配置阈值并记录审计轨迹

## 六、交付确认

- ✅ JSON Schema 规范文档已生成
- ✅ 示例审计输出文件已生成
- ✅ 工具理性悖论防护声明已内置
- ✅ 所有文件使用 UTF-8 编码

## 七、联系方式

如有问题，请在 GitHub Issue #1470 中回复，或联系项目维护者。

---

**版权声明**: Copyright (c) 2026 李广好 (luoxuejian000) — Resonance-Missile 项目
**工具理性悖论防护已内置**