#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест FreeIPA GUI с отображением списка групп
"""

import sys
import tkinter as tk
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_freeipa_gui():
    """Тест GUI FreeIPA с новым функционалом"""
    print("🧪 Тест FreeIPA GUI с отображением групп...")
    
    try:
        # Создаем простое окно
        root = tk.Tk()
        root.title("FreeIPA GUI Test")
        root.geometry("600x500")
        
        # Добавляем кнопку для открытия FreeIPA Management
        def open_freeipa_window():
            try:
                from src.ui.freeipa_management import open_freeipa_management
                open_freeipa_management(root)
            except Exception as e:
                import traceback
                error_text = f"Ошибка открытия FreeIPA окна:\n{e}\n\nТрейсбек:\n{traceback.format_exc()}"
                
                # Показываем ошибку в отдельном окне
                error_window = tk.Toplevel(root)
                error_window.title("Ошибка")
                error_window.geometry("600x400")
                
                text_widget = tk.Text(error_window, wrap='word')
                text_widget.pack(fill='both', expand=True, padx=10, pady=10)
                text_widget.insert('1.0', error_text)
                print(f"❌ Ошибка: {e}")
        
        # Кнопка для теста подключения
        def test_connection():
            try:
                from src.services.freeipa_safe_import import get_freeipa_status
                status = get_freeipa_status()
                result = f"""FreeIPA статус:
✅ Доступен: {status['freeipa_available']}
🔧 Клиент: {status['client_class']}
📋 Примечание: {status.get('import_error', 'Нет ошибок')}"""
                result_label.config(text=result)
                print("✅ Статус FreeIPA проверен")
            except Exception as e:
                result_label.config(text=f"❌ Ошибка: {e}")
                print(f"❌ Ошибка проверки статуса: {e}")
        
        # Главная метка
        main_label = tk.Label(root, text="🔗 Тест FreeIPA GUI", 
                             font=("Arial", 16), pady=20)
        main_label.pack()
        
        # Кнопки
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        test_btn = tk.Button(btn_frame, text="🧪 Проверить статус FreeIPA", 
                            command=test_connection, font=("Arial", 10), 
                            bg='lightblue', padx=10, pady=5)
        test_btn.pack(pady=5)
        
        open_btn = tk.Button(btn_frame, text="🔗 Открыть FreeIPA Management", 
                            command=open_freeipa_window, font=("Arial", 10), 
                            bg='lightgreen', padx=10, pady=5)
        open_btn.pack(pady=5)
        
        # Результат
        result_label = tk.Label(root, text="Нажмите кнопку для теста", 
                               font=("Arial", 9), pady=10, wraplength=550,
                               justify='left')
        result_label.pack()
        
        # Инструкции
        instructions = """📋 Инструкции:
1. Нажмите "Проверить статус FreeIPA" для проверки подключения
2. Нажмите "Открыть FreeIPA Management" для открытия интерфейса управления
3. В окне FreeIPA:
   • Перейдите на вкладку "Подключение"
   • Нажмите "Подключиться к FreeIPA"
   • Перейдите на вкладку "Управление группами"
   • Должен отображаться список групп FreeIPA в таблице
   • Попробуйте кнопку "Обновить список"
   • Двойной клик по группе покажет детали"""
        
        instructions_label = tk.Label(root, text=instructions, 
                                     font=("Arial", 8), justify='left',
                                     wraplength=550, bg='lightyellow')
        instructions_label.pack(fill='x', padx=10, pady=10)
        
        print("✅ GUI создан, запуск mainloop...")
        root.mainloop()
        print("✅ GUI завершен")
        
    except Exception as e:
        print(f"❌ Ошибка GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_freeipa_gui()
