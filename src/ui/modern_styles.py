# -*- coding: utf-8 -*-
"""
Современные стили и конфигурация для компактного дизайна окон.
Следует принципам Material Design и современным трендам UX/UI.
"""

import tkinter as tk
from tkinter import ttk

# Подключаем менеджер тем для единого источника правды
from ..themes.theme_manager import theme_manager


class ModernColors:
    """
    Центральная палитра цветов для современного интерфейса.
    Теперь значения динамически подстраиваются под активную тему через ThemeManager.
    Сохраняет прежний API (атрибуты в UPPER_CASE), чтобы не ломать существующий код.
    """
    # Значения по умолчанию (fallback), используются до применения темы и для ключей, которых нет в теме
    PRIMARY = "#2563eb"       # Основной синий цвет
    PRIMARY_DARK = "#1d4ed8"  # Темно-синий для hover эффектов
    PRIMARY_LIGHT = "#3b82f6" # Светло-синий для выделений
    SUCCESS = "#10b981"       # Зеленый для успешных операций
    WARNING = "#f59e0b"       # Оранжевый для предупреждений
    DANGER = "#ef4444"        # Красный для ошибок и удаления
    ERROR = DANGER             # Алиас для DANGER (совместимость)
    SECONDARY = "#374151"     # Темно-серый для второстепенных элементов
    SECONDARY_DARK = "#111827" # Почти черный для hover
    BACKGROUND = "#f8fafc"    # Светло-серый фон приложения
    SURFACE = "#ffffff"       # Поверхности/карточки
    CARD_BG = "#ffffff"       # Алиас для SURFACE
    TEXT_PRIMARY = "#1f2937"  # Основной цвет текста
    TEXT_SECONDARY = "#6b7280" # Вторичный цвет текста
    BORDER = "#e5e7eb"        # Цвет границ
    INFO = "#0ea5e9"          # Информационный цвет

    @classmethod
    def apply_theme(cls, theme):
        """Применяет цвета активной темы к палитре ModernColors."""
        if not theme:
            return
        # Отображение ключей из ThemeManager в локальные токены
        cls.PRIMARY = theme.get_color('accent', cls.PRIMARY)
        cls.PRIMARY_DARK = theme.get_color('accent_hover', cls.PRIMARY_DARK)
        # У тем нет отдельного accent_light — используем accent
        cls.PRIMARY_LIGHT = theme.get_color('accent', cls.PRIMARY_LIGHT)

        cls.SUCCESS = theme.get_color('success', cls.SUCCESS)
        cls.WARNING = theme.get_color('warning', cls.WARNING)
        cls.DANGER = theme.get_color('error', cls.DANGER)
        cls.ERROR = cls.DANGER

        # Поверхности и фон
        cls.BACKGROUND = theme.get_color('background', cls.BACKGROUND)
        secondary_surface = theme.get_color('secondary', cls.SURFACE)
        cls.SURFACE = secondary_surface
        cls.CARD_BG = secondary_surface

        # Текст и границы
        cls.TEXT_PRIMARY = theme.get_color('text_primary', cls.TEXT_PRIMARY)
        cls.TEXT_SECONDARY = theme.get_color('text_secondary', cls.TEXT_SECONDARY)
        cls.BORDER = theme.get_color('border', cls.BORDER)

        # Вторичные/нейтральные
        # Если в теме нет отдельного SECONDARY_DARK — сохраняем дефолт
        cls.SECONDARY = theme.get_color('secondary', cls.SECONDARY)
        # SECONDARY_DARK оставляем как есть (можно вычислять по теме при необходимости)

        # Информационный
        cls.INFO = theme.get_color('info', cls.INFO)


