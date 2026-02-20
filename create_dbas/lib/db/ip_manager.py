#!/usr/bin/env python3
"""Управление IP-адресами в VPC."""

from typing import Optional
from .api_client import TimewebAPIClient


class IPManager:
    """Менеджер для работы с IP-адресами в VPC."""
    
    def __init__(self, api_client: TimewebAPIClient, subnet_base: str = "192.168.0"):
        """
        Инициализирует менеджер IP-адресов.
        
        Args:
            api_client: Клиент API Timeweb Cloud
            subnet_base: Базовый адрес подсети (например, "192.168.0")
        """
        self.api_client = api_client
        self.subnet_base = subnet_base
    
    def find_first_free_ip(self, start: int = 2, end: int = 254) -> Optional[str]:
        """
        Находит первый свободный приватный IP из указанного диапазона.
        
        Args:
            start: Начальный адрес диапазона (по умолчанию 2, исключая .0 и .1)
            end: Конечный адрес диапазона (по умолчанию 254, исключая .255)
        
        Returns:
            Первый свободный IP-адрес или None, если свободных нет
        """
        busy_ips = set(self.api_client.get_busy_ips())
        
        for i in range(start, end + 1):
            ip = f"{self.subnet_base}.{i}"
            if ip not in busy_ips:
                return ip
        
        return None
    
    def get_floating_ip(self) -> str:
        """
        Получает новый плавающий IP.
        
        Returns:
            Плавающий IP-адрес
        """
        return self.api_client.get_floating_ip()
