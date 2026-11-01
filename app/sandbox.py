import docker
import os
import tempfile
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

class SandboxError(Exception):
    """Custom exception for sandbox execution failures."""
    pass

class CodeSandbox:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            raise SandboxError(f"Failed to connect to Docker daemon: {e}")

        # Configuration from environment
        self.image = os.getenv("SANDBOX_IMAGE", "python:3.11-slim")
        self.mem_limit = os.getenv("SANDBOX_MEMORY_LIMIT", "256m")
        self.cpu_quota = int(os.getenv("SANDBOX_CPU_QUOTA", "50")) * 1000  # Convert % to quota (100% = 100,000)
        self.timeout = int(os.getenv("SANDBOX_TIMEOUT", "30"))

    def execute(self, code: str) -> Tuple[str, int]:
        """
        Executes Python code in a hardened Docker container.
        Returns a tuple of (stdout/stderr, exit_code).
        """
        # Create a temporary file for the code to be executed
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        container = None
        try:
            # Hardened Container Configuration
            container = self.client.containers.run(
                image=self.image,
                command=f"python {os.path.basename(tmp_path)}",
                volumes={
                    tmp_path: {'bind': '/app/script.py', 'mode': 'ro'}
                },
                working_dir="/app",
                # Security Hardening
                network_disabled=True,      # No internet/network access
                read_only=True,             # Root filesystem is read-only
                mem_limit=self.mem_limit,   # Memory ceiling
                cpu_quota=self.cpu_quota,   # CPU limit (50% of one core)
                tmpfs={'/tmp': 'rw'},      # Small writable area for Python internals
                detach=True,
                stdin_open=False,
            )

            # Wait for execution with timeout
            try:
                result = container.wait(timeout=self.timeout)
                exit_code = result.get("StatusCode", 1)
            except Exception:
                container.kill()
                return "Error: Execution timed out.", 124

            # Capture combined logs
            logs = container.logs().decode("utf-8")
            return logs, exit_code

        except Exception as e:
            return f"Sandbox System Error: {str(e)}", 1
        finally:
            if container:
                container.remove(force=True)
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    # Basic functional test
    sb = CodeSandbox()
    
    # Test 1: Valid Code
    print("Testing valid code...")
    out, code = sb.execute("print('Hello from Sandbox!')")
    print(f"Out: {out.strip()} | Code: {code}")

    # Test 2: Network Attempt (Should fail/be blocked)
    print("\nTesting network restriction...")
    out, code = sb.execute("import urllib.request; urllib.request.urlopen('http://google.com')")
    print(f"Out: {out.strip()} | Code: {code}")

    # Test 3: Filesystem Write (Should fail due to read-only)
    print("\nTesting read-only root...")
    out, code = sb.execute("open('/root/test.txt', 'w').write('fail')")
    print(f"Out: {out.strip()} | Code: {code}")
