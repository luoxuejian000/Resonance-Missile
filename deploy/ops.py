# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
运维工具脚本 —— 提供常用运维命令的封装。
"""
import subprocess
import os
import sys
import json
from datetime import datetime


def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd or os.getcwd()
        )
        return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


def check_dependencies():
    """检查系统依赖"""
    print("检查系统依赖...")
    
    checks = [
        ("python", "python --version"),
        ("pip", "pip --version"),
        ("docker", "docker --version"),
        ("docker-compose", "docker-compose --version")
    ]
    
    for name, cmd in checks:
        result = run_command(cmd)
        status = "OK" if result["success"] else "缺失"
        print(f"  {name}: {status}")
        if result["success"]:
            print(f"    {result['output'].strip()}")


def start_docker():
    """启动 Docker 服务"""
    print("启动 Docker 服务...")
    result = run_command("docker-compose up -d")
    if result["success"]:
        print("  Docker 服务启动成功")
    else:
        print(f"  启动失败: {result['error']}")


def stop_docker():
    """停止 Docker 服务"""
    print("停止 Docker 服务...")
    result = run_command("docker-compose down")
    if result["success"]:
        print("  Docker 服务已停止")
    else:
        print(f"  停止失败: {result['error']}")


def show_status():
    """显示服务状态"""
    print("服务状态:")
    result = run_command("docker-compose ps")
    if result["success"]:
        print(result["output"])
    else:
        print("  无法获取状态")


def show_logs(service=None, lines=50):
    """显示日志"""
    print(f"显示日志 ({lines} 行)...")
    cmd = f"docker-compose logs {'--tail=' + str(lines)} {' ' + service if service else ''}"
    result = run_command(cmd)
    if result["success"]:
        print(result["output"])
    else:
        print(f"  无法获取日志: {result['error']}")


def backup_data():
    """备份数据"""
    print("备份数据...")
    backup_dir = os.path.join(os.getcwd(), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.zip")
    
    files_to_backup = [
        "knowledge_base.json",
        "audit.jsonl",
        "security_policy.json"
    ]
    
    existing_files = [f for f in files_to_backup if os.path.exists(f)]
    
    if existing_files:
        cmd = f"zip {backup_file} {' '.join(existing_files)}"
        result = run_command(cmd)
        if result["success"]:
            print(f"  备份成功: {backup_file}")
        else:
            print(f"  备份失败: {result['error']}")
    else:
        print("  没有需要备份的文件")


def restore_data(backup_file):
    """恢复数据"""
    print(f"恢复数据: {backup_file}")
    if not os.path.exists(backup_file):
        print(f"  文件不存在: {backup_file}")
        return
    
    result = run_command(f"unzip -o {backup_file}")
    if result["success"]:
        print("  恢复成功")
    else:
        print(f"  恢复失败: {result['error']}")


def run_tests():
    """运行测试"""
    print("运行测试...")
    result = run_command("python -m pytest tests/test_integration.py -v")
    if result["success"]:
        print(result["output"])
    else:
        print(f"  测试失败: {result['error']}")


def run_stress_test():
    """运行压力测试"""
    print("运行压力测试...")
    result = run_command("python stress_test/runner.py")
    if result["success"]:
        print(result["output"])
    else:
        print(f"  压力测试失败: {result['error']}")


def show_usage():
    """显示使用帮助"""
    print("""
Resonance-Missile 运维工具

用法: python deploy/ops.py <命令>

命令列表:
  check       - 检查系统依赖
  start       - 启动 Docker 服务
  stop        - 停止 Docker 服务
  status      - 显示服务状态
  logs [服务名] - 显示日志
  backup      - 备份数据
  restore <文件> - 恢复数据
  test        - 运行测试
  stress      - 运行压力测试
  help        - 显示帮助

示例:
  python deploy/ops.py start
  python deploy/ops.py logs hub
  python deploy/ops.py backup
""")


def main():
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1]
    
    commands = {
        "check": check_dependencies,
        "start": start_docker,
        "stop": stop_docker,
        "status": show_status,
        "logs": lambda: show_logs(sys.argv[2] if len(sys.argv) > 2 else None),
        "backup": backup_data,
        "restore": lambda: restore_data(sys.argv[2] if len(sys.argv) > 2 else ""),
        "test": run_tests,
        "stress": run_stress_test,
        "help": show_usage
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"未知命令: {command}")
        show_usage()


if __name__ == "__main__":
    main()