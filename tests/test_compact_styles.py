#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест компактных компонентов
"""

import tkinter as tk
import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_modern_styles():
    """Тест компактных стилей"""
    try:
        # Тестируем импорт
        from src.ui.modern_styles import (
            ModernColors, ModernWindowConfig, CompactFrame, 
            CompactLabel, CompactEntry, CompactButton
        )
        print("✅ Импорт модуля современных стилей успешен")
        
        # Тестируем создание компонентов
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        test_window = tk.Toplevel(root)
        test_window.title("Тест компактных компонентов")
        test_window.geometry("400x300")
        test_window.configure(bg=ModernColors.BACKGROUND)
        
        # Создаем компактные компоненты
        frame = CompactFrame(test_window)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Метка
        label = CompactLabel(frame, text="Тестовая метка", font_type='title')
        label.pack(pady=5)
        
        # Поле ввода
        entry = CompactEntry(frame, width_type='entry_small')
        entry.pack(pady=5)
        entry.insert(0, "Тест поля ввода")
        
        # Кнопки разных стилей
        styles = ['primary', 'success', 'warning', 'danger', 'info', 'secondary']
        for style in styles:
            btn = CompactButton(frame, text=f"Кнопка {style}", style=style, width_type='button_small')
            btn.pack(pady=2)
        
        print("✅ Создание компактных компонентов успешно")
        
        # Проверяем конфигурацию
        print(f"📏 Размеры окон: {len(ModernWindowConfig.WINDOW_SIZES)} типов")
        print(f"🎨 Основной цвет: {ModernColors.PRIMARY}")
        print(f"📝 Шрифт заголовка: {ModernWindowConfig.FONTS['title']}")
        print(f"📐 Размер кнопки: {ModernWindowConfig.WIDGET_SIZES['button_width']}")
        
        # Показываем окно на 3 секунды
        test_window.after(3000, root.destroy)
        test_window.deiconify()
        root.mainloop()
        
        print("✅ Тест завершен успешно")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        return False

if __name__ == "__main__":
    success = test_modern_styles()
    print(f"\n{'🎉 ВСЕ ТЕСТЫ ПРОШЛИ' if success else '💥 ЕСТЬ ОШИБКИ'}")
