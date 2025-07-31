#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Фиктивный FreeIPA клиент для Windows (без Kerberos)
Обходит проблему с python-freeipa на Windows без Kerberos
"""

import json
import requests
from typing import Dict, List, Optional, Any
import urllib3

# Отключаем SSL warnings для FreeIPA (тестовая среда)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FreeIPAClientStub:
    """Упрощенный FreeIPA клиент без Kerberos зависимостей"""
    
    def __init__(self, server: str, verify_ssl: bool = True, timeout: int = 30):
        # Убеждаемся, что URL содержит схему
        if not server.startswith(('http://', 'https://')):
            server = f"https://{server}"
        self.host = server.rstrip('/')
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.timeout = timeout
        self._logged_in = False
        
    def login(self, user: str, password: str) -> bool:
        """Логин через пароль (без Kerberos)"""
        login_url = f"{self.host}/ipa/session/login_password"
        
        # Попробуем несколько вариантов имени пользователя
        usernames_to_try = [
            user,
            f"{user}@infra.int.sputnik8.com",
            user.lower(),
            f"{user.lower()}@infra.int.sputnik8.com"
        ]
        
        for username in usernames_to_try:
            print(f"🔐 Попытка логина: URL={login_url}, User={username}")
            
            try:
                # Сначала получим CSRF токен если нужно
                response = self.session.get(f"{self.host}/ipa/ui/")
                
                response = self.session.post(
                    login_url,
                    data={'user': username, 'password': password},
                    headers={
                        'Referer': f"{self.host}/ipa/ui/",
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                )
                
                print(f"📡 Ответ сервера для {username}: status={response.status_code}")
                
                if response.text:
                    print(f"📄 Response text (первые 300 символов): {response.text[:300]}...")
                
                if response.status_code == 200:
                    # Проверяем, есть ли в ответе признак успешного входа
                    if ('Set-Cookie' in response.headers or 
                        'ipa_session' in response.text or
                        'user-menu' in response.text or
                        'logout' in response.text.lower()):
                        print(f"✅ Логин успешен для пользователя: {username}")
                        self._logged_in = True
                        return True
                    else:
                        print(f"⚠️ Получен 200, но нет признаков успешного логина для {username}")
                elif response.status_code == 302:
                    # Редирект может означать успешный логин
                    print(f"✅ Редирект - возможно успешный логин для {username}")
                    self._logged_in = True
                    return True
                else:
                    print(f"❌ Ошибка HTTP для {username}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Ошибка при попытке логина {username}: {e}")
                continue
        
        print(f"❌ Все попытки логина неудачны")
        return False
    
    def logout(self):
        """Выход из сессии"""
        if self._logged_in:
            try:
                logout_url = f"{self.host}/ipa/session/logout"
                self.session.get(logout_url)
            except:
                pass
            self._logged_in = False
    
    def _api_call(self, method: str, params: Optional[List] = None, options: Optional[Dict] = None) -> Dict:
        """Базовый API вызов"""
        if not self._logged_in:
            raise Exception("Not logged in")
        
        api_url = f"{self.host}/ipa/json"
        
        payload = {
            "method": method,
            "params": [params or [], options or {}]
        }
        
        response = self.session.post(
            api_url,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Referer': f"{self.host}/ipa/ui/"
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API call failed: {response.status_code}")
    
    def ping(self) -> Dict:
        """Ping сервера"""
        try:
            return self._api_call("ping")
        except:
            # Простой ping без аутентификации
            api_url = f"{self.host}/ipa/json"
            response = self.session.post(
                api_url,
                json={"method": "ping", "params": [[], {}]},
                headers={'Content-Type': 'application/json'}
            )
            return response.json() if response.status_code == 200 else {}
    
    def group_find(self, criteria: str = "", **options) -> Dict:
        """Поиск групп"""
        return self._api_call("group_find", [criteria], options)
    
    def group_add(self, group_name: str, **options) -> Dict:
        """Создание группы"""
        return self._api_call("group_add", [group_name], options)
    
    def group_show(self, group_name: str, **options) -> Dict:
        """Получение информации о группе"""
        return self._api_call("group_show", [group_name], options)
    
    def group_add_member(self, group_name: str, user: str = None, **options) -> Dict:
        """Добавление участника в группу"""
        params = [group_name]
        if user:
            options.setdefault('user', []).append(user)
        return self._api_call("group_add_member", params, options)
    
    def group_remove_member(self, group_name: str, user: str = None, **options) -> Dict:
        """Удаление участника из группы"""
        params = [group_name]
        if user:
            options.setdefault('user', []).append(user)
        return self._api_call("group_remove_member", params, options)
    
    def user_find(self, criteria: str = "", **options) -> Dict:
        """Поиск пользователей"""
        return self._api_call("user_find", [criteria], options)
    
    def user_show(self, user_name: str, **options) -> Dict:
        """Получение информации о пользователе"""
        return self._api_call("user_show", [user_name], options)
    
    def user_add(self, user_name: str, **options) -> Dict:
        """Создание пользователя"""
        return self._api_call("user_add", [user_name], options)
    
    def user_mod(self, user_name: str, **options) -> Dict:
        """Изменение пользователя"""
        return self._api_call("user_mod", [user_name], options)
    
    def user_del(self, user_name: str, **options) -> Dict:
        """Удаление пользователя"""
        return self._api_call("user_del", [user_name], options)
    
    def group_del(self, group_name: str, **options) -> Dict:
        """Удаление группы"""
        return self._api_call("group_del", [group_name], options)
    
    def login_kerberos(self):
        """Заглушка для Kerberos аутентификации"""
        print("⚠️ Kerberos аутентификация не поддерживается в stub режиме")
        return False


class FreeIPAErrorStub(Exception):
    """Заглушка для FreeIPAError"""
    pass


# Экспортируем под теми же именами, что и python-freeipa
Client = FreeIPAClientStub
FreeIPAError = FreeIPAErrorStub


def test_connection(host: str, user: str = None, password: str = None) -> bool:
    """Тест подключения к FreeIPA серверу"""
    try:
        client = FreeIPAClientStub(host, verify_ssl=False)
        
        if user and password:
            return client.login(user, password)
        else:
            # Просто проверяем доступность
            client.ping()
            return True
            
    except Exception:
        return False
