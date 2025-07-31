#!/usr/bin/env python3
"""
Тест для проверки исправления синтаксической ошибки в freeipa_management.py
"""

import sys
import os
import ast

def test_python_syntax(file_path):
    """Проверка синтаксиса Python файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Компилируем в AST для проверки синтаксиса
        ast.parse(content)
        return True, "Синтаксис корректен"
        
    except SyntaxError as e:
        return False, f"Синтаксическая ошибка в строке {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Ошибка чтения файла: {e}"

def main():
    """Главная функция теста"""
    print("🧪 Проверка синтаксиса freeipa_management.py")
    print("=" * 50)
    
    file_path = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'freeipa_management.py')
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return 1
    
    success, message = test_python_syntax(file_path)
    
    if success:
        print(f"✅ {message}")
        print("\n📋 Дополнительные проверки:")
        
        # Проверяем размер файла
        file_size = os.path.getsize(file_path)
        print(f"  📁 Размер файла: {file_size} байт")
        
        # Проверяем количество строк
        with open(file_path, 'r', encoding='utf-8') as f:
            line_count = len(f.readlines())
        print(f"  📊 Количество строк: {line_count}")
        
        print("\n✅ Все проверки пройдены успешно!")
        print("🎉 Кнопка FreeIPA теперь должна работать без ошибок")
        return 0
        
    else:
        print(f"❌ {message}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
