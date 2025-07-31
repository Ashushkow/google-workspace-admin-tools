#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест подключения к серверу FreeIPA
Сервер: https://ipa001.infra.int.sputnik8.com/
"""

import sys
import requests
import json
from urllib.parse import urljoin
import warnings
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


def test_freeipa_with_library():
    """Тест с использованием python-freeipa библиотеки"""
    print("\n🔍 Тестирование с python-freeipa библиотекой...")
    
    try:
        from python_freeipa import ClientMeta
        
        # Создаем клиент (без аутентификации)
        client = ClientMeta(
            'ipa001.infra.int.sputnik8.com',
            verify_ssl=False
        )
        
        print("✅ FreeIPA клиент создан успешно")
        
        # Попытка подключения (ожидаем ошибку аутентификации)
        try:
            result = client.ping()
            print("✅ Ping к серверу успешен")
            print(f"📊 Результат ping: {result}")
            return True
        except Exception as e:
            if "Unauthorized" in str(e) or "Authentication" in str(e):
                print("✅ Сервер отвечает (требуется аутентификация)")
                return True
            else:
                print(f"⚠️  Ошибка ping: {e}")
                return False
                
    except ImportError:
        print("❌ Библиотека python-freeipa не установлена")
        print("💡 Установите: pip install python-freeipa")
        return False
    except Exception as e:
        print(f"❌ Ошибка при использовании python-freeipa: {e}")
        return False


def analyze_server_info():
    """Анализ информации о сервере"""
    print("\n🔍 Анализ информации о сервере...")
    
    server_url = "https://ipa001.infra.int.sputnik8.com/"
    
    try:
        response = requests.get(server_url, timeout=10, verify=False)
        
        # Анализ заголовков
        print("📋 HTTP заголовки:")
        important_headers = ['server', 'x-frame-options', 'strict-transport-security']
        for header in important_headers:
            if header in response.headers:
                print(f"  {header}: {response.headers[header]}")
        
        # Попытка определить версию
        content = response.text
        if "IPA.version" in content:
            print("✅ Обнаружена информация о версии IPA в контенте")
            
        # Проверка наличия стандартных IPA URL
        ipa_paths = ["/ipa/ui/", "/ipa/json", "/ipa/xml"]
        print("\n📂 Проверка стандартных путей FreeIPA:")
        
        for path in ipa_paths:
            try:
                test_url = urljoin(server_url, path)
                test_response = requests.head(test_url, timeout=5, verify=False)
                status = "✅" if test_response.status_code in [200, 401, 403] else "❌"
                print(f"  {status} {path}: HTTP {test_response.status_code}")
            except:
                print(f"  ❌ {path}: Недоступен")
                
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        return False


def main():
    """Главная функция тестирования"""
    print("=" * 70)
    print("🧪 ТЕСТ ПОДКЛЮЧЕНИЯ К FREEIPA СЕРВЕРУ")
    print("🌐 Сервер: https://ipa001.infra.int.sputnik8.com/")
    print("=" * 70)
    
    tests = [
        ("Базовая доступность", test_basic_connectivity),
        ("FreeIPA API", test_freeipa_api),
        ("Python FreeIPA библиотека", test_freeipa_with_library),
        ("Анализ сервера", analyze_server_info)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            results[test_name] = False
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 70)
    
    for test_name, success in results.items():
        status = "✅ ПРОЙДЕН" if success else "❌ НЕ ПРОЙДЕН"
        print(f"{status:<15} {test_name}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\nРезультат: {passed_tests}/{total_tests} тестов пройдено")
    
    if passed_tests >= total_tests * 0.5:
        print("✅ Сервер FreeIPA доступен и готов к настройке!")
        print("\n💡 Следующие шаги:")
        print("   1. Получите учетные данные для подключения")
        print("   2. Настройте конфигурацию в приложении")
        print("   3. Протестируйте аутентификацию")
    else:
        print("❌ Возможны проблемы с доступностью сервера")
        print("\n💡 Рекомендации:")
        print("   1. Проверьте сетевое подключение")
        print("   2. Убедитесь, что URL корректен")
        print("   3. Обратитесь к администратору сервера")
    
    return 0 if passed_tests >= total_tests * 0.5 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
