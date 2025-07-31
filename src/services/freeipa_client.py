#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FreeIPA Client для интеграции с Google Workspace Admin Tools
Управление пользователями и группами в FreeIPA
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from .freeipa_safe_import import (
    FREEIPA_AVAILABLE, 
    KERBEROS_AVAILABLE, 
    FREEIPA_IMPORT_ERROR,
    FreeIPAClient, 
    FreeIPAError, 
    HTTPKerberosAuth, 
    OPTIONAL,
    create_freeipa_client,
    get_freeipa_status
)

import requests
from requests.auth import HTTPBasicAuth


logger = logging.getLogger(__name__)


@dataclass
class FreeIPAConfig:
    """Конфигурация для подключения к FreeIPA"""
    server_url: str
    domain: str
    username: Optional[str] = None
    password: Optional[str] = None
    use_kerberos: bool = False
    verify_ssl: bool = True
    ca_cert_path: Optional[str] = None
    timeout: int = 30
    
    @classmethod
    def from_file(cls, config_path: str) -> 'FreeIPAConfig':
        """Загрузка конфигурации из файла"""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)
    
    def to_file(self, config_path: str) -> None:
        """Сохранение конфигурации в файл"""
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)


@dataclass
class FreeIPAUser:
    """Модель пользователя FreeIPA"""
    uid: str
    givenname: str
    sn: str
    mail: Optional[str] = None
    userpassword: Optional[str] = None
    homedirectory: Optional[str] = None
    loginshell: Optional[str] = '/bin/bash'
    uidnumber: Optional[int] = None
    gidnumber: Optional[int] = None
    gecos: Optional[str] = None
    telephonenumber: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    manager: Optional[str] = None
    
    @property
    def cn(self) -> str:
        """Полное имя пользователя"""
        return f"{self.givenname} {self.sn}"
    
    def to_freeipa_dict(self) -> Dict[str, Any]:
        """Преобразование в формат для FreeIPA API"""
        data = {}
        for field, value in asdict(self).items():
            if value is not None:
                data[field] = value
        
        # Добавляем cn если не указан
        if 'cn' not in data:
            data['cn'] = self.cn
            
        return data


@dataclass
class FreeIPAGroup:
    """Модель группы FreeIPA"""
    cn: str
    description: Optional[str] = None
    gidnumber: Optional[int] = None
    
    def to_freeipa_dict(self) -> Dict[str, Any]:
        """Преобразование в формат для FreeIPA API"""
        data = {}
        for field, value in asdict(self).items():
            if value is not None:
                data[field] = value
        return data