class ModernWindowConfig:
    """Конфигурация для современных окон"""
    
    # Размеры окон (компактные)
    WINDOW_SIZES = {
        'create_user': '580x520',      # Было 700x650
        'edit_user': '880x580',        # Было 900x650
        'group_management': '780x580', # Было 900x650, оптимизировано
        'group_edit': '480x420',       # Было 500x450
        'asana_invite': '380x240',     # Было 420x270
        'error_log': '720x480',        # Было 800x500
        'add_to_group': '420x350',     # Новый размер
        'user_selection': '450x380',   # Было 500x400
        'employee_list': '800x600',    # Компактный размер
        'freeipa_management': '750x580', # Было 800x600
        'orgunit_management': '950x680', # Оптимизировано с 1000x700
        'document_management': '650x480' # Новый: окно управления документами
    }
    
    # Отступы и размеры (уменьшенные для компактности)
    PADDING = {
        'window': {'padx': 15, 'pady': 12},      # Было 20, 15
        'section': {'padx': 10, 'pady': 8},      # Было 15, 10
        'field': {'padx': 8, 'pady': 6},         # Было 10, 8
        'button': {'padx': 12, 'pady': 4},       # Было 15, 6
        'small': {'padx': 5, 'pady': 3}          # Новый размер
    }
    
    # Шрифты (оптимизированные для компактности)
    FONTS = {
        'title': ('Segoe UI', 14, 'bold'),       # Было 16
        'subtitle': ('Segoe UI', 11, 'bold'),    # Было 12
        'label': ('Segoe UI', 9),                # Было 11
        'entry': ('Segoe UI', 9),                # Было 11
        'button': ('Segoe UI', 9),               # Было 11
        'small': ('Segoe UI', 8)                 # Новый размер
    }
    
    # Размеры виджетов
    WIDGET_SIZES = {
        'entry_width': 40,          # Было 50
        'entry_small': 25,          # Было 32
        'button_width': 16,         # Было 18
        'button_small': 12,         # Новый размер
        'listbox_height': 12,       # Было 15
        'text_height': 4,           # Было 5
        'combo_width': 38           # Было 47
    }


class CompactFrame(tk.Frame):
    """Компактный фрейм с автоматическими отступами"""
    
    def __init__(self, parent, padding_type='section', **kwargs):
        kwargs.setdefault('bg', ModernColors.BACKGROUND)
        super().__init__(parent, **kwargs)
        
        self.padding = ModernWindowConfig.PADDING[padding_type]


class CompactLabel(tk.Label):
    """Компактная метка с современным стилем"""
    
    def __init__(self, parent, text='', font_type='label', **kwargs):
        kwargs.setdefault('font', ModernWindowConfig.FONTS[font_type])
        kwargs.setdefault('bg', ModernColors.BACKGROUND)
        kwargs.setdefault('fg', ModernColors.TEXT_PRIMARY)
        super().__init__(parent, text=text, **kwargs)


class CompactEntry(tk.Entry):
    """Компактное поле ввода с современным стилем"""
    
    def __init__(self, parent, width_type='entry_width', **kwargs):
        kwargs.setdefault('width', ModernWindowConfig.WIDGET_SIZES[width_type])
        kwargs.setdefault('font', ModernWindowConfig.FONTS['entry'])
        kwargs.setdefault('relief', 'solid')
        kwargs.setdefault('bd', 1)
        kwargs.setdefault('bg', 'white')
        kwargs.setdefault('fg', ModernColors.TEXT_PRIMARY)
        super().__init__(parent, **kwargs)


class CompactButton(tk.Button):
    """Компактная кнопка с современным стилем"""
    
    def __init__(self, parent, text='', style='primary', width_type='button_width', **kwargs):
        # Цветовая схема
        color_map = {
            'primary': (ModernColors.PRIMARY, 'white'),
            'success': (ModernColors.SUCCESS, 'white'),
            'danger': (ModernColors.DANGER, 'white'),
            'warning': (ModernColors.WARNING, 'white'),
            'info': (ModernColors.INFO, 'white'),
            'secondary': (ModernColors.SECONDARY, 'white')
        }
        
        bg_color, fg_color = color_map.get(style, color_map['primary'])
        
        kwargs.setdefault('width', ModernWindowConfig.WIDGET_SIZES[width_type])
        kwargs.setdefault('font', ModernWindowConfig.FONTS['button'])
        kwargs.setdefault('bg', bg_color)
        kwargs.setdefault('fg', fg_color)
        kwargs.setdefault('relief', 'flat')
        kwargs.setdefault('borderwidth', 0)
        kwargs.setdefault('cursor', 'hand2')
        
        super().__init__(parent, text=text, **kwargs)


class CompactListbox(tk.Listbox):
    """Компактный список с современным стилем"""
    
    def __init__(self, parent, height_type='listbox_height', **kwargs):
        kwargs.setdefault('height', ModernWindowConfig.WIDGET_SIZES[height_type])
        kwargs.setdefault('font', ModernWindowConfig.FONTS['entry'])
        kwargs.setdefault('bg', 'white')
        kwargs.setdefault('fg', ModernColors.TEXT_PRIMARY)
        kwargs.setdefault('selectbackground', ModernColors.PRIMARY)
        kwargs.setdefault('selectforeground', 'white')
        kwargs.setdefault('relief', 'solid')
        kwargs.setdefault('bd', 1)
        super().__init__(parent, **kwargs)


