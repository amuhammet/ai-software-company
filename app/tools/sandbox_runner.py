from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    success: bool = False

    @property
    def output(self) -> str:
        return (self.stdout or "") + (self.stderr or "")


class SandboxExecutionRunner:
    """Executes generated scripts in an isolated Docker sandbox."""

    def __init__(self, image_name: str = "python:3.11-slim") -> None:
        self.image_name = image_name
        try:
            import docker
        except ImportError:  # pragma: no cover
            docker = None
        self._docker = docker
        self._client = docker.from_env() if docker is not None else None

    def execute_code(self, script_content: str, timeout_sec: int = 30) -> SandboxResult:
        if self._client is None:
            return SandboxResult(exit_code=-1, stderr="Docker SDK not available; sandbox unavailable.")

        container = None
        try:
            container = self._client.containers.run(
                image=self.image_name,
                command=["python", "-c", script_content],
                network_disabled=True,
                mem_limit="512m",
                auto_remove=True,
                detach=False,
                stdout=True,
                stderr=True,
                timeout=timeout_sec,
            )
            if isinstance(container, bytes):
                stdout = container.decode("utf-8", errors="replace")
                return SandboxResult(exit_code=0, stdout=stdout, success=True)

            # Docker SDK returns bytes or a tuple depending on API behavior.
            if isinstance(container, tuple):
                stdout, stderr = container
                return SandboxResult(
                    exit_code=0,
                    stdout=stdout.decode("utf-8", errors="replace") if isinstance(stdout, bytes) else str(stdout),
                    stderr=stderr.decode("utf-8", errors="replace") if isinstance(stderr, bytes) else str(stderr),
                    success=True,
                )

            return SandboxResult(exit_code=0, stdout=str(container), success=True)
        except Exception as exc:  # pragma: no cover
            return SandboxResult(exit_code=-1, stderr=f"Sandbox execution error: {exc}")
        finally:
            if container is not None and hasattr(container, "remove"):
                try:
                    container.remove(force=True)
                except Exception:
                    pass


__all__ = ["SandboxExecutionRunner", "SandboxResult"]
