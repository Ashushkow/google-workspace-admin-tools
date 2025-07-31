#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для диагностики проблемы удаления участников из групп
"""

import sys
import os
from pathlib import Path

def analyze_source_code():
    """Анализирует исходный код для поиска проблем"""
    
    print("🔍 АНАЛИЗ ИСХОДНОГО КОДА ДЛЯ ДИАГНОСТИКИ ПРОБЛЕМЫ")
    print("=" * 80)
    
    # Путь к файлу репозитория
    repo_file = Path(__file__).parent / 'src' / 'repositories' / 'google_api_repository.py'
    
    if not repo_file.exists():
        print(f"❌ Файл не найден: {repo_file}")
        return False
    
    print(f"📁 Анализируем файл: {repo_file}")
    
    try:
        with open(repo_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Размер файла: {len(content)} символов")
        
        # Поиск проблем
        problems_found = []
        
        # 1. Проверяем наличие TODO комментариев
        todo_count = content.count('TODO: Реализовать через Google API')
        if todo_count > 0:
            problems_found.append(f"🚨 Найдено {todo_count} нереализованных TODO для Google API")
        
        # 2. Проверяем заглушки
        stub_count = content.count('(заглушка)')
        if stub_count > 0:
            problems_found.append(f"🚨 Найдено {stub_count} заглушек в коде")
        
        # 3. Проверяем дублирование методов remove_member
        remove_method_count = content.count('async def remove_member')
        if remove_method_count > 1:
            problems_found.append(f"🚨 Найдено {remove_method_count} дублированных методов remove_member")
        
        # 4. Поиск методов remove_member и анализ их содержимого
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'async def remove_member' in line:
                print(f"\n📍 Найден метод remove_member на строке {i+1}:")
                
                # Показываем метод с контекстом
                start = max(0, i-2)
                end = min(len(lines), i+15)
                for j in range(start, end):
                    prefix = ">>> " if j == i else "    "
                    print(f"{prefix}{j+1:3}: {lines[j]}")
                
                # Проверяем содержимое метода
                method_lines = []
                indent_level = None
                for k in range(i+1, len(lines)):
                    line = lines[k]
                    if line.strip() == "":
                        method_lines.append(line)
                        continue
                    
                    current_indent = len(line) - len(line.lstrip())
                    if indent_level is None:
                        if line.strip():
                            indent_level = current_indent
                    
                    if line.strip() and current_indent <= len(line.split('def remove_member')[0]):
                        break
                    
                    method_lines.append(line)
                    
                    if k - i > 20:  # Ограничиваем количество строк
                        break
                
                method_content = '\n'.join(method_lines)
                
                if 'TODO' in method_content:
                    problems_found.append(f"🚨 Метод на строке {i+1} содержит TODO - не реализован")
                
                if 'заглушка' in method_content:
                    problems_found.append(f"🚨 Метод на строке {i+1} является заглушкой")
                
                if 'return True' in method_content and len(method_content.strip()) < 200:
                    problems_found.append(f"🚨 Метод на строке {i+1} просто возвращает True - подозрительно простая реализация")
        
        # Выводим найденные проблемы
        print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print("=" * 50)
        
        if problems_found:
            print("❌ НАЙДЕНЫ ПРОБЛЕМЫ:")
            for i, problem in enumerate(problems_found, 1):
                print(f"{i}. {problem}")
        else:
            print("✅ Проблем в коде не найдено")
        
        # Проверяем Google API клиент
        api_client_file = Path(__file__).parent / 'src' / 'api' / 'google_api_client.py'
        if api_client_file.exists():
            print(f"\n📁 Проверяем Google API клиент: {api_client_file}")
            
            with open(api_client_file, 'r', encoding='utf-8') as f:
                api_content = f.read()
            
            # Ищем методы для работы с участниками групп
            group_member_methods = [
                'add_group_member',
                'remove_group_member', 
                'get_group_members'
            ]
            
            missing_methods = []
            for method in group_member_methods:
                if f'def {method}' not in api_content:
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"🚨 В Google API клиенте отсутствуют методы: {', '.join(missing_methods)}")
                problems_found.extend([f"Отсутствует метод {method} в Google API клиенте" for method in missing_methods])
            else:
                print("✅ Все необходимые методы найдены в Google API клиенте")
        
        return len(problems_found) == 0
        
    except Exception as e:
        print(f"❌ Ошибка анализа файла: {e}")
        return False


def generate_fix_plan():
    """Генерирует план исправления проблемы"""
    
    print("\n💡 ПЛАН ИСПРАВЛЕНИЯ ПРОБЛЕМЫ")
    print("=" * 80)
    
    print("1. 🔧 ИСПРАВЛЕНИЕ GOOGLE API КЛИЕНТА:")
    print("   - Добавить метод remove_group_member(group_email, member_email)")
    print("   - Добавить метод add_group_member(group_email, member_email)")  
    print("   - Добавить метод get_group_members(group_email)")
    print("   - Реализовать через Google Directory API")
    
    print("\n2. 🔧 ИСПРАВЛЕНИЕ РЕПОЗИТОРИЯ:")
    print("   - Удалить дублированные методы remove_member")
    print("   - Заменить заглушки на реальные вызовы API")
    print("   - Добавить корректную обработку ошибок")
    
    print("\n3. 🔧 ТЕСТИРОВАНИЕ:")
    print("   - Создать тесты для проверки функциональности")
    print("   - Протестировать с реальными данными")
    
    print("\n4. 🔧 ЛОГИРОВАНИЕ:")
    print("   - Добавить подробное логирование операций")
    print("   - Логировать ошибки Google API")


def main():
    """Главная функция диагностики"""
    
    print("🚀 ДИАГНОСТИКА ПРОБЛЕМЫ УДАЛЕНИЯ УЧАСТНИКОВ ИЗ ГРУПП GOOGLE")
    print("Проверяем исходный код на наличие проблем...")
    print("=" * 80)
    
    success = analyze_source_code()
    
    if not success:
        print("\n❌ ПРОБЛЕМА ПОДТВЕРЖДЕНА: Удаление участников из групп не работает!")
        generate_fix_plan()
    else:
        print("\n✅ Код выглядит корректно, проблема может быть в другом месте")
    
    print("\n" + "=" * 80)
    print("✅ Диагностика завершена")


if __name__ == "__main__":
    main()
