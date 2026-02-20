#!/usr/bin/env python3
"""Клиент для работы с Timeweb Cloud API."""

import time
import json
import requests
from typing import Dict, Any, Optional, List


class TimewebAPIClient:
    """Клиент для взаимодействия с Timeweb Cloud API."""
    
    DEFAULT_BASE_URL_V1 = "https://api.timeweb.cloud/api/v1"
    DEFAULT_BASE_URL_V2 = "https://api.timeweb.cloud/api/v2"
    
    def __init__(
        self,
        token: str,
        network_id: str,
        project_id: int,
        availability_zone: str = "spb-3",
        base_url_v1: Optional[str] = None,
        base_url_v2: Optional[str] = None,
        databases_url: Optional[str] = None,
    ):
        """
        Инициализирует клиент API.
        
        Args:
            token: Токен авторизации Timeweb Cloud
            network_id: ID сети VPC
            project_id: ID проекта
            availability_zone: Зона доступности
            base_url_v1: Базовый URL для v1 API (floating-ips, и т.п.)
            base_url_v2: Базовый URL для v2 API (vpcs, и т.п.)
            databases_url: Полный URL для эндпоинта создания БД (может отличаться для stage)
        """
        self.token = token
        self.network_id = network_id
        self.project_id = project_id
        self.availability_zone = availability_zone
        self.base_url_v1 = (base_url_v1 or self.DEFAULT_BASE_URL_V1).rstrip("/")
        self.base_url_v2 = (base_url_v2 or self.DEFAULT_BASE_URL_V2).rstrip("/")

        # databases_url можно задать как полный эндпоинт (/databases) или как базовый /api/v1
        if databases_url:
            db_url = databases_url.rstrip("/")
            self.databases_url = db_url if db_url.endswith("/databases") else f"{db_url}/databases"
        else:
            self.databases_url = f"{self.base_url_v1}/databases"

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    
    def get_floating_ip(self) -> str:
        """
        Создает новый плавающий IP.
        
        Returns:
            IP-адрес плавающего IP
        
        Raises:
            RuntimeError: Если не удалось получить плавающий IP
        """
        url = f"{self.base_url_v1}/floating-ips"
        payload = {
            "is_ddos_guard": False,
            "availability_zone": self.availability_zone
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        floating_ip = data.get("ip", {}).get("ip")
        if not floating_ip or floating_ip == "null":
            raise RuntimeError(f"Не удалось получить плавающий IP. Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        time.sleep(1)  # Небольшая пауза между запросами
        return floating_ip
    
    def get_busy_ips(self) -> List[str]:
        """
        Получает список занятых IP-адресов в VPC.
        
        Returns:
            Список занятых IP-адресов
        
        Raises:
            RuntimeError: Если не удалось получить список IP
        """
        url = f"{self.base_url_v2}/vpcs/{self.network_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        
        busy_ips = data.get("vpc", {}).get("busy_address", [])
        if busy_ips is None:
            raise RuntimeError("Не удалось получить занятые IP-адреса.")
        
        return busy_ips if isinstance(busy_ips, list) else []
    
    def create_database(
        self,
        db_name: str,
        db_type: str,
        preset_id: Optional[int],
        local_ip: str,
        floating_ip: str,
        is_cluster: bool = False,
        config: Optional[Dict[str, Any]] = None,
        admin_password: Optional[str] = None,
        auto_backups: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создает базу данных через API.
        
        Args:
            db_name: Имя базы данных
            db_type: Тип БД (mysql, postgres14, postgres15, и т.д.)
            preset_id: ID пресета конфигурации
            local_ip: Локальный IP-адрес
            floating_ip: Плавающий IP-адрес
            is_cluster: Создавать кластер (True) или одиночную БД (False)
            config: Дополнительная конфигурация (CPU, RAM, disk)
            admin_password: Пароль администратора
            auto_backups: Настройки автоматических бэкапов
        
        Returns:
            Ответ API с данными созданной БД
        """
        url = self.databases_url
        
        # Типы БД, которые поддерживают hash_type (только MySQL)
        mysql_types = {"mysql", "mysql8_4"}
        
        payload: Dict[str, Any] = {
            "name": db_name,
            "type": db_type,
            "availability_zone": self.availability_zone,
            "project_id": self.project_id,
            "network": {
                "id": self.network_id,
                "floating_ip": floating_ip,
                "local_ip": local_ip
            }
        }

        # ВАЖНО: API обычно не принимает одновременно preset_id и configuration.
        # По умолчанию используем configuration (конфигуратор).
        # Если preset_id задан — используем его и НЕ отправляем configuration.
        if preset_id is not None:
            payload["preset_id"] = int(preset_id)
        else:
            if config is None:
                # Конфигурация по умолчанию (fallback)
                config = {
                    "configurator_id": 45,
                    "cpu": 1,
                    "ram": 1024,
                    "disk": 10240,
                }
            payload["configuration"] = config
        
        # Добавляем hash_type только для MySQL
        if db_type in mysql_types:
            payload["hash_type"] = "caching_sha2"
        
        # Добавляем admin только для БД, которые требуют пароль администратора
        # (некоторые типы БД могут не требовать этого поля)
        admin_required_types = {"mysql", "mysql8_4", "postgres14", "postgres15", 
                                "postgres16", "postgres17", "postgres18", 
                                "mongodb7", "mongodb8_0"}
        if db_type in admin_required_types:
            payload["admin"] = {
                "password": admin_password or "Passwd123",
                "for_all": False
            }
        
        # replication добавляем только там, где это поддерживается
        cluster_supported_types = {
            "mysql", "mysql8_4",
            "postgres14", "postgres15", "postgres16", "postgres17", "postgres18",
            "mongodb7", "mongodb8_0",
            "redis7", "redis8_1",
        }
        if is_cluster and db_type in cluster_supported_types:
            payload["replication"] = {"count": 3}
        
        if auto_backups:
            payload["auto_backups"] = auto_backups
        
        response = requests.post(url, headers=self.headers, json=payload)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            body = response.text
            raise requests.HTTPError(
                f"{e} | url={url} | response={body}",
                response=response,
            ) from e

        data = response.json() if response.content else {}
        
        time.sleep(2)  # Пауза после создания
        return data
