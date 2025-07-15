#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автономный тест нового диалога добавления участников.
"""

import sys
import os
from pathlib import Path
import tkinter as tk

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_dialog():
    """Прямой тест диалога"""
    try:
        from src.ui.sputnik_calendar_ui import AddSputnikMemberDialog
        from src.api.sputnik_calendar import create_sputnik_calendar_manager
        
        print("🚀 Запуск автономного теста диалога...")
        
        # Создаем календарный менеджер
        calendar_manager = create_sputnik_calendar_manager()
        if not calendar_manager:
            print("❌ Не удалось создать календарный менеджер")
            return
        
        print("✅ Календарный менеджер создан")
        
        # Создаем корневое окно
        root = tk.Tk()
        root.title("Тест диалога SPUTNIK")
        root.geometry("400x200")
        
        # Функция для открытия диалога
        def open_dialog():
            def refresh_dummy():
                print("✅ Диалог был закрыт (refresh callback)")
            
            dialog = AddSputnikMemberDialog(root, calendar_manager, refresh_dummy)
            print("✅ Диалог открыт!")
        
        # Создаем кнопку для открытия диалога
        btn = tk.Button(
            root, 
            text="🎯 Открыть диалог добавления участника SPUTNIK",
            command=open_dialog,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            pady=10
        )
        btn.pack(expand=True, pady=50)
        
        info_label = tk.Label(
            root,
            text="Нажмите кнопку для тестирования нового диалога\nс выбором пользователей домена sputnik8.com",
            font=("Arial", 10),
            justify="center"
        )
        info_label.pack(pady=10)
        
        print("✅ Тестовое окно готово")
        print("💡 Нажмите кнопку в окне для открытия диалога")
        
        # Запускаем главный цикл
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dialog()
