from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str, content: str) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return str(target)


def ensure_dir(path: str) -> str:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return str(target)


def list_files(root: str) -> List[str]:
    base = Path(root)
    if not base.exists():
        return []
    return [str(p.relative_to(base)) for p in base.rglob("*") if p.is_file()]


def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default)
