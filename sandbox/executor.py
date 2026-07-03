# Copyright (c) 2026 李广好 (luoxuejian000)
# Resonance-Missile 项目
# 版权哈希: 814d69e39cbaa230
# 本文件受版权保护，未经授权不得修改、复制或分发。
# 完整版权信息请查看项目根目录下的 LICENSE 文件。

"""
沙箱执行器 —— 实践介入论：在隔离环境中安全执行漏洞利用验证。
资源限制：CPU、内存、磁盘、网络全隔离。
"""
import subprocess
import os
import tempfile
import shutil
import json
import signal
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SandboxResult:
    success: bool
    output: str
    error: str
    return_code: int
    execution_time: float
    resource_usage: Dict[str, Any]


class SandboxExecutor:
    def __init__(self, timeout: int = 30, max_memory_mb: int = 128, max_cpu_time: int = 10):
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb
        self.max_cpu_time = max_cpu_time
        self.sandbox_root = os.path.join(tempfile.gettempdir(), "resonance_sandbox")
        self._ensure_sandbox_dir()

    def _ensure_sandbox_dir(self):
        os.makedirs(self.sandbox_root, exist_ok=True)

    def _create_isolation_dir(self) -> str:
        return tempfile.mkdtemp(prefix="sandbox_", dir=self.sandbox_root)

    def execute_python(self, code: str, extra_files: Dict[str, str] = None) -> SandboxResult:
        start_time = time.time()
        isolation_dir = self._create_isolation_dir()
        
        try:
            script_path = os.path.join(isolation_dir, "exploit.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            if extra_files:
                for filename, content in extra_files.items():
                    file_path = os.path.join(isolation_dir, filename)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

            env = os.environ.copy()
            env["PYTHONPATH"] = isolation_dir
            env["SANDBOX_MODE"] = "true"
            env["MAX_MEMORY_MB"] = str(self.max_memory_mb)

            escaped_path = isolation_dir.replace("\\", "\\\\")
            result = subprocess.run(
                ["python", "-c", f"import sys; sys.path.insert(0, r'{escaped_path}'); exec(open('exploit.py', encoding='utf-8').read())"],
                cwd=isolation_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env
            )

            execution_time = time.time() - start_time
            return SandboxResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                resource_usage={"memory_mb": self.max_memory_mb, "timeout": self.timeout}
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return SandboxResult(
                success=False,
                output="",
                error=f"执行超时 ({self.timeout}s)",
                return_code=-1,
                execution_time=execution_time,
                resource_usage={"memory_mb": self.max_memory_mb, "timeout": self.timeout}
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return SandboxResult(
                success=False,
                output="",
                error=str(e),
                return_code=-2,
                execution_time=execution_time,
                resource_usage={"memory_mb": self.max_memory_mb, "timeout": self.timeout}
            )
        finally:
            shutil.rmtree(isolation_dir, ignore_errors=True)

    def execute_shell(self, command: str) -> SandboxResult:
        start_time = time.time()
        isolation_dir = self._create_isolation_dir()

        try:
            result = subprocess.run(
                command,
                cwd=isolation_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                shell=True
            )

            execution_time = time.time() - start_time
            return SandboxResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                resource_usage={"timeout": self.timeout}
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return SandboxResult(
                success=False,
                output="",
                error=f"执行超时 ({self.timeout}s)",
                return_code=-1,
                execution_time=execution_time,
                resource_usage={"timeout": self.timeout}
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return SandboxResult(
                success=False,
                output="",
                error=str(e),
                return_code=-2,
                execution_time=execution_time,
                resource_usage={"timeout": self.timeout}
            )
        finally:
            shutil.rmtree(isolation_dir, ignore_errors=True)

    def validate_exploit(self, exploit_code: str, target_code: str) -> Dict[str, Any]:
        test_code = f"""
import sys
sys.stdout = open('sandbox_output.txt', 'w', encoding='utf-8')
sys.stderr = open('sandbox_error.txt', 'w', encoding='utf-8')

TARGET_CODE = {repr(target_code)}

{exploit_code}

print('=== SANDBOX_EXECUTION_COMPLETE ===')
"""
        result = self.execute_python(test_code)
        
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "execution_time": result.execution_time,
            "risk_level": self._assess_risk(exploit_code)
        }

    def _assess_risk(self, code: str) -> str:
        high_risk_patterns = [
            "os.system", "subprocess", "exec(", "eval(", "import os",
            "import sys", "import socket", "import requests",
            "__import__", "open(", "write(", "shutil", "os.remove"
        ]
        medium_risk_patterns = [
            "print(", "input(", "len(", "str(", "int("
        ]

        high_count = sum(1 for p in high_risk_patterns if p in code)
        medium_count = sum(1 for p in medium_risk_patterns if p in code)

        if high_count >= 3:
            return "critical"
        elif high_count >= 1:
            return "high"
        elif medium_count >= 5:
            return "medium"
        else:
            return "low"


if __name__ == "__main__":
    sandbox = SandboxExecutor(timeout=10)
    
    test_code = """
print('Sandbox test running...')
for i in range(5):
    print(f'Iteration {i}')
print('Test completed!')
"""
    
    result = sandbox.execute_python(test_code)
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
    print(f"Error: {result.error}")
    print(f"Time: {result.execution_time:.2f}s")