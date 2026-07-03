# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

#!/usr/bin/env python3
"""
系统健康检查脚本 —— 谐振调谐论：定期检查各组件健康状态。
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import websockets
import json
import time
from config import settings


async def check_hub():
    try:
        import httpx
        connect_host = "localhost" if settings.hub_host == "0.0.0.0" else settings.hub_host
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{connect_host}:{settings.hub_port}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return True, f"Hub正常运行, 连接客户端: {len(data.get('connected_clients', []))}"
            return False, f"Hub异常: HTTP {response.status_code}"
    except Exception as e:
        return False, f"Hub异常: {str(e)}"


async def check_dashboard():
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8001/api/state", timeout=5)
            if response.status_code == 200:
                return True, "Dashboard正常运行"
            return False, f"Dashboard异常: HTTP {response.status_code}"
    except Exception as e:
        return False, f"Dashboard异常: {str(e)}"


async def main():
    print("Resonance-Missile 健康检查")
    print("=" * 40)

    hub_ok, hub_msg = await check_hub()
    dashboard_ok, dashboard_msg = await check_dashboard()

    hub_status = "[OK]" if hub_ok else "[FAIL]"
    dashboard_status = "[OK]" if dashboard_ok else "[FAIL]"
    print(f"通信中枢: {hub_status} {hub_msg}")
    print(f"仪表盘: {dashboard_status} {dashboard_msg}")

    if hub_ok and dashboard_ok:
        print("\n系统状态: 健康")
        sys.exit(0)
    else:
        print("\n系统状态: 异常")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())