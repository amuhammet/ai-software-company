from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from duckduckgo_search import DDGS  # type: ignore
except Exception:  # pragma: no cover
    DDGS = None

try:
    from tavily import TavilyClient  # type: ignore
except Exception:  # pragma: no cover
    TavilyClient = None


class SandboxResult:
    def __init__(self, success: bool, stdout: str, stderr: str, return_code: int) -> None:
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code

    def as_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "return_code": self.return_code,
        }


def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search the web using Tavily when credentials are set; fallback to DuckDuckGo."""
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    if tavily_key and TavilyClient is not None:
        try:
            client = TavilyClient(api_key=tavily_key)
            response = client.search(query=query, max_results=max_results)
            out: List[Dict[str, str]] = []
            for item in response.get("results", [])[:max_results]:
                out.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", item.get("snippet", "")),
                })
            return out
        except Exception:
            pass

    if DDGS is not None:
        try:
            results = []
            search = DDGS().text(query, max_results=max_results)
            for item in search:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "content": item.get("body", ""),
                })
            return results
        except Exception:
            pass

    return [{
        "title": "Fallback reference",
        "url": "https://example.com",
        "content": "Live search is unavailable; configure TAVILY_API_KEY for automatic research.",
    }]


def run_python_in_sandbox(code: str, timeout: int = 30) -> SandboxResult:
    """Runs Python snippets in an isolated Docker container when available; otherwise local Python fallback."""
    temp_dir = Path(tempfile.mkdtemp(prefix="agent_sandbox_"))
    script = temp_dir / "solution.py"
    script.write_text(code, encoding="utf-8")

    try:
        proc = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--network=none",
                "-v",
                f"{temp_dir}:/workspace",
                "-w",
                "/workspace",
                "python:3.11-slim",
                "python",
                "/workspace/solution.py",
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return SandboxResult(
            success=proc.returncode == 0,
            stdout=proc.stdout,
            stderr=proc.stderr,
            return_code=proc.returncode,
        )
    except FileNotFoundError:
        proc = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=timeout)
        return SandboxResult(
            success=proc.returncode == 0,
            stdout=proc.stdout,
            stderr=proc.stderr,
            return_code=proc.returncode,
        )
    except subprocess.TimeoutExpired as exc:
        return SandboxResult(False, exc.stdout or "", exc.stderr or "Execution timeout exceeded", 124)


def write_text(path: str, content: str) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return str(target)


__all__ = ["search_web", "run_python_in_sandbox", "SandboxResult", "write_text"]
