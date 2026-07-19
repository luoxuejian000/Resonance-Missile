# Resonance-Missile

## 中国版 Missile 漏洞挖掘系统 —— 基于晶脉哲学四重公理的智能体协同工程

### 项目定位

在国家关键基础设施防护领域，构建一套不依赖单一最强模型、具备自我感知与调谐能力的智能体协同漏洞挖掘系统。

### 设计哲学

从"对齐"到"调谐"，从"单体最强"到"群体谐振"。

### 理论根基

| 公理 | 工程实现 | 核心代码 |
|------|---------|---------|
| 关系本体论 | 漏洞危险度由它在系统拓扑中的位置决定 | `resonance/field_perceiver.py` |
| 矛盾动力论 | 智能体间的分歧是系统演化的驱动力 | `resonance/phase_detector.py` |
| 实践介入论 | 所有操作均可审计、可追溯 | `core/audit_logger.py` |
| 谐振调谐论 | 场域健康度H驱动协同策略调整 | `resonance/harmony_tuner.py` |

### 系统架构

```
[通信中枢 (Hub)] ←→ [协同调度器 (Orchestrator)]
    ↕                      ↕
[智能体集群]         [场域监控仪表盘]
├── 代码审计Agent    ├── U/D/A/H实时显示
├── 模糊测试Agent    ├── 历史趋势图
├── 知识图谱Agent    └── 翻转点告警
├── 验证Agent
└── 依赖分析Agent
```

### 快速启动

```bash
# Docker部署
docker-compose up -d

# 或手动启动
pip install -r requirements.txt
python main.py

# 运行演示
python run_demo.py

# 运行压力测试
python stress_test/runner.py

# 健康检查
python deploy/health_check.py
```

### 访问地址

- 通信中枢: ws://localhost:8000
- 仪表盘: http://localhost:8001

### 防范工具理性悖论

本系统内置五道防线：

1. **人机协同审批**：所有高危操作必须经人类审批
2. **透明审计**：所有决策携带完整场域快照
3. **能力边界硬限制**：沙箱严格限制网络和文件访问
4. **自我感知告警**：系统异常时自动暂停自动化任务
5. **价值锚点声明**：系统以保障人民生命财产安全为首要目标

### 项目结构

```
Resonance-Missile/
├── main.py                    # 主程序入口
├── run_demo.py                # 演示脚本
├── hub.py                     # 通信中枢
├── config.py                  # 配置管理
├── requirements.txt           # 依赖清单
├── agents/                    # 智能体模块
│   ├── base_agent.py          # 智能体基类
│   ├── scheduler.py           # 协同调度器
│   ├── code_audit_agent.py    # 代码审计智能体
│   ├── knowledge_graph_agent.py # 知识图谱智能体
│   ├── fuzz_test_agent.py     # 模糊测试智能体
│   ├── verify_agent.py        # 验证智能体
│   └── dependency_agent.py    # 依赖分析智能体
├── core/                      # 核心模块
│   ├── message_types.py       # 消息类型定义
│   └── audit_logger.py        # 审计日志模块
├── resonance/                 # 场域感知与调谐
│   ├── field_perceiver.py     # 场域感知器
│   ├── phase_detector.py      # 翻转点检测器
│   └── harmony_tuner.py       # 谐振调谐引擎
├── dashboard/                 # 场域监控仪表盘
│   ├── field_monitor.py       # 场域监控器
│   └── api.py                 # 仪表盘 API
├── tasks/                     # 任务管理
│   ├── task_queue.py          # 任务队列管理器
│   ├── human_approval.py      # 人类审批接口
│   └── templates.py           # 任务模板
├── sandbox/                   # 漏洞验证沙箱
│   ├── executor.py            # 沙箱执行器
│   ├── verify_sandbox.py      # 漏洞验证沙箱
│   └── report_generator.py    # 报告生成器
├── knowledge/                 # 知识库同步
│   ├── sync_manager.py        # 知识库同步管理器
│   ├── policy_manager.py      # 安全策略管理器
│   └── security_policy.py     # 安全策略配置
├── integration/               # 外部集成
│   ├── thinkcheck_adapter.py  # ThinkCheck适配器
│   └── task_generator.py      # 任务生成器
├── stress_test/               # 压力测试
│   └── runner.py              # 七重压力测试执行器
├── deploy/                    # 部署与运维
│   ├── deploy_guide.md        # 部署指南
│   ├── ops.py                 # 运维脚本
│   └── health_check.py        # 健康检查脚本
├── tests/                     # 测试用例
│   └── test_integration.py    # 集成测试
├── Dockerfile                 # Docker镜像配置
├── docker-compose.yml         # Docker Compose配置
└── .dockerignore              # Docker忽略文件
```

### 场域感知指标

| 指标 | 含义 | 范围 | 健康状态 |
|------|------|------|---------|
| U | 统一性 (Unity) | 0-1 | >0.5 健康 |
| D | 发展性 (Development) | 0-1 | >0.3 健康 |
| A | 对抗性 (Antagonism) | 0-1 | <0.5 健康 |
| H | 和谐度 (Harmony) | 0-1 | >0.5 健康 |

### 安全配置

生产环境必须设置：

```env
HUMAN_APPROVAL_REQUIRED=true
LOG_LEVEL=INFO
```
## 🛒 产品超市（并排放置）

以下框架均已在 #1466 跨框架验证中独立验证。它们各自解决不同的问题，彼此独立，互不隶属。选择哪个取决于你的场景，而不是谁的“更好”。

| 框架 | 一句话定位 | 适用场景 | 框架主 |
|------|-----------|---------|--------|
| **HeartFlow** | 前置决策审计 | 企业安全、AI审计平台 | yun520-1 |
| **TAT-7** | 实时分歧追踪 | 可观测性平台、Agent监控 | Marat Sultanov |
| **Cophy** | 跨会话因果密度 | 长期Agent、记忆系统 | icophy |
| **Agora/mnemo** | 存储基底、可审计存储 | 合规审计、数据溯源 | DanceNitra |
| **TLAA** | G0-G4分层审计 | 安全审计、合规团队 | YING-SHI-XI |
| **协调叙事** | 跨框架梳理、时间轴定位 | 技术文档、协作方法论 | qingkong66 |
| **U/D/A/H** | 场域诊断、四维轨迹追踪 | AI系统健康监测 | 李广好 |

> 本列表不做排序，不设评分，无“推荐”。判断权在观察者手中。
### 许可证

Apache 2.0
