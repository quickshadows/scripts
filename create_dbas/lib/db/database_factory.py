#!/usr/bin/env python3
"""Фабрика для создания баз данных."""

import json
from typing import Dict, Any, Optional, List, Tuple
from .api_client import TimewebAPIClient
from .ip_manager import IPManager


class DatabaseFactory:
    """Фабрика для создания баз данных различных типов."""
    
    def __init__(self, api_client: TimewebAPIClient, ip_manager: IPManager):
        """
        Инициализирует фабрику БД.
        
        Args:
            api_client: Клиент API Timeweb Cloud
            ip_manager: Менеджер IP-адресов
        """
        self.api_client = api_client
        self.ip_manager = ip_manager
    
    def create_database(
        self,
        db_name: str,
        db_type: str,
        preset_id: Optional[int] = None,
        is_cluster: bool = False,
        config: Optional[Dict[str, Any]] = None,
        admin_password: Optional[str] = None,
        auto_backups: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создает базу данных с автоматическим выделением IP-адресов.
        
        Args:
            db_name: Имя базы данных
            db_type: Тип БД (mysql, postgres14, postgres15, и т.д.)
            preset_id: ID пресета конфигурации
            is_cluster: Создавать кластер (True) или одиночную БД (False)
            config: Дополнительная конфигурация (CPU, RAM, disk)
            admin_password: Пароль администратора
            auto_backups: Настройки автоматических бэкапов
        
        Returns:
            Ответ API с данными созданной БД
        
        Raises:
            RuntimeError: Если не удалось выделить IP-адреса
        """
        # Получаем IP-адреса
        floating_ip = self.ip_manager.get_floating_ip()
        local_ip = self.ip_manager.find_first_free_ip()
        
        if not local_ip:
            raise RuntimeError(f"Нет свободного приватного IP для {db_name}")
        
        print(f"Создание {'кластера' if is_cluster else 'базы'} {db_name} ({db_type})")
        print(f"floating IP: {floating_ip}, local IP: {local_ip}")
        
        # Создаем БД
        result = self.api_client.create_database(
            db_name=db_name,
            db_type=db_type,
            preset_id=preset_id,
            local_ip=local_ip,
            floating_ip=floating_ip,
            is_cluster=is_cluster,
            config=config,
            admin_password=admin_password,
            auto_backups=auto_backups
        )
        
        print(f"\nОтвет API на создание {'кластера' if is_cluster else 'базы'} '{db_name}':")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
    
    def create_multiple(
        self,
        databases: List[Tuple[str, str, Optional[int]]],
        is_cluster: bool = False,
        config: Optional[Dict[str, Any]] = None,
        admin_password: Optional[str] = None,
        auto_backups: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Создает несколько баз данных.
        
        Args:
            databases: Список кортежей (db_name, db_type, preset_id)
            is_cluster: Создавать кластеры (True) или одиночные БД (False)
            config: Дополнительная конфигурация
            admin_password: Пароль администратора
            auto_backups: Настройки автоматических бэкапов
        
        Returns:
            Список ответов API для каждой созданной БД
        """
        results = []
        for db_name, db_type, preset_id in databases:
            try:
                result = self.create_database(
                    db_name=db_name,
                    db_type=db_type,
                    preset_id=preset_id,
                    is_cluster=is_cluster,
                    config=config,
                    admin_password=admin_password,
                    auto_backups=auto_backups
                )
                results.append(result)
            except Exception as e:
                print(f"Ошибка при создании {db_name}: {e}")
                raise
        
        return results