class FreeIPAService:
    """Сервис для работы с FreeIPA API"""
    
    def __init__(self, config: FreeIPAConfig):
        self.config = config
        self.client: Optional[FreeIPAClient] = None
        self._session = None
        
        if not FREEIPA_AVAILABLE:
            logger.warning("FreeIPA библиотека не установлена. Установите: pip install python-freeipa")
    
    def connect(self) -> bool:
        """Подключение к FreeIPA серверу"""
        if not FREEIPA_AVAILABLE:
            logger.error("FreeIPA библиотека не доступна")
            return False
        
        try:
            # Создаем клиент
            self.client = create_freeipa_client(
                server=self.config.server_url,
                verify_ssl=self.config.verify_ssl,
                timeout=self.config.timeout
            )
            
            # Аутентификация
            if self.config.use_kerberos:
                # Kerberos аутентификация
                logger.info("Подключение через Kerberos...")
                self.client.login_kerberos()
            elif self.config.username and self.config.password:
                # Аутентификация по паролю
                logger.info(f"Подключение как пользователь: {self.config.username}")
                self.client.login(self.config.username, self.config.password)
            else:
                logger.error("Не указан метод аутентификации")
                return False
            
            logger.info("Успешное подключение к FreeIPA")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка подключения к FreeIPA: {e}")
            return False
    
    def disconnect(self) -> None:
        """Отключение от FreeIPA"""
        if self.client:
            try:
                self.client.logout()
                logger.info("Отключение от FreeIPA")
            except Exception as e:
                logger.warning(f"Ошибка при отключении: {e}")
            finally:
                self.client = None
    
    def test_connection(self) -> bool:
        """Проверка подключения"""
        if not self.client:
            return False
        
        try:
            # Простой запрос для проверки связи
            result = self.client.user_find(sizelimit=1)
            return True
        except Exception as e:
            logger.error(f"Ошибка проверки подключения: {e}")
            return False
    
    # === Управление пользователями ===
    
    def create_user(self, user: FreeIPAUser) -> bool:
        """Создание пользователя в FreeIPA"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            user_data = user.to_freeipa_dict()
            result = self.client.user_add(user.uid, **user_data)
            
            logger.info(f"Пользователь {user.uid} создан в FreeIPA")
            return True
            
        except FreeIPAError as e:
            logger.error(f"Ошибка создания пользователя {user.uid}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при создании пользователя {user.uid}: {e}")
            return False
    
    def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """Получение информации о пользователе"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return None
        
        try:
            result = self.client.user_show(uid)
            return result['result']
        except FreeIPAError as e:
            logger.error(f"Пользователь {uid} не найден: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {uid}: {e}")
            return None
    
    def update_user(self, uid: str, **kwargs) -> bool:
        """Обновление пользователя"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            self.client.user_mod(uid, **kwargs)
            logger.info(f"Пользователь {uid} обновлен")
            return True
        except FreeIPAError as e:
            logger.error(f"Ошибка обновления пользователя {uid}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при обновлении пользователя {uid}: {e}")
            return False
    
    def delete_user(self, uid: str) -> bool:
        """Удаление пользователя"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            self.client.user_del(uid)
            logger.info(f"Пользователь {uid} удален из FreeIPA")
            return True
        except FreeIPAError as e:
            logger.error(f"Ошибка удаления пользователя {uid}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при удалении пользователя {uid}: {e}")
            return False
    
    def list_users(self, search_filter: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение списка пользователей"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return []
        
        try:
            if search_filter:
                result = self.client.user_find(search_filter, sizelimit=limit)
            else:
                result = self.client.user_find(sizelimit=limit)
            
            return result['result']
        except Exception as e:
            logger.error(f"Ошибка получения списка пользователей: {e}")
            return []
    
    # === Управление группами ===
    
    def create_group(self, group: FreeIPAGroup) -> bool:
        """Создание группы в FreeIPA"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            group_data = group.to_freeipa_dict()
            # Исключаем cn из дополнительных параметров, так как он передается отдельно
            cn = group_data.pop('cn')
            result = self.client.group_add(cn, **group_data)
            
            logger.info(f"Группа {group.cn} создана в FreeIPA")
            return True
            
        except FreeIPAError as e:
            logger.error(f"Ошибка создания группы {group.cn}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при создании группы {group.cn}: {e}")
            return False
    
    def get_group(self, cn: str) -> Optional[Dict[str, Any]]:
        """Получение информации о группе"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return None
        
        try:
            result = self.client.group_show(cn)
            return result['result']
        except FreeIPAError as e:
            logger.error(f"Группа {cn} не найдена: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка получения группы {cn}: {e}")
            return None
    
    def delete_group(self, cn: str) -> bool:
        """Удаление группы"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            self.client.group_del(cn)
            logger.info(f"Группа {cn} удалена из FreeIPA")
            return True
        except FreeIPAError as e:
            logger.error(f"Ошибка удаления группы {cn}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при удалении группы {cn}: {e}")
            return False
    
    def list_groups(self, search_filter: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение списка групп"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return []
        
        try:
            if search_filter:
                result = self.client.group_find(search_filter, sizelimit=limit)
            else:
                result = self.client.group_find(sizelimit=limit)
            
            # ОТЛАДКА: Выводим что получили
            print(f"🐛 DEBUG list_groups: тип={type(result)}, ключи={list(result.keys()) if isinstance(result, dict) else 'N/A'}")
            
            # Обрабатываем как полный ответ FreeIPA API
            if isinstance(result, dict):
                # Сначала проверим простую структуру (прямо result содержит список групп)
                if 'result' in result and isinstance(result['result'], list):
                    groups_list = result['result']
                    print(f"🐛 DEBUG: Простая структура - {len(groups_list)} групп")
                    return groups_list
                
                # Проверим вложенную структуру (result.result.result содержит список)
                elif 'result' in result and isinstance(result['result'], dict):
                    inner_result = result['result']
                    print(f"🐛 DEBUG: Вложенная структура, внутренние ключи: {list(inner_result.keys())}")
                    
                    if 'result' in inner_result and isinstance(inner_result['result'], list):
                        groups_list = inner_result['result']
                        print(f"🐛 DEBUG: Извлекли {len(groups_list)} групп из вложенной структуры")
                        return groups_list
                
                # Если это не то, что мы ожидаем
                print(f"🐛 DEBUG: Неожиданная структура данных")
                logger.warning(f"Неожиданный формат ответа от FreeIPA API: {result}")
                return []
                
            # Если это уже список (для совместимости)
            elif isinstance(result, list):
                print(f"🐛 DEBUG: Получили уже готовый список из {len(result)} групп")
                return result
            else:
                logger.warning(f"Неожиданный формат ответа от FreeIPA API: {type(result)}")
                print(f"🐛 DEBUG: Неожиданный формат: {type(result)}")
                return []
        except Exception as e:
            logger.error(f"Ошибка получения списка групп: {e}")
            return []
    
    def get_groups(self, search_filter: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Алиас для list_groups - получение списка групп"""
        return self.list_groups(search_filter, limit)
    
    # === Управление членством в группах ===
    
    def add_user_to_group(self, uid: str, group_cn: str) -> bool:
        """Добавление пользователя в группу"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            self.client.group_add_member(group_cn, user=[uid])
            logger.info(f"Пользователь {uid} добавлен в группу {group_cn}")
            return True
        except FreeIPAError as e:
            logger.error(f"Ошибка добавления пользователя {uid} в группу {group_cn}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при добавлении пользователя {uid} в группу {group_cn}: {e}")
            return False
    
    def remove_user_from_group(self, uid: str, group_cn: str) -> bool:
        """Удаление пользователя из группы"""
        if not self.client:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            self.client.group_remove_member(group_cn, user=[uid])
            logger.info(f"Пользователь {uid} удален из группы {group_cn}")
            return True
        except FreeIPAError as e:
            logger.error(f"Ошибка удаления пользователя {uid} из группы {group_cn}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при удалении пользователя {uid} из группы {group_cn}: {e}")
            return False
    
    def get_user_groups(self, uid: str) -> List[str]:
        """Получение списка групп пользователя"""
        user_data = self.get_user(uid)
        if not user_data:
            return []
        
        return user_data.get('memberof_group', [])
    
    def get_group_members(self, group_cn: str) -> List[str]:
        """Получение списка членов группы"""
        group_data = self.get_group(group_cn)
        if not group_data:
            return []
        
        return group_data.get('member_user', [])
    
    # === Интеграция с Google Workspace ===
    
    def sync_user_from_google(self, google_user: Dict[str, Any], default_groups: List[str] = None) -> bool:
        """Синхронизация пользователя из Google Workspace в FreeIPA"""
        if default_groups is None:
            default_groups = []
        
        try:
            # Извлекаем данные из Google user
            uid = google_user.get('primaryEmail', '').split('@')[0]
            if not uid:
                logger.error("Не удалось извлечь username из Google user")
                return False
            
            # Создаем FreeIPA пользователя
            freeipa_user = FreeIPAUser(
                uid=uid,
                givenname=google_user.get('name', {}).get('givenName', ''),
                sn=google_user.get('name', {}).get('familyName', ''),
                mail=google_user.get('primaryEmail', ''),
                title=google_user.get('organizations', [{}])[0].get('title', '') if google_user.get('organizations') else '',
                department=google_user.get('organizations', [{}])[0].get('department', '') if google_user.get('organizations') else '',
                telephonenumber=google_user.get('phones', [{}])[0].get('value', '') if google_user.get('phones') else ''
            )
            
            # Создаем пользователя
            if not self.create_user(freeipa_user):
                return False
            
            # Добавляем в группы по умолчанию
            for group_cn in default_groups:
                self.add_user_to_group(uid, group_cn)
            
            logger.info(f"Пользователь {uid} синхронизирован из Google Workspace в FreeIPA")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации пользователя из Google Workspace: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        if self.connect():
            return self
        else:
            raise Exception("Не удалось подключиться к FreeIPA")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# === Вспомогательные функции ===

def create_freeipa_config_template(output_path: str = "config/freeipa_config.json") -> None:
    """Создание шаблона конфигурации FreeIPA"""
    config = FreeIPAConfig(
        server_url="https://ipa.example.com",
        domain="example.com",
        username="admin",
        password="your_password",
        use_kerberos=False,
        verify_ssl=True,
        ca_cert_path=None,
        timeout=30
    )
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    config.to_file(output_path)
    print(f"Шаблон конфигурации FreeIPA создан: {output_path}")


def test_freeipa_connection(config_path: str = "config/freeipa_config.json") -> bool:
    """Тестирование подключения к FreeIPA"""
    try:
        config = FreeIPAConfig.from_file(config_path)
        
        with FreeIPAService(config) as freeipa:
            if freeipa.test_connection():
                print("✅ Подключение к FreeIPA успешно")
                
                # Показываем статистику
                users = freeipa.list_users(limit=10)
                groups = freeipa.list_groups(limit=10)
                
                print(f"📊 Найдено пользователей: {len(users)}")
                print(f"📊 Найдено групп: {len(groups)}")
                
                return True
            else:
                print("❌ Ошибка подключения к FreeIPA")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка тестирования FreeIPA: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "create-config":
            create_freeipa_config_template()
        elif sys.argv[1] == "test":
            test_freeipa_connection()
        else:
            print("Доступные команды:")
            print("  create-config - создать шаблон конфигурации")
            print("  test - протестировать подключение")
    else:
        print("FreeIPA Client для Admin Team Tools")
        print("Используйте: python freeipa_client.py [create-config|test]")
