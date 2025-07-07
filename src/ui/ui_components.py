# -*- coding: utf-8 -*-
"""
Современные UI компоненты и стили.
"""

import tkinter as tk


class ModernColors:
    """
    Центральная палитра цветов для современного интерфейса.
    Использует Material Design принципы.
    """
    PRIMARY = "#2563eb"       # Основной синий цвет
    PRIMARY_DARK = "#1d4ed8"  # Темно-синий для hover эффектов
    PRIMARY_LIGHT = "#3b82f6" # Светло-синий для выделений
    SUCCESS = "#10b981"       # Зеленый для успешных операций
    WARNING = "#f59e0b"       # Оранжевый для предупреждений
    DANGER = "#ef4444"        # Красный для ошибок и удаления
    SECONDARY = "#374151"     # Темно-серый для второстепенных элементов (было #6b7280)
    SECONDARY_DARK = "#111827" # Почти черный для hover
    BACKGROUND = "#f8fafc"    # Светло-серый фон приложения
    SURFACE = "#ffffff"       # Белый фон для карточек
    CARD_BG = "#ffffff"       # Белый фон для карточек (алиас)
    TEXT_PRIMARY = "#1f2937"  # Основной цвет текста
    TEXT_SECONDARY = "#6b7280" # Вторичный цвет текста
    BORDER = "#e5e7eb"        # Цвет границ
    INFO = "#0ea5e9"          # Информационный цвет


class ModernButton(tk.Button):
    """
    Современная кнопка с автоматическими стилями и hover эффектами.
    
    Поддерживает различные типы:
    - primary: Основные действия (синий)
    - success: Успешные операции (зеленый) 
    - danger: Опасные действия (красный)
    - secondary: Второстепенные действия (серый)
    
    Автоматически добавляет иконки и hover эффекты.
    """
    
    def __init__(self, parent, **kwargs):
        # Извлекаем кастомные параметры
        button_type = kwargs.pop('button_type', kwargs.pop('style', 'primary'))
        icon = kwargs.pop('icon', '')
        
        # Устанавливаем стили по типу кнопки
        color_map = {
            'primary': (ModernColors.PRIMARY, ModernColors.PRIMARY_DARK, 'white'),
            'success': (ModernColors.SUCCESS, '#059669', 'white'),
            'danger': (ModernColors.DANGER, '#dc2626', 'white'),
            'warning': (ModernColors.WARNING, '#d97706', 'white'),
            'info': (ModernColors.INFO, '#0284c7', 'white'),
            'secondary': (ModernColors.SECONDARY, ModernColors.SECONDARY_DARK, 'white')
        }
        
        bg_color, hover_color, text_color = color_map.get(button_type, color_map['primary'])
        
        # Добавляем иконку к тексту если есть
        text = kwargs.get('text', '')
        if icon:
            kwargs['text'] = f"{icon} {text}"
        
        # Устанавливаем стандартные стили для компактности
        defaults = {
            'bg': bg_color,
            'fg': text_color,
            'relief': 'flat',
            'borderwidth': 0,
            'padx': 15,
            'pady': 6,
            'font': ('Segoe UI', 9),
            'cursor': 'hand2'
        }
        
        # Объединяем с переданными параметрами
        for key, value in defaults.items():
            kwargs.setdefault(key, value)
        
        super().__init__(parent, **kwargs)
        
        # Добавляем hover эффекты для лучшего UX
        self.hover_color = hover_color
        self.normal_color = bg_color
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        """Эффект при наведении мыши"""
        self.config(bg=self.hover_color)
    
    def on_leave(self, event):
        """Эффект при уходе мыши"""
        self.config(bg=self.normal_color)


class StatusIndicator(tk.Canvas):
    """Современный круглый индикатор статуса подключения"""
    
    def __init__(self, master, size=12, color="#6b7280", **kwargs):
        super().__init__(master, width=size, height=size, highlightthickness=0, 
                        bg=master.cget('bg'), **kwargs)
        self.size = size
        
        # Создаем круг с небольшой тенью (используем светло-серый вместо прозрачного)
        self.shadow = self.create_oval(1, 1, size-1, size-1, fill="#e5e7eb", outline="")
        self.circle = self.create_oval(0, 0, size-2, size-2, fill=color, outline="", width=0)
        
    def set_color(self, color):
        """Изменяет цвет индикатора"""
        self.itemconfig(self.circle, fill=color)
    
    def set_status(self, status):
        """
        Устанавливает статус индикатора.
        
        Args:
            status: 'online', 'offline', 'warning', 'error'
        """
        status_colors = {
            'online': ModernColors.SUCCESS,
            'offline': ModernColors.SECONDARY,
            'warning': ModernColors.WARNING,
            'error': ModernColors.DANGER
        }
        
        color = status_colors.get(status, ModernColors.SECONDARY)
        self.set_color(color)


def center_window(win, parent):
    """
    Центрирует дочернее окно относительно родительского.
    
    Args:
        win: Дочернее окно для центрирования
        parent: Родительское окно
    """
    win.update_idletasks()
    parent.update_idletasks()
    
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    ww = win.winfo_width()
    wh = win.winfo_height()
    
    x = px + (pw - ww) // 2
    y = py + (ph - wh) // 2
    
    win.geometry(f'+{x}+{y}')
