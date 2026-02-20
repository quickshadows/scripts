#!/usr/bin/env python3
"""Загрузка конфигураций из файлов и переменных окружения."""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(env: str = None) -> Dict[str, Any]:
    """
    Загружает конфигурацию для указанного окружения.
    
    Args:
        env: Окружение (prod, stage, dev). Если не указано, берется из переменной окружения ENV.
    
    Returns:
        Словарь с конфигурацией
    """
    if env is None:
        env = os.getenv("ENV", "dev")
    
    # Путь к config относительно этой утилиты
    config_dir = Path(__file__).parent.parent.parent / "config"
    
    # Загружаем базовую конфигурацию БД
    db_config_path = config_dir / "db_config.yaml"
    db_config = {}
    if db_config_path.exists():
        with open(db_config_path, "r", encoding="utf-8") as f:
            db_config = yaml.safe_load(f) or {}
    
    # Загружаем конфигурацию окружения
    env_config_path = config_dir / "environments" / f"{env}.yaml"
    env_config = {}
    if env_config_path.exists():
        with open(env_config_path, "r", encoding="utf-8") as f:
            env_config = yaml.safe_load(f) or {}
    
    # Объединяем конфигурации (env_config перезаписывает db_config)
    config = {**db_config, **env_config}
    
    # Переопределяем значения из переменных окружения
    config["timeweb_token"] = os.getenv("TIMEWEB_CLOUD_TOKEN", config.get("timeweb_token"))
    config["network_id"] = os.getenv("NETWORK_ID", config.get("network_id"))
    config["project_id"] = int(os.getenv("PROJECT_ID", config.get("project_id", 0)))
    
    return config


def validate_config(config: Dict[str, Any]) -> None:
    """
    Валидирует конфигурацию и выбрасывает исключение при отсутствии обязательных полей.
    
    Args:
        config: Словарь с конфигурацией
    
    Raises:
        ValueError: Если отсутствуют обязательные поля
    """
    required_fields = ["timeweb_token", "network_id", "project_id"]
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        raise ValueError(f"Отсутствуют обязательные поля конфигурации: {', '.join(missing_fields)}")
