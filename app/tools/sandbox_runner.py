from __future__ import annotations

from typing import Any, Dict

try:
    import docker
except ImportError:  # pragma: no cover
    docker = None


class SandboxExecutionRunner:
    """Executes scripts in an isolated Docker sandbox."""

    def __init__(self, image_name: str = "python:3.11-slim") -> None:
        self.image_name = image_name
        self.client = docker.from_env() if docker is not None else None

    def execute_code(self, script_content: str, timeout_sec: int = 30) -> Dict[str, Any]:
        if self.client is None:
            return {"exit_code": -1, "output": "Docker SDK not installed; sandbox unavailable."}

        container = None
        try:
            container = self.client.containers.create(
                image=self.image_name,
                command=f"python -c \"{script_content}\"",
                network_disabled=True,
                mem_limit="512m",
                cpu_quota=50000,
            )
            container.start()
            result = container.wait(timeout=timeout_sec)
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")
            return {
                "exit_code": result.get("StatusCode", -1),
                "output": logs,
            }
        except Exception as exc:  # pragma: no cover
            return {"exit_code": -1, "output": f"Sandbox execution error: {exc}"}
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:  # pragma: no cover
                    pass


__all__ = ["SandboxExecutionRunner"]
