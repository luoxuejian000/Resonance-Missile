# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
仪表盘API —— 实践介入论：提供场域状态的查询接口，只读，不修改任何系统状态。
"""
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from dashboard.field_monitor import monitor

app = FastAPI(title="Resonance-Missile Dashboard")


@app.get("/api/state")
async def get_state():
    return monitor.get_current_state()


@app.get("/api/history")
async def get_history(limit: int = Query(default=100, le=1000)):
    return monitor.get_history(limit)


@app.get("/api/alerts")
async def get_alerts(limit: int = Query(default=50, le=200)):
    return monitor.get_alerts(limit)


@app.get("/api/trend")
async def get_trend():
    return monitor.get_trend()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>Resonance-Missile 场域监控</title>
        <style>
            body { font-family: sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
            .metric { display: inline-block; margin: 10px; padding: 20px; background: #16213e; border-radius: 8px; min-width: 120px; text-align: center; }
            .metric .value { font-size: 36px; font-weight: bold; }
            .metric .label { font-size: 14px; color: #aaa; }
            .alert { padding: 10px; margin: 5px; border-radius: 4px; }
            .warning { background: #f39c12; color: #000; }
            .critical { background: #e74c3c; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 8px; text-align: center; border-bottom: 1px solid #333; }
            th { background: #16213e; }
        </style>
    </head>
    <body>
        <h1>🦅 Resonance-Missile 场域监控</h1>
        <div id="metrics"></div>
        <h2>📈 历史趋势</h2>
        <table id="history"><thead><tr><th>时间</th><th>U</th><th>D</th><th>A</th><th>H</th><th>告警</th></tr></thead><tbody></tbody></table>
        <script>
            async function refresh() {
                const state = await (await fetch('/api/state')).json();
                document.getElementById('metrics').innerHTML = `
                    <div class="metric"><div class="value">${state.U.toFixed(2)}</div><div class="label">U 统一性</div></div>
                    <div class="metric"><div class="value">${state.D.toFixed(2)}</div><div class="label">D 发展性</div></div>
                    <div class="metric"><div class="value">${state.A.toFixed(2)}</div><div class="label">A 对抗性</div></div>
                    <div class="metric"><div class="value">${state.H.toFixed(2)}</div><div class="label">H 和谐度</div></div>
                    <div class="metric"><div class="value">${state.agent_count}</div><div class="label">智能体数</div></div>
                    <div class="metric"><div class="value">${state.task_count}</div><div class="label">任务数</div></div>
                `;

                const history = await (await fetch('/api/history?limit=50')).json();
                const tbody = document.querySelector('#history tbody');
                tbody.innerHTML = history.slice().reverse().map(s => `
                    <tr>
                        <td>${new Date(s.timestamp*1000).toLocaleTimeString()}</td>
                        <td>${s.field.U.toFixed(2)}</td>
                        <td>${s.field.D.toFixed(2)}</td>
                        <td>${s.field.A.toFixed(2)}</td>
                        <td style="color:${s.field.H<0.3?'#e74c3c':s.field.H<0.5?'#f39c12':'#27ae60'}">${s.field.H.toFixed(2)}</td>
                        <td>${s.alerts.length > 0 ? '⚠️' : ''}</td>
                    </tr>
                `).join('');
            }
            refresh();
            setInterval(refresh, 3000);
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)