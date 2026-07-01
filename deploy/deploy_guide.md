# Resonance-Missile 部署指南

## 系统要求

- Python 3.11+
- 内存：最低 2GB，推荐 8GB+
- 磁盘：1GB 可用空间（不含知识库数据）
- 操作系统：Linux (推荐) / macOS / Windows

## 快速部署（Docker）

1. 安装 Docker 和 Docker Compose
2. 克隆或复制项目文件到服务器
3. 在项目根目录执行：
   ```bash
   docker-compose up -d
   ```

4. 访问服务：
   - 仪表盘：http://localhost:8001
   - Hub API：http://localhost:8000

## 手动部署（Python 虚拟环境）

### 步骤 1：创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 步骤 2：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 3：配置环境变量

编辑 `.env` 文件：

```env
HUB_HOST=0.0.0.0
HUB_PORT=8000
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
HUMAN_APPROVAL_REQUIRED=true
MAX_AUTO_FIX_ATTEMPTS=0
```

### 步骤 4：启动服务

```bash
# 启动通信中枢
python -c "from hub import start_hub; start_hub()"

# 启动调度器（新终端）
python -c "import asyncio; from agents.scheduler import Orchestrator; asyncio.run(Orchestrator().run())"

# 启动仪表盘（新终端）
python -m uvicorn dashboard.api:app --host 0.0.0.0 --port 8001
```

## 生产环境部署

### Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Systemd 服务配置

创建 `/etc/systemd/system/resonance-missile.service`：

```ini
[Unit]
Description=Resonance-Missile Security System
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
ExecStart=/path/to/project/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
systemctl daemon-reload
systemctl enable resonance-missile
systemctl start resonance-missile
```

## 运维命令

### 查看日志

```bash
# Docker 部署
docker-compose logs -f

# Systemd 部署
journalctl -u resonance-missile -f
```

### 重启服务

```bash
# Docker 部署
docker-compose restart

# Systemd 部署
systemctl restart resonance-missile
```

### 运行测试

```bash
python -m pytest tests/test_integration.py -v
```

### 运行压力测试

```bash
python stress_test/runner.py
```

## 安全注意事项

1. **禁止公开暴露 Hub 端口**：8000 端口仅用于内部通信
2. **启用 HTTPS**：生产环境必须配置 SSL/TLS
3. **定期更新依赖**：执行 `pip update -r requirements.txt`
4. **备份数据库**：定期备份 `knowledge_base.json` 和审计日志
5. **限制访问权限**：仅授权人员可访问仪表盘

## 故障排查

### 服务无法启动

1. 检查端口是否被占用：`netstat -tlnp | grep 8000`
2. 检查依赖是否安装完整：`pip list`
3. 检查环境变量配置：`cat .env`

### 智能体无法连接

1. 检查 Hub 服务是否运行正常
2. 确认网络可访问性：`curl http://localhost:8000/status`
3. 检查防火墙配置

### 仪表盘无数据

1. 检查场域监控是否启动
2. 检查浏览器控制台是否有错误
3. 确认 WebSocket 连接正常

## 版本升级

```bash
# 停止服务
docker-compose down

# 拉取最新代码或更新文件
git pull

# 重新构建
docker-compose up -d --build
```