#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест оптимизированного диалога добавления участников.
"""

import sys
import os
from pathlib import Path
import tkinter as tk

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_optimized_dialog():
    """Тест оптимизированного диалога"""
    try:
        from src.ui.sputnik_calendar_ui import AddSputnikMemberDialog
        from src.api.sputnik_calendar import create_sputnik_calendar_manager
        
        print("🚀 Тест оптимизированного диалога с быстрой загрузкой...")
        
        # Создаем календарный менеджер
        calendar_manager = create_sputnik_calendar_manager()
        if not calendar_manager:
            print("❌ Не удалось создать календарный менеджер")
            return
        
        print("✅ Календарный менеджер создан")
        
        # Создаем корневое окно
        root = tk.Tk()
        root.title("Тест БЫСТРОГО диалога SPUTNIK")
        root.geometry("500x300")
        
        # Функция для открытия диалога
        def open_dialog():
            def refresh_dummy():
                print("✅ Диалог был закрыт (refresh callback)")
            
            dialog = AddSputnikMemberDialog(root, calendar_manager, refresh_dummy)
            print("✅ Диалог открыт с оптимизацией!")
            print("💡 Особенности:")
            print("  ⚡ Быстрая загрузка (50 пользователей)")
            print("  ❌ Кнопка отмены загрузки") 
            print("  💾 Кэширование результатов")
            print("  📥 Кнопка 'Загрузить еще' для полного списка")
        
        # Создаем описание
        info_text = tk.Text(
            root, 
            height=12,
            width=60,
            font=("Arial", 10),
            wrap="word",
            padx=10,
            pady=10
        )
        info_text.pack(expand=True, fill="both", padx=20, pady=10)
        
        info_content = """🎯 ОПТИМИЗАЦИИ ДИАЛОГА ДОБАВЛЕНИЯ УЧАСТНИКОВ:

⚡ БЫСТРАЯ ЗАГРУЗКА:
• Загружается только первые 50 пользователей (вместо 500)
• Время загрузки уменьшено в ~10 раз
• Приложение не зависает

❌ ОТМЕНА ЗАГРУЗКИ:
• Кнопка "❌ Отмена" для прерывания загрузки
• Проверка отмены каждые 5 пользователей
• Fallback на примеры пользователей

💾 КЭШИРОВАНИЕ:
• Результаты сохраняются в памяти
• Повторное открытие диалога мгновенно

📥 РАСШИРЕННАЯ ЗАГРУЗКА:
• Кнопка "📥 Загрузить больше" после быстрой загрузки
• Загрузка полного списка (500 пользователей) по желанию

🔍 УМНЫЙ ПОИСК:
• Работает по имени и email одновременно
• Мгновенная фильтрация без задержек"""
        
        info_text.insert("1.0", info_content)
        info_text.config(state="disabled")
        
        # Создаем кнопку для открытия диалога
        btn = tk.Button(
            root, 
            text="🎯 ОТКРЫТЬ ОПТИМИЗИРОВАННЫЙ ДИАЛОГ",
            command=open_dialog,
            font=("Arial", 12, "bold"),
            bg="#2E8B57",
            fg="white",
            pady=8
        )
        btn.pack(pady=10)
        
        print("✅ Тестовое окно готово")
        print("💡 Нажмите кнопку для открытия БЫСТРОГО диалога")
        
        # Запускаем главный цикл
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_optimized_dialog()
