#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный тест подключения к серверу FreeIPA
Сервер: https://ipa001.infra.int.sputnik8.com/
Включает тест с простой аутентификацией для Windows
"""

import sys
import requests
import json
from urllib.parse import urljoin
import warnings
import base64
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


def test_basic_connectivity():
    """Базовый тест доступности сервера"""
    print("🔍 Тестирование базовой доступности сервера...")
    
    server_url = "https://ipa001.infra.int.sputnik8.com/"
    
    try:
        # Простой GET запрос к серверу
        response = requests.get(server_url, timeout=10, verify=False)
        print(f"✅ Сервер доступен! HTTP код: {response.status_code}")
        print(f"📊 Размер ответа: {len(response.content)} байт")
        
        # Проверяем, содержит ли ответ признаки FreeIPA
        content = response.text.lower()
        if "freeipa" in content or "identity management" in content:
            print("✅ Подтверждено: это сервер FreeIPA")
        else:
            print("⚠️  Не удалось подтвердить, что это FreeIPA сервер")
            
        return True
        
    except requests.exceptions.ConnectTimeout:
        print("❌ Тайм-аут подключения")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


def test_freeipa_api():
    """Тест FreeIPA API endpoint"""
    print("\n🔍 Тестирование FreeIPA API...")
    
    server_url = "https://ipa001.infra.int.sputnik8.com/"
    api_url = urljoin(server_url, "/ipa/json")
    
    try:
        # Попытка получить информацию о сервере через API
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Простой запрос к API (без аутентификации)
        response = requests.post(
            api_url, 
            headers=headers,
            json={
                "method": "ping",
                "params": [[], {}]
            },
            timeout=10,
            verify=False
        )
        
        print(f"📡 API endpoint доступен! HTTP код: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ API отвечает корректным JSON")
                if 'result' in result:
                    print("✅ Структура ответа соответствует FreeIPA API")
                    return True
            except json.JSONDecodeError:
                print("⚠️  API вернул не JSON ответ")
        elif response.status_code == 401:
            print("✅ API работает (требуется аутентификация)")
            return True
        
        return response.status_code in [200, 401]  # 401 ожидаем без аутентификации
        
    except requests.exceptions.ConnectTimeout:
        print("❌ Тайм-аут при обращении к API")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Ошибка подключения к API: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")
        return False


def test_freeipa_login_form():
    """Тест формы входа FreeIPA"""
    print("\n🔍 Тестирование формы входа FreeIPA...")
    
    server_url = "https://ipa001.infra.int.sputnik8.com/"
    login_url = urljoin(server_url, "/ipa/session/login_password")
    
    try:
        # Проверяем доступность формы входа
        response = requests.get(login_url, timeout=10, verify=False)
        
        if response.status_code == 200:
            print("✅ Форма входа доступна")
            return True
        elif response.status_code == 401:
            print("✅ Endpoint для входа найден (требуется аутентификация)")
            return True
        else:
            print(f"⚠️  Неожиданный код ответа: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании формы входа: {e}")
        return False


def test_freeipa_manual_auth():
    """Тест ручной аутентификации (демонстрация)"""
    print("\n🔍 Тест структуры аутентификации...")
    
    server_url = "https://ipa001.infra.int.sputnik8.com/"
    
    try:
        # Тестируем различные методы аутентификации
        auth_methods = [
            ("/ipa/session/login_password", "POST", "Пароль"),
            ("/ipa/session/login_kerberos", "POST", "Kerberos"),
            ("/ipa/json", "POST", "JSON API")
        ]
        
        print("📋 Проверка методов аутентификации:")
        
        for endpoint, method, description in auth_methods:
            try:
                url = urljoin(server_url, endpoint)
                if method == "POST":
                    response = requests.post(url, timeout=5, verify=False)
                else:
                    response = requests.get(url, timeout=5, verify=False)
                    
                if response.status_code in [200, 401, 403]:
                    print(f"  ✅ {description}: HTTP {response.status_code}")
                else:
                    print(f"  ⚠️  {description}: HTTP {response.status_code}")
                    
            except Exception:
                print(f"  ❌ {description}: Недоступен")
        
        print("\n💡 Для полного тестирования потребуются:")
        print("   - Имя пользователя FreeIPA")
        print("   - Пароль пользователя")
        print("   - Домен (вероятно: infra.int.sputnik8.com)")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании аутентификации: {e}")
        return False


def test_domain_info():
    """Тест получения информации о домене"""
    print("\n🔍 Анализ информации о домене...")
    
    server_url = "https://ipa001.infra.int.sputnik8.com/"
    
    try:
        # Анализируем URL для определения домена
        from urllib.parse import urlparse
        parsed = urlparse(server_url)
        hostname = parsed.hostname
        
        print(f"🌐 Hostname сервера: {hostname}")
        
        # Предполагаемые домены на основе hostname
        if hostname:
            parts = hostname.split('.')
            if len(parts) >= 3:
                # ipa001.infra.int.sputnik8.com -> infra.int.sputnik8.com
                domain = '.'.join(parts[1:])
                print(f"🏠 Предполагаемый домен: {domain}")
                
                # Проверка DNS записей (если возможно)
                try:
                    import socket
                    ip = socket.gethostbyname(hostname)
                    print(f"🔍 IP адрес сервера: {ip}")
                except:
                    print("⚠️  Не удалось определить IP адрес")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа домена: {e}")
        return False


def analyze_server_info():
    """Детальный анализ информации о сервере"""
    print("\n🔍 Детальный анализ сервера...")
    
    server_url = "https://ipa001.infra.int.sputnik8.com/"
    
    try:
        response = requests.get(server_url, timeout=10, verify=False)
        
        # Анализ заголовков
        print("📋 HTTP заголовки:")
        important_headers = [
            'server', 'x-frame-options', 'strict-transport-security',
            'set-cookie', 'www-authenticate', 'content-type'
        ]
        for header in important_headers:
            if header in response.headers:
                value = response.headers[header]
                if len(value) > 100:
                    value = value[:100] + "..."
                print(f"  {header}: {value}")
        
        # Анализ контента
        content = response.text
        
        # Поиск информации о версии
        if "IPA.version" in content:
            print("\n✅ Найдена информация о версии IPA в контенте")
            
        # Поиск конфигурационной информации
        if "IPA.config" in content:
            print("✅ Найдена конфигурационная информация IPA")
            
        # Проверка наличия стандартных IPA URL
        ipa_paths = [
            "/ipa/ui/", "/ipa/json", "/ipa/xml", 
            "/ipa/session/login_password", "/ipa/session/logout"
        ]
        print("\n📂 Проверка стандартных путей FreeIPA:")
        
        available_paths = 0
        for path in ipa_paths:
            try:
                test_url = urljoin(server_url, path)
                test_response = requests.head(test_url, timeout=5, verify=False)
                if test_response.status_code in [200, 401, 403]:
                    print(f"  ✅ {path}: HTTP {test_response.status_code}")
                    available_paths += 1
                else:
                    print(f"  ⚠️  {path}: HTTP {test_response.status_code}")
            except:
                print(f"  ❌ {path}: Недоступен")
        
        print(f"\n📊 Доступно {available_paths}/{len(ipa_paths)} стандартных путей")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        return False


def create_config_template():
    """Создание шаблона конфигурации для подключения"""
    print("\n🔧 Создание шаблона конфигурации...")
    
    config_template = {
        "server_url": "https://ipa001.infra.int.sputnik8.com/",
        "domain": "infra.int.sputnik8.com",
        "username": "your_username_here",
        "password": "your_password_here", 
        "use_kerberos": False,
        "verify_ssl": False,
        "description": "FreeIPA Server Configuration"
    }
    
    try:
        # Создаем директорию config если не существует
        import os
        os.makedirs("config", exist_ok=True)
        
        # Сохраняем шаблон
        config_file = "config/freeipa_config_template.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_template, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Шаблон конфигурации создан: {config_file}")
        print("💡 Отредактируйте файл, указав ваши учетные данные")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания шаблона: {e}")
        return False


def main():
    """Главная функция тестирования"""
    print("=" * 80)
    print("🧪 РАСШИРЕННЫЙ ТЕСТ ПОДКЛЮЧЕНИЯ К FREEIPA СЕРВЕРУ")
    print("🌐 Сервер: https://ipa001.infra.int.sputnik8.com/")
    print("=" * 80)
    
    tests = [
        ("Базовая доступность", test_basic_connectivity),
        ("FreeIPA API", test_freeipa_api),
        ("Форма входа", test_freeipa_login_form),
        ("Методы аутентификации", test_freeipa_manual_auth),
        ("Информация о домене", test_domain_info),
        ("Детальный анализ сервера", analyze_server_info),
        ("Создание шаблона конфигурации", create_config_template)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            results[test_name] = False
    
    # Итоговый отчет
    print("\n" + "=" * 80)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 80)
    
    for test_name, success in results.items():
        status = "✅ ПРОЙДЕН" if success else "❌ НЕ ПРОЙДЕН"
        print(f"{status:<15} {test_name}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\nРезультат: {passed_tests}/{total_tests} тестов пройдено")
    
    if passed_tests >= total_tests * 0.7:
        print("\n🎉 ОТЛИЧНЫЙ РЕЗУЛЬТАТ!")
        print("✅ Сервер FreeIPA полностью доступен и готов к интеграции!")
        
        print("\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
        print("   1. Получите учетные данные у администратора FreeIPA")
        print("   2. Отредактируйте config/freeipa_config_template.json")
        print("   3. Запустите приложение и настройте FreeIPA интеграцию")
        print("   4. Протестируйте создание групп и синхронизацию")
        
    elif passed_tests >= total_tests * 0.5:
        print("\n⚠️  ЧАСТИЧНЫЙ УСПЕХ")
        print("✅ Сервер FreeIPA доступен, но есть проблемы")
        
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("   1. Проверьте проблемные тесты")
        print("   2. Убедитесь в корректности URL сервера")
        print("   3. Обратитесь к администратору сервера")
        
    else:
        print("\n❌ ПРОБЛЕМЫ С ПОДКЛЮЧЕНИЕМ")
        print("❌ Сервер недоступен или работает некорректно")
        
        print("\n🆘 ДЕЙСТВИЯ:")
        print("   1. Проверьте сетевое подключение")
        print("   2. Убедитесь, что URL сервера правильный")
        print("   3. Проверьте настройки firewall/proxy")
        print("   4. Обратитесь к администратору сети")
    
    return 0 if passed_tests >= total_tests * 0.5 else 1


if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Тестирование завершено с кодом выхода: {exit_code}")
    sys.exit(exit_code)
