#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Минимальный тест GUI запуска
"""

import sys
import tkinter as tk
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_gui():
    """Простой тест GUI"""
    print("🧪 Тест простого GUI...")
    
    try:
        # Создаем простое окно
        root = tk.Tk()
        root.title("Test GUI - FreeIPA Ready")
        root.geometry("400x300")
        
        # Добавляем текст
        label = tk.Label(root, text="✅ GUI работает!\n🔗 FreeIPA интеграция готова к тестированию", 
                        font=("Arial", 12), pady=20)
        label.pack()
        
        # Кнопка для теста FreeIPA
        def test_freeipa():
            try:
                from src.services.freeipa_safe_import import get_freeipa_status
                status = get_freeipa_status()
                result = f"FreeIPA статус:\n✅ Доступен: {status['freeipa_available']}\n🔧 Клиент: {status['client_class']}"
                result_label.config(text=result)
            except Exception as e:
                result_label.config(text=f"❌ Ошибка: {e}")
        
        btn = tk.Button(root, text="🧪 Тест FreeIPA", command=test_freeipa, 
                       font=("Arial", 10), pady=10)
        btn.pack()
        
        result_label = tk.Label(root, text="Нажмите кнопку для теста", 
                               font=("Arial", 9), pady=10, wraplength=350)
        result_label.pack()
        
        print("✅ GUI создан, запуск mainloop...")
        root.mainloop()
        print("✅ GUI завершен")
        
    except Exception as e:
        print(f"❌ Ошибка GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gui()
