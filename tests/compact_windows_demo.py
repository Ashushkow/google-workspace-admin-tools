#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация обновленных компактных окон с современным дизайном
"""

import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.ui.modern_styles import (ModernWindowConfig, CompactFrame, CompactLabel, 
                                 CompactEntry, CompactButton, CompactListbox,
                                 apply_modern_window_style, create_title_section, 
                                 center_window_modern, ButtonRow)
from src.ui.ui_components import ModernColors


class CompactWindowDemo:
    """Демонстрация компактных окон"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Демонстрация компактных окон")
        self.root.geometry("400x300")
        self.root.configure(bg=ModernColors.BACKGROUND)
        
        self.create_demo_ui()
        
    def create_demo_ui(self):
        """Создание демонстрационного интерфейса"""
        # Заголовок
        title_frame = create_title_section(self.root, "Демонстрация компактных окон")
        title_frame.pack(fill='x', **ModernWindowConfig.PADDING['window'])
        
        # Главный фрейм
        main_frame = CompactFrame(self.root, padding_type='section')
        main_frame.pack(fill='both', expand=True, **ModernWindowConfig.PADDING['window'])
        
        # Кнопки для демонстрации
        button_configs = [
            {'text': '👤 Создать пользователя', 'command': self.show_create_user, 'style': 'primary'},
            {'text': '✏️ Редактировать пользователя', 'command': self.show_edit_user, 'style': 'secondary'},
            {'text': '👥 Управление группами', 'command': self.show_group_management, 'style': 'info'},
            {'text': '📧 Asana приглашение', 'command': self.show_asana_invite, 'style': 'success'},
            {'text': '📋 Журнал ошибок', 'command': self.show_error_log, 'style': 'warning'},
            {'text': '🔗 FreeIPA управление', 'command': self.show_freeipa, 'style': 'danger'}
        ]
        
        # Кнопки в два ряда для компактности
        buttons_row = ButtonRow(main_frame, button_configs, max_per_row=2)
        buttons_row.pack(fill='x', pady=20)
        
        # Информация о изменениях
        info_frame = CompactFrame(main_frame, padding_type='small')
        info_frame.pack(fill='x', pady=(20, 0))
        
        CompactLabel(info_frame, text="Улучшения в дизайне:", font_type='subtitle').pack(anchor='w')
        
        improvements = [
            "✅ Компактные размеры окон",
            "✅ Современные цвета и шрифты",
            "✅ Кнопки в два ряда",
            "✅ Единообразный стиль",
            "✅ Улучшенная читаемость",
            "✅ Следование UX/UI трендам"
        ]
        
        for improvement in improvements:
            CompactLabel(info_frame, text=improvement, font_type='small').pack(anchor='w', pady=1)
    
    def show_create_user(self):
        """Демонстрация окна создания пользователя"""
        try:
            from src.ui.user_windows import CreateUserWindow
            # Имитируем сервис
            window = CreateUserWindow(self.root, service=None)
        except Exception as e:
            messagebox.showinfo("Демонстрация", f"Окно создания пользователя\nРазмер: {ModernWindowConfig.WINDOW_SIZES['create_user']}")
    
    def show_edit_user(self):
        """Демонстрация окна редактирования пользователя"""
        try:
            from src.ui.user_windows import EditUserWindow
            window = EditUserWindow(self.root, service=None)
        except Exception as e:
            messagebox.showinfo("Демонстрация", f"Окно редактирования пользователя\nРазмер: {ModernWindowConfig.WINDOW_SIZES['edit_user']}")
    
    def show_group_management(self):
        """Демонстрация окна управления группами"""
        try:
            from src.ui.group_management import GroupManagementWindow
            window = GroupManagementWindow(self.root, service=None)
        except Exception as e:
            messagebox.showinfo("Демонстрация", f"Окно управления группами\nРазмер: {ModernWindowConfig.WINDOW_SIZES['group_management']}")
    
    def show_asana_invite(self):
        """Демонстрация окна Asana приглашения"""
        try:
            from src.ui.additional_windows import AsanaInviteWindow
            window = AsanaInviteWindow(self.root)
        except Exception as e:
            messagebox.showinfo("Демонстрация", f"Окно Asana приглашения\nРазмер: {ModernWindowConfig.WINDOW_SIZES['asana_invite']}")
    
    def show_error_log(self):
        """Демонстрация окна журнала ошибок"""
        try:
            from src.ui.additional_windows import ErrorLogWindow
            window = ErrorLogWindow(self.root)
        except Exception as e:
            messagebox.showinfo("Демонстрация", f"Окно журнала ошибок\nРазмер: {ModernWindowConfig.WINDOW_SIZES['error_log']}")
    
    def show_freeipa(self):
        """Демонстрация окна FreeIPA"""
        try:
            from src.ui.freeipa_management import FreeIPAManagementWindow
            window = FreeIPAManagementWindow(self.root)
        except Exception as e:
            messagebox.showinfo("Демонстрация", f"Окно FreeIPA управления\nРазмер: {ModernWindowConfig.WINDOW_SIZES['freeipa_management']}")
    
    def run(self):
        """Запуск демонстрации"""
        self.root.mainloop()


if __name__ == "__main__":
    demo = CompactWindowDemo()
    demo.run()
