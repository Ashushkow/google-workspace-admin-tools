#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест кнопки календарей для воспроизведения ошибки
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ui.calendar_management import open_calendar_management
    print("✅ Импорт calendar_management успешный")
    
    # Создаем тестовое окно
    root = tk.Tk()
    root.title("Тест календарей")
    root.geometry("300x200")
    
    def test_calendar():
        """Тестируем открытие календарей"""
        try:
            window = open_calendar_management(root, None)
            print("✅ Окно календарей открыто успешно")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            messagebox.showerror("Ошибка", str(e))
    
    # Кнопка для теста
    btn = tk.Button(
        root,
        text="📅 Тест календарей",
        command=test_calendar,
        font=('Arial', 12),
        pady=10
    )
    btn.pack(pady=50)
    
    print("🧪 Нажмите кнопку для тестирования календарей")
    root.mainloop()
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