class CompactScrolledText(tk.Text):
    """Компактное текстовое поле с прокруткой"""
    
    def __init__(self, parent, width=60, height_type='text_height', **kwargs):
        kwargs.setdefault('height', ModernWindowConfig.WIDGET_SIZES[height_type])
        kwargs.setdefault('width', width)
        kwargs.setdefault('font', ModernWindowConfig.FONTS['entry'])
        kwargs.setdefault('bg', 'white')
        kwargs.setdefault('fg', ModernColors.TEXT_PRIMARY)
        kwargs.setdefault('relief', 'solid')
        kwargs.setdefault('bd', 1)
        kwargs.setdefault('wrap', tk.WORD)
        super().__init__(parent, **kwargs)
        
        # Добавляем скроллбар
        self.scrollbar = tk.Scrollbar(parent, orient='vertical', command=self.yview)
        self.config(yscrollcommand=self.scrollbar.set)


class ButtonRow(tk.Frame):
    """Ряд кнопок в два ряда для компактности"""
    
    def __init__(self, parent, buttons_config, max_per_row=4, **kwargs):
        kwargs.setdefault('bg', ModernColors.BACKGROUND)
        super().__init__(parent, **kwargs)
        
        self.buttons = []
        rows = [buttons_config[i:i + max_per_row] for i in range(0, len(buttons_config), max_per_row)]
        
        for row_idx, row_buttons in enumerate(rows):
            row_frame = CompactFrame(self, padding_type='small')
            row_frame.pack(fill='x', pady=2)
            
            for col_idx, btn_config in enumerate(row_buttons):
                btn = CompactButton(
                    row_frame,
                    text=btn_config.get('text', ''),
                    style=btn_config.get('style', 'primary'),
                    width_type='button_small',
                    command=btn_config.get('command', None)
                )
                btn.pack(side='left', padx=2)
                self.buttons.append(btn)


def apply_modern_window_style(window, window_type='default'):
    """Применяет современный стиль к окну"""
    # Размер окна
    if window_type in ModernWindowConfig.WINDOW_SIZES:
        window.geometry(ModernWindowConfig.WINDOW_SIZES[window_type])
    
    # Общие свойства
    window.configure(bg=ModernColors.BACKGROUND)
    window.resizable(False, False)
    
    # Центрирование будет выполнено отдельно


def create_compact_form(parent, fields_config):
    """Создает компактную форму с полями"""
    form_frame = CompactFrame(parent, padding_type='section')
    
    entries = {}
    
    for row, field_config in enumerate(fields_config):
        field_name = field_config['name']
        field_label = field_config['label']
        field_type = field_config.get('type', 'entry')
        field_width = field_config.get('width', 'entry_width')
        
        # Метка
        label = CompactLabel(form_frame, text=field_label)
        label.grid(row=row, column=0, sticky='e', **ModernWindowConfig.PADDING['field'])
        
        # Поле ввода
        if field_type == 'entry':
            widget = CompactEntry(form_frame, width_type=field_width)
        elif field_type == 'combobox':
            widget = ttk.Combobox(
                form_frame, 
                width=ModernWindowConfig.WIDGET_SIZES[field_width],
                font=ModernWindowConfig.FONTS['entry'],
                state='readonly'
            )
        elif field_type == 'text':
            widget = CompactScrolledText(form_frame, height_type='text_height')
        
        widget.grid(row=row, column=1, **ModernWindowConfig.PADDING['field'])
        entries[field_name] = widget
    
    return form_frame, entries


def create_title_section(parent, title_text):
    """Создает секцию с заголовком"""
    title_frame = CompactFrame(parent, padding_type='section')
    title_label = CompactLabel(title_frame, text=title_text, font_type='title')
    title_label.pack(pady=(0, 10))
    return title_frame


def center_window_modern(window, parent=None):
    """Центрирует окно с учетом современных стандартов"""
    window.update_idletasks()
    
    if parent and parent.winfo_exists():
        # Центрируем относительно родительского окна
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        ww = window.winfo_width()
        wh = window.winfo_height()
        
        x = px + (pw - ww) // 2
        y = py + (ph - wh) // 2
    else:
        # Центрируем относительно экрана
        ww = window.winfo_width()
        wh = window.winfo_height()
        sw = window.winfo_screenwidth()
        sh = window.winfo_screenheight()
        
        x = (sw - ww) // 2
        y = (sh - wh) // 2
    
    window.geometry(f'+{x}+{y}')


# Применяем активную тему при импорте и подписываемся на изменения темы
try:
    if theme_manager.current_theme:
        ModernColors.apply_theme(theme_manager.current_theme)

    # Обновление палитры при смене темы
    def _on_theme_change(theme):
        ModernColors.apply_theme(theme)
    theme_manager.add_theme_change_callback(_on_theme_change)
except Exception:
    # В случае проблем с темами остаемся на значениях по умолчанию
    pass
