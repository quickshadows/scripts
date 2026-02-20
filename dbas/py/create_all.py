#!/usr/bin/env python3
"""
Совместимый враппер.

Исторически скрипт лежал в `dbas/py/create_all.py`, но после рефакторинга
актуальная реализация находится в `dbas/create/create_all.py`.

Этот файл оставлен, чтобы не ломать старые инструкции/алиасы/автоматизацию.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]  # .../scripts
    target = repo_root / "dbas" / "create" / "create_all.py"

    if not target.exists():
        raise FileNotFoundError(f"Не найден новый скрипт: {target}")

    print(
        "⚠️  DEPRECATED: используйте `dbas/create/create_all.py` "
        "(этот путь оставлен для совместимости).",
        file=sys.stderr,
    )

    # Пробрасываем argv как есть; runpy выполнит target как __main__
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
