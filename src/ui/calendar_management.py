# -*- coding: utf-8 -*-
"""
Окно управления календарями Google.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Optional

from .ui_components import ModernColors, ModernButton, center_window


class CalendarManagementWindow(tk.Toplevel):
    """
    Окно для управления календарями Google.
    """
    
    def __init__(self, master=None, service=None):
        super().__init__(master)
        self.service = service
        self.master_window = master
        
        # Настройка окна
        self.title('Управление календарями Google')
        self.geometry('800x600')
        self.resizable(True, True)
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(master)
        
        # Центрируем окно относительно родительского
        if master:
            center_window(self, master)
            
        self.setup_ui()
        self.load_calendars()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(
            header_frame,
            text='📅 Управление календарями Google',
            font=('Arial', 16, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left')
        
        # Панель кнопок
        buttons_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        buttons_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        ModernButton(
            buttons_frame,
            text='🔄 Обновить',
            command=self.load_calendars,
            style='primary'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text='👥 Управление участниками',
            command=self.manage_calendar_members,
            style='info'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text='➕ Добавить участника',
            command=self.add_calendar_member,
            style='success'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text='➖ Удалить участника',
            command=self.remove_calendar_member,
            style='danger'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text='➕ Создать календарь',
            command=self.create_calendar,
            style='secondary'
        ).pack(side='right')
        
        # Список календарей
        list_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Создаем Treeview для списка календарей
        columns = ('name', 'owner', 'access', 'description')
        self.calendar_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        self.calendar_tree.heading('name', text='Название')
        self.calendar_tree.heading('owner', text='Владелец')
        self.calendar_tree.heading('access', text='Доступ')
        self.calendar_tree.heading('description', text='Описание')
        
        self.calendar_tree.column('name', width=250)
        self.calendar_tree.column('owner', width=200)
        self.calendar_tree.column('access', width=150)
        self.calendar_tree.column('description', width=300)
        
        # Scrollbar для списка
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.calendar_tree.yview)
        self.calendar_tree.configure(yscrollcommand=scrollbar.set)
        
        # Упаковка
        self.calendar_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Статус бар
        self.status_label = tk.Label(
            self,
            text='Готов',
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_SECONDARY,
            anchor='w',
            padx=10,
            pady=5
        )
        self.status_label.pack(fill='x', side='bottom')

    def load_calendars(self):
        """Загрузка списка календарей"""
        try:
            self.status_label.config(text='Загрузка календарей...')
            self.update()
            
            # Очищаем список
            for item in self.calendar_tree.get_children():
                self.calendar_tree.delete(item)
            
            if not self.service:
                messagebox.showerror("Ошибка", "Сервис Google API недоступен")
                return
            
            # Загружаем календари через Calendar API
            from ..api.calendar_api import create_calendar_api
            calendar_api = create_calendar_api()
            
            if calendar_api:
                calendars = calendar_api.get_calendar_list()
                
                for calendar in calendars:
                    # Выделяем календарь SPUTNIK (общий)
                    if "sputnik" in calendar.name.lower() and "общий" in calendar.name.lower():
                        calendar.name = f"🎯 {calendar.name}"  # Выделяем иконкой
                    
                    self.calendar_tree.insert('', 'end', values=(
                        calendar.name,
                        calendar.owner,
                        self._translate_role(calendar.access_role),
                        calendar.description
                    ), tags=(calendar.id,))
                
                self.status_label.config(text=f'Загружено календарей: {len(calendars)}')
            else:
                # Fallback к тестовым данным
                test_calendars = [
                    ("🎯 SPUTNIK (общий)", "admin@sputnik.com", "Владелец", "Общий календарь команды SPUTNIK"),
                    ("Основной календарь", "admin@company.com", "Владелец", "Основной рабочий календарь"),
                    ("Командный календарь", "team@company.com", "Редактор", "Календарь для командных встреч")
                ]
                
                for calendar_data in test_calendars:
                    self.calendar_tree.insert('', 'end', values=calendar_data)
                
                self.status_label.config(text=f'Загружено календарей: {len(test_calendars)} (тестовые данные)')
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить календари:\n{str(e)}")
            self.status_label.config(text='Ошибка загрузки')

    def create_calendar(self):
        """Создание нового календаря"""
        messagebox.showinfo("В разработке", "Функция создания календаря будет реализована в следующих версиях")
    
    def _translate_role(self, role: str) -> str:
        """Перевод роли на русский язык"""
        role_translations = {
            'owner': 'Владелец',
            'reader': 'Читатель',
            'writer': 'Редактор',
            'freeBusyReader': 'Просмотр занятости',
            'editor': 'Редактор'
        }
        return role_translations.get(role, role)
    
    def _get_selected_calendar_id(self) -> str:
        """Получение ID выбранного календаря"""
        selection = self.calendar_tree.selection()
        if not selection:
            return ""
        
        item = self.calendar_tree.item(selection[0])
        tags = item.get('tags', [])
        return tags[0] if tags else ""
    
    def _get_selected_calendar_name(self) -> str:
        """Получение названия выбранного календаря"""
        selection = self.calendar_tree.selection()
        if not selection:
            return ""
        
        item = self.calendar_tree.item(selection[0])
        values = item.get('values', [])
        return values[0] if values else ""
    
    def manage_calendar_members(self):
        """Открытие окна управления участниками календаря"""
        calendar_id = self._get_selected_calendar_id()
        calendar_name = self._get_selected_calendar_name()
        
        if not calendar_id:
            messagebox.showwarning("Предупреждение", "Выберите календарь для управления участниками")
            return
        
        # Открываем окно управления участниками
        CalendarMembersWindow(self, calendar_id, calendar_name)
    
    def add_calendar_member(self):
        """Быстрое добавление участника к выбранному календарю"""
        calendar_id = self._get_selected_calendar_id()
        calendar_name = self._get_selected_calendar_name()
        
        if not calendar_id:
            messagebox.showwarning("Предупреждение", "Выберите календарь для добавления участника")
            return
        
        # Диалог добавления пользователя
        AddCalendarMemberDialog(self, calendar_id, calendar_name, self.refresh_calendars)
    
    def remove_calendar_member(self):
        """Быстрое удаление участника из выбранного календаря"""
        calendar_id = self._get_selected_calendar_id()
        calendar_name = self._get_selected_calendar_name()
        
        if not calendar_id:
            messagebox.showwarning("Предупреждение", "Выберите календарь для удаления участника")
            return
        
        # Диалог удаления пользователя
        RemoveCalendarMemberDialog(self, calendar_id, calendar_name, self.refresh_calendars)
    
    def refresh_calendars(self):
        """Обновление списка календарей после изменений"""
        self.load_calendars()

    def on_closing(self):
        """Обработчик закрытия окна"""
        self.destroy()


class CalendarMembersWindow(tk.Toplevel):
    """Окно управления участниками календаря"""
    
    def __init__(self, parent, calendar_id: str, calendar_name: str):
        super().__init__(parent)
        self.parent = parent
        self.calendar_id = calendar_id
        self.calendar_name = calendar_name
        
        # Настройка окна
        self.title(f'Участники календаря: {calendar_name}')
        self.geometry('700x500')
        self.resizable(True, True)
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(parent)
        
        center_window(self, parent)
        self.setup_ui()
        self.load_members()
    
    def setup_ui(self):
        """Настройка UI окна участников"""
        # Заголовок
        header_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(
            header_frame,
            text=f'👥 Участники: {self.calendar_name}',
            font=('Arial', 14, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left')
        
        # Кнопки управления
        buttons_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        buttons_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        ModernButton(
            buttons_frame,
            text='🔄 Обновить',
            command=self.load_members,
            style='primary'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text='➕ Добавить',
            command=self.add_member,
            style='success'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text='✏️ Изменить роль',
            command=self.change_member_role,
            style='info'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text='🗑️ Удалить',
            command=self.remove_member,
            style='danger'
        ).pack(side='left', padx=(0, 8))
        
        # Список участников
        list_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        columns = ('email', 'role', 'type')
        self.members_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Настройка колонок
        self.members_tree.heading('email', text='Email участника')
        self.members_tree.heading('role', text='Роль')
        self.members_tree.heading('type', text='Тип')
        
        self.members_tree.column('email', width=350)
        self.members_tree.column('role', width=150)
        self.members_tree.column('type', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.members_tree.yview)
        self.members_tree.configure(yscrollcommand=scrollbar.set)
        
        self.members_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Статус бар
        self.status_label = tk.Label(
            self,
            text='Готов',
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_SECONDARY,
            anchor='w',
            padx=10,
            pady=5
        )
        self.status_label.pack(fill='x', side='bottom')
    
    def load_members(self):
        """Загрузка участников календаря"""
        try:
            self.status_label.config(text='Загрузка участников...')
            self.update()
            
            # Очищаем список
            for item in self.members_tree.get_children():
                self.members_tree.delete(item)
            
            # Загружаем участников через Calendar API
            from ..api.calendar_api import create_calendar_api
            calendar_api = create_calendar_api()
            
            if calendar_api:
                permissions = calendar_api.get_calendar_permissions(self.calendar_id)
                
                for permission in permissions:
                    self.members_tree.insert('', 'end', values=(
                        permission.user_email,
                        self._translate_role(permission.role),
                        permission.scope_type
                    ))
                
                self.status_label.config(text=f'Загружено участников: {len(permissions)}')
            else:
                self.status_label.config(text='Ошибка подключения к Calendar API')
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить участников:\n{str(e)}")
            self.status_label.config(text='Ошибка загрузки')
    
    def _translate_role(self, role: str) -> str:
        """Перевод роли на русский язык"""
        role_translations = {
            'owner': 'Владелец',
            'reader': 'Читатель', 
            'writer': 'Редактор',
            'freeBusyReader': 'Просмотр занятости'
        }
        return role_translations.get(role, role)
    
    def add_member(self):
        """Добавление участника"""
        AddCalendarMemberDialog(self, self.calendar_id, self.calendar_name, self.load_members)
    
    def change_member_role(self):
        """Изменение роли участника"""
        selection = self.members_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите участника для изменения роли")
            return
        
        item = self.members_tree.item(selection[0])
        values = item.get('values', [])
        if not values:
            return
        
        user_email = values[0]
        current_role = values[1]
        
        ChangeRoleDialog(self, self.calendar_id, user_email, current_role, self.load_members)
    
    def remove_member(self):
        """Удаление участника"""
        selection = self.members_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите участника для удаления")
            return
        
        item = self.members_tree.item(selection[0])
        values = item.get('values', [])
        if not values:
            return
        
        user_email = values[0]
        
        if messagebox.askyesno(
            "Подтверждение",
            f"Удалить участника {user_email} из календаря?"
        ):
            try:
                from ..api.calendar_api import create_calendar_api
                calendar_api = create_calendar_api()
                
                if calendar_api and calendar_api.remove_user_from_calendar(self.calendar_id, user_email):
                    messagebox.showinfo("Успех", f"Участник {user_email} удален из календаря")
                    self.load_members()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить участника")
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка удаления участника:\n{str(e)}")


class AddCalendarMemberDialog(tk.Toplevel):
    """Диалог добавления участника к календарю"""
    
    def __init__(self, parent, calendar_id: str, calendar_name: str, refresh_callback):
        super().__init__(parent)
        self.parent = parent
        self.calendar_id = calendar_id
        self.calendar_name = calendar_name
        self.refresh_callback = refresh_callback
        
        # Настройка окна
        self.title('Добавить участника')
        self.geometry('400x250')
        self.resizable(False, False)
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(parent)
        
        center_window(self, parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка UI диалога"""
        # Заголовок
        tk.Label(
            self,
            text=f'➕ Добавить участника к календарю:\n{self.calendar_name}',
            font=('Arial', 12, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            justify='center'
        ).pack(pady=20)
        
        # Форма
        form_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            form_frame,
            text='Email участника:',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w')
        
        self.email_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
        self.email_entry.pack(fill='x', pady=(5, 15))
        self.email_entry.focus()
        
        tk.Label(
            form_frame,
            text='Роль доступа:',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w')
        
        self.role_var = tk.StringVar(value='reader')
        role_frame = tk.Frame(form_frame, bg=ModernColors.BACKGROUND)
        role_frame.pack(fill='x', pady=(5, 15))
        
        roles = [
            ('reader', 'Читатель'),
            ('writer', 'Редактор'),
            ('owner', 'Владелец')
        ]
        
        for role_value, role_text in roles:
            tk.Radiobutton(
                role_frame,
                text=role_text,
                variable=self.role_var,
                value=role_value,
                bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_PRIMARY,
                selectcolor=ModernColors.SURFACE
            ).pack(side='left', padx=(0, 15))
        
        # Кнопки
        buttons_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        ModernButton(
            buttons_frame,
            text='✅ Добавить',
            command=self.add_member,
            style='success'
        ).pack(side='right', padx=(8, 0))
        
        ModernButton(
            buttons_frame,
            text='❌ Отмена',
            command=self.destroy,
            style='secondary'
        ).pack(side='right')
        
        # Обработка Enter
        self.bind('<Return>', lambda e: self.add_member())
    
    def add_member(self):
        """Добавление участника"""
        email = self.email_entry.get().strip()
        role = self.role_var.get()
        
        if not email:
            messagebox.showwarning("Предупреждение", "Введите email участника")
            return
        
        # Простая валидация email
        if '@' not in email or '.' not in email:
            messagebox.showwarning("Предупреждение", "Введите корректный email адрес")
            return
        
        try:
            from ..api.calendar_api import create_calendar_api
            calendar_api = create_calendar_api()
            
            if calendar_api and calendar_api.add_user_to_calendar(self.calendar_id, email, role):
                messagebox.showinfo("Успех", f"Участник {email} добавлен к календарю с ролью {role}")
                if self.refresh_callback:
                    self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить участника")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка добавления участника:\n{str(e)}")


class RemoveCalendarMemberDialog(tk.Toplevel):
    """Диалог удаления участника из календаря"""
    
    def __init__(self, parent, calendar_id: str, calendar_name: str, refresh_callback):
        super().__init__(parent)
        self.parent = parent
        self.calendar_id = calendar_id
        self.calendar_name = calendar_name
        self.refresh_callback = refresh_callback
        
        # Настройка окна
        self.title('Удалить участника')
        self.geometry('400x200')
        self.resizable(False, False)
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(parent)
        
        center_window(self, parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка UI диалога"""
        # Заголовок
        tk.Label(
            self,
            text=f'➖ Удалить участника из календаря:\n{self.calendar_name}',
            font=('Arial', 12, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            justify='center'
        ).pack(pady=20)
        
        # Форма
        form_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            form_frame,
            text='Email участника для удаления:',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w')
        
        self.email_entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
        self.email_entry.pack(fill='x', pady=(5, 15))
        self.email_entry.focus()
        
        # Кнопки
        buttons_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        ModernButton(
            buttons_frame,
            text='🗑️ Удалить',
            command=self.remove_member,
            style='danger'
        ).pack(side='right', padx=(8, 0))
        
        ModernButton(
            buttons_frame,
            text='❌ Отмена',
            command=self.destroy,
            style='secondary'
        ).pack(side='right')
        
        # Обработка Enter
        self.bind('<Return>', lambda e: self.remove_member())
    
    def remove_member(self):
        """Удаление участника"""
        email = self.email_entry.get().strip()
        
        if not email:
            messagebox.showwarning("Предупреждение", "Введите email участника")
            return
        
        if not messagebox.askyesno(
            "Подтверждение",
            f"Удалить участника {email} из календаря?"
        ):
            return
        
        try:
            from ..api.calendar_api import create_calendar_api
            calendar_api = create_calendar_api()
            
            if calendar_api and calendar_api.remove_user_from_calendar(self.calendar_id, email):
                messagebox.showinfo("Успех", f"Участник {email} удален из календаря")
                if self.refresh_callback:
                    self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить участника")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка удаления участника:\n{str(e)}")


class ChangeRoleDialog(tk.Toplevel):
    """Диалог изменения роли участника"""
    
    def __init__(self, parent, calendar_id: str, user_email: str, current_role: str, refresh_callback):
        super().__init__(parent)
        self.parent = parent
        self.calendar_id = calendar_id
        self.user_email = user_email
        self.current_role = current_role
        self.refresh_callback = refresh_callback
        
        # Настройка окна
        self.title('Изменить роль')
        self.geometry('400x220')
        self.resizable(False, False)
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(parent)
        
        center_window(self, parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка UI диалога"""
        # Заголовок
        tk.Label(
            self,
            text=f'✏️ Изменить роль участника:\n{self.user_email}',
            font=('Arial', 12, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            justify='center'
        ).pack(pady=20)
        
        # Форма
        form_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            form_frame,
            text=f'Текущая роль: {self.current_role}',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_SECONDARY
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            form_frame,
            text='Новая роль:',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w')
        
        # Определяем текущую роль в английском формате
        current_english_role = 'reader'
        for eng_role, rus_role in [('reader', 'Читатель'), ('writer', 'Редактор'), ('owner', 'Владелец')]:
            if rus_role == self.current_role:
                current_english_role = eng_role
                break
        
        self.role_var = tk.StringVar(value=current_english_role)
        role_frame = tk.Frame(form_frame, bg=ModernColors.BACKGROUND)
        role_frame.pack(fill='x', pady=(5, 15))
        
        roles = [
            ('reader', 'Читатель'),
            ('writer', 'Редактор'), 
            ('owner', 'Владелец')
        ]
        
        for role_value, role_text in roles:
            tk.Radiobutton(
                role_frame,
                text=role_text,
                variable=self.role_var,
                value=role_value,
                bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_PRIMARY,
                selectcolor=ModernColors.SURFACE
            ).pack(side='left', padx=(0, 15))
        
        # Кнопки
        buttons_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        ModernButton(
            buttons_frame,
            text='✅ Изменить',
            command=self.change_role,
            style='info'
        ).pack(side='right', padx=(8, 0))
        
        ModernButton(
            buttons_frame,
            text='❌ Отмена',
            command=self.destroy,
            style='secondary'
        ).pack(side='right')
        
        # Обработка Enter
        self.bind('<Return>', lambda e: self.change_role())
    
    def change_role(self):
        """Изменение роли участника"""
        new_role = self.role_var.get()
        
        try:
            from ..api.calendar_api import create_calendar_api
            calendar_api = create_calendar_api()
            
            if calendar_api and calendar_api.update_user_role(self.calendar_id, self.user_email, new_role):
                messagebox.showinfo("Успех", f"Роль участника {self.user_email} изменена на {new_role}")
                if self.refresh_callback:
                    self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось изменить роль участника")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка изменения роли:\n{str(e)}")


def open_calendar_management(master=None, service=None):
    """
    Открытие окна управления календарями.
    
    Args:
        master: Родительское окно
        service: Сервис Google API
    """
    try:
        window = CalendarManagementWindow(master, service)
        window.protocol("WM_DELETE_WINDOW", window.on_closing)
        return window
    except Exception as e:
        messagebox.showerror(
            "Ошибка",
            f"Не удалось открыть окно управления календарями:\n{str(e)}"
        )
        return None