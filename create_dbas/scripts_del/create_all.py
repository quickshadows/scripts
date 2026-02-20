#!/usr/bin/env python3
"""
Совместимый враппер.

Основной скрипт теперь лежит в корне утилиты: `create_dbas/create_all.py`.
Этот файл оставлен, чтобы не ломать старые инструкции вида `cd scripts`.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    tool_root = Path(__file__).resolve().parents[1]
    target = tool_root / "create_all.py"
    if not target.exists():
        raise FileNotFoundError(f"Не найден основной скрипт: {target}")
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
