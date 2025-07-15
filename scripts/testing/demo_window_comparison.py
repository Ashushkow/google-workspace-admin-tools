#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация улучшений диалога управления документами
"""

import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.ui.ui_components import ModernColors, ModernButton


def show_comparison():
    """Показывает сравнение размеров окна до и после оптимизации"""
    
    def create_old_window():
        """Создает окно старого размера для сравнения"""
        old_win = tk.Toplevel()
        old_win.title("🔴 Старый размер (900x700)")
        old_win.geometry("900x700")
        old_win.configure(bg=ModernColors.BACKGROUND)
        
        label = tk.Label(
            old_win,
            text="📏 Старый размер окна\n900x700 пикселей\n(~80% экрана)",
            font=('Segoe UI', 16, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            justify='center'
        )
        label.pack(expand=True)
        
        ModernButton(
            old_win,
            text="Закрыть",
            command=old_win.destroy,
            button_type="danger"
        ).pack(pady=20)
    
    def create_new_window():
        """Создает окно нового размера"""
        new_win = tk.Toplevel()
        new_win.title("✅ Новый размер (800x600)")
        new_win.geometry("800x600")
        new_win.configure(bg=ModernColors.BACKGROUND)
        
        label = tk.Label(
            new_win,
            text="📏 Новый размер окна\n800x600 пикселей\n(~60% экрана)\n\n✨ Более компактный\n📋 С функциями копирования/вставки",
            font=('Segoe UI', 14, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            justify='center'
        )
        label.pack(expand=True)
        
        ModernButton(
            new_win,
            text="Закрыть",
            command=new_win.destroy,
            button_type="success"
        ).pack(pady=20)
    
    # Создаем главное окно
    root = tk.Tk()
    root.title("📊 Сравнение размеров окна")
    root.geometry("400x300")
    root.configure(bg=ModernColors.BACKGROUND)
    
    # Заголовок
    title_label = tk.Label(
        root,
        text="📊 Демонстрация улучшений\nдиалога управления документами",
        font=('Segoe UI', 14, 'bold'),
        bg=ModernColors.BACKGROUND,
        fg=ModernColors.TEXT_PRIMARY,
        justify='center'
    )
    title_label.pack(pady=30)
    
    # Кнопки для демонстрации
    button_frame = tk.Frame(root, bg=ModernColors.BACKGROUND)
    button_frame.pack(expand=True)
    
    ModernButton(
        button_frame,
        text="🔴 Показать старый размер",
        command=create_old_window,
        button_type="danger"
    ).pack(pady=10)
    
    ModernButton(
        button_frame,
        text="✅ Показать новый размер",
        command=create_new_window,
        button_type="success"
    ).pack(pady=10)
    
    # Информация о улучшениях
    info_text = """
🎯 Улучшения:
• Размер уменьшен на 25%
• Добавлено контекстное меню для URL
• Оптимизированы отступы и шрифты
• Сохранена вся функциональность
    """
    
    info_label = tk.Label(
        root,
        text=info_text,
        font=('Segoe UI', 9),
        bg=ModernColors.BACKGROUND,
        fg=ModernColors.TEXT_SECONDARY,
        justify='left'
    )
    info_label.pack(pady=20)
    
    ModernButton(
        root,
        text="Закрыть демо",
        command=root.quit,
        button_type="primary"
    ).pack(pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    show_comparison()
