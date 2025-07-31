# -*- coding: utf-8 -*-
"""
Улучшенное управление участниками групп с интеграцией FreeIPA.
"""

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from typing import Any, Optional, List, Dict
import logging

from .ui_components import ModernColors, ModernButton, center_window

# Условный импорт FreeIPA
try:
    from ..services.freeipa_client import FreeIPAService
    FREEIPA_AVAILABLE = True
except ImportError:
    FreeIPAService = None
    FREEIPA_AVAILABLE = False

logger = logging.getLogger(__name__)


class GroupMembersManagementWindow(tk.Toplevel):
    """
    Окно для управления участниками групп с поддержкой FreeIPA.
    """
    
    def __init__(self, master=None, group_id=None, group_name=None, 
                 google_service=None, freeipa_service=None):
        super().__init__(master)
        
        self.group_id = group_id
        self.group_name = group_name or "Неизвестная группа"
        self.google_service = google_service
        self.freeipa_service = freeipa_service
        
        self.title(f'Участники группы: {self.group_name}')
        self.geometry('900x700')
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(master)
        
        if master:
            center_window(self, master)
            
        self.google_members = []
        self.freeipa_members = []
        self.freeipa_users = []
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        title_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        title_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        title_label = tk.Label(
            title_frame, 
            text=f'👥 Участники группы: {self.group_name}',
            font=('Arial', 16, 'bold'), 
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        title_label.pack(side='left')
        
        # Кнопка обновления
        ModernButton(
            title_frame, 
            text='🔄 Обновить',
            command=self.load_data, 
            style='secondary'
        ).pack(side='right')
        
        # Основной контейнер
        main_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Создаем Notebook для разделения источников
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Вкладка Google Workspace
        self.setup_google_tab()
        
        # Вкладка FreeIPA (если доступна)
        if FREEIPA_AVAILABLE and self.freeipa_service:
            self.setup_freeipa_tab()
        
        # Кнопки действий
        self.setup_action_buttons(main_frame)

    def setup_google_tab(self):
        """Настройка вкладки Google Workspace"""
        google_frame = ttk.Frame(self.notebook)
        self.notebook.add(google_frame, text="📊 Google Workspace")
        
        # Контейнер
        container = tk.Frame(google_frame, bg=ModernColors.BACKGROUND)
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Текущие участники Google
        current_frame = tk.LabelFrame(
            container,
            text="Текущие участники Google Workspace",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 11, 'bold')
        )
        current_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Treeview для участников Google
        columns = ('email', 'name', 'role', 'status')
        self.google_members_tree = ttk.Treeview(
            current_frame, 
            columns=columns, 
            show='headings',
            height=12
        )
        
        # Настройка колонок
        self.google_members_tree.heading('email', text='Email')
        self.google_members_tree.heading('name', text='Имя')
        self.google_members_tree.heading('role', text='Роль')
        self.google_members_tree.heading('status', text='Статус')
        
        self.google_members_tree.column('email', width=250)
        self.google_members_tree.column('name', width=200)
        self.google_members_tree.column('role', width=100)
        self.google_members_tree.column('status', width=100)
        
        # Скроллбар для Google
        google_scroll = ttk.Scrollbar(
            current_frame, 
            orient='vertical', 
            command=self.google_members_tree.yview
        )
        self.google_members_tree.configure(yscrollcommand=google_scroll.set)
        
        self.google_members_tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        google_scroll.pack(side='right', fill='y', pady=10, padx=(0, 10))

    def setup_freeipa_tab(self):
        """Настройка вкладки FreeIPA"""
        freeipa_frame = ttk.Frame(self.notebook)
        self.notebook.add(freeipa_frame, text="🔗 FreeIPA")
        
        # Контейнер
        container = tk.Frame(freeipa_frame, bg=ModernColors.BACKGROUND)
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Разделяем на две части: участники и доступные пользователи
        left_frame = tk.Frame(container, bg=ModernColors.BACKGROUND)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        right_frame = tk.Frame(container, bg=ModernColors.BACKGROUND)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Текущие участники FreeIPA
        members_frame = tk.LabelFrame(
            left_frame,
            text="Участники группы в FreeIPA",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 11, 'bold')
        )
        members_frame.pack(fill='both', expand=True)
        
        # Listbox для участников FreeIPA
        self.freeipa_members_listbox = tk.Listbox(
            members_frame,
            font=('Arial', 10),
            bg='white',
            fg=ModernColors.TEXT_PRIMARY,
            selectbackground=ModernColors.PRIMARY,
            selectmode='extended'
        )
        
        members_scroll = tk.Scrollbar(
            members_frame,
            orient='vertical',
            command=self.freeipa_members_listbox.yview
        )
        self.freeipa_members_listbox.configure(yscrollcommand=members_scroll.set)
        
        self.freeipa_members_listbox.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        members_scroll.pack(side='right', fill='y', pady=10, padx=(0, 10))
        
        # Кнопки управления участниками
        members_buttons_frame = tk.Frame(members_frame, bg=ModernColors.BACKGROUND)
        members_buttons_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ModernButton(
            members_buttons_frame,
            text='➖ Исключить из группы',
            command=self.remove_from_freeipa_group,
            style='danger'
        ).pack(side='left', padx=(0, 5))
        
        # Доступные пользователи FreeIPA
        users_frame = tk.LabelFrame(
            right_frame,
            text="Доступные пользователи FreeIPA",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 11, 'bold')
        )
        users_frame.pack(fill='both', expand=True)
        
        # Поиск пользователей
        search_frame = tk.Frame(users_frame, bg=ModernColors.BACKGROUND)
        search_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        tk.Label(
            search_frame,
            text='🔍 Поиск:',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left')
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10)
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(5, 10))
        search_entry.bind('<KeyRelease>', self.filter_users)
        
        # Listbox для доступных пользователей
        self.freeipa_users_listbox = tk.Listbox(
            users_frame,
            font=('Arial', 10),
            bg='white',
            fg=ModernColors.TEXT_PRIMARY,
            selectbackground=ModernColors.SUCCESS,
            selectmode='extended'
        )
        
        users_scroll = tk.Scrollbar(
            users_frame,
            orient='vertical',
            command=self.freeipa_users_listbox.yview
        )
        self.freeipa_users_listbox.configure(yscrollcommand=users_scroll.set)
        
        self.freeipa_users_listbox.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=5)
        users_scroll.pack(side='right', fill='y', pady=5, padx=(0, 10))
        
        # Кнопки управления пользователями
        users_buttons_frame = tk.Frame(users_frame, bg=ModernColors.BACKGROUND)
        users_buttons_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ModernButton(
            users_buttons_frame,
            text='➕ Добавить в группу',
            command=self.add_to_freeipa_group,
            style='success'
        ).pack(side='left', padx=(0, 5))
        
        ModernButton(
            users_buttons_frame,
            text='🔄 Обновить список',
            command=self.load_freeipa_users,
            style='secondary'
        ).pack(side='right')

    def setup_action_buttons(self, parent):
        """Настройка кнопок действий"""
        buttons_frame = tk.Frame(parent, bg=ModernColors.BACKGROUND)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        # Кнопка синхронизации (если доступен FreeIPA)
        if FREEIPA_AVAILABLE and self.freeipa_service:
            ModernButton(
                buttons_frame,
                text='🔄 Синхронизировать с FreeIPA',
                command=self.sync_with_freeipa,
                style='info'
            ).pack(side='left')
        
        # Кнопка закрытия
        ModernButton(
            buttons_frame,
            text='❌ Закрыть',
            command=self.destroy,
            style='secondary'
        ).pack(side='right')

    def load_data(self):
        """Загрузка данных о участниках"""
        self.load_google_members()
        if FREEIPA_AVAILABLE and self.freeipa_service:
            self.load_freeipa_members()
            self.load_freeipa_users()

    def load_google_members(self):
        """Загрузка участников Google Workspace"""
        if not self.google_service or not self.group_id:
            return
        
        try:
            # Здесь должен быть вызов к Google API для получения участников группы
            # Заглушка для демонстрации
            self.google_members = []
            
            # Очищаем дерево
            for item in self.google_members_tree.get_children():
                self.google_members_tree.delete(item)
            
            # Добавляем участников (заглушка)
            sample_members = [
                ('user1@company.com', 'Иван Иванов', 'MEMBER', 'ACTIVE'),
                ('user2@company.com', 'Петр Петров', 'OWNER', 'ACTIVE'),
                ('user3@company.com', 'Мария Сидорова', 'MEMBER', 'SUSPENDED')
            ]
            
            for email, name, role, status in sample_members:
                self.google_members_tree.insert('', 'end', values=(email, name, role, status))
                
        except Exception as e:
            logger.error(f"Ошибка загрузки участников Google: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить участников Google: {e}")

    def load_freeipa_members(self):
        """Загрузка участников группы из FreeIPA"""
        if not self.freeipa_service:
            return
        
        try:
            # Определяем тип сервиса по классу
            service_class_name = self.freeipa_service.__class__.__name__
            
            if service_class_name == 'FreeIPAService':
                # Синхронный вызов для FreeIPAService
                members = self.freeipa_service.get_group_members(self.group_name)
            else:
                # Асинхронный вызов для FreeIPAIntegration
                import asyncio
                import inspect
                
                # Проверяем, является ли метод корутиной
                if inspect.iscoroutinefunction(self.freeipa_service.get_group_members):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        members = loop.run_until_complete(self.freeipa_service.get_group_members(self.group_name))
                    finally:
                        loop.close()
                else:
                    # Обычный синхронный вызов
                    members = self.freeipa_service.get_group_members(self.group_name)
            
            self.freeipa_members = members if members else []
            
            # Очищаем список
            self.freeipa_members_listbox.delete(0, tk.END)
            
            # Добавляем участников
            for member in self.freeipa_members:
                self.freeipa_members_listbox.insert(tk.END, member)
                
        except Exception as e:
            logger.error(f"Ошибка загрузки участников FreeIPA: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить участников FreeIPA: {e}")

    def load_freeipa_users(self):
        """Загрузка всех пользователей FreeIPA"""
        if not self.freeipa_service:
            return
        
        try:
            # Определяем тип сервиса по классу
            service_class_name = self.freeipa_service.__class__.__name__
            
            if service_class_name == 'FreeIPAService':
                # Синхронный вызов для FreeIPAService
                users_data = self.freeipa_service.list_users()
            else:
                # Асинхронный вызов для FreeIPAIntegration
                import asyncio
                import inspect
                
                # Проверяем, является ли метод корутиной
                if inspect.iscoroutinefunction(self.freeipa_service.list_users):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        users_data = loop.run_until_complete(self.freeipa_service.list_users())
                    finally:
                        loop.close()
                else:
                    # Обычный синхронный вызов
                    users_data = self.freeipa_service.list_users()
            
            self.freeipa_users = [user.get('uid', [''])[0] for user in users_data if user.get('uid')]
            
            # Обновляем отображение
            self.update_users_display()
                
        except Exception as e:
            logger.error(f"Ошибка загрузки пользователей FreeIPA: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей FreeIPA: {e}")

    def update_users_display(self):
        """Обновление отображения пользователей с учетом фильтра"""
        if not hasattr(self, 'freeipa_users_listbox'):
            return
        
        # Очищаем список
        self.freeipa_users_listbox.delete(0, tk.END)
        
        # Фильтр поиска
        search_term = self.search_var.get().lower()
        
        # Добавляем пользователей, которые еще не в группе
        for user in self.freeipa_users:
            if user not in self.freeipa_members:
                if not search_term or search_term in user.lower():
                    self.freeipa_users_listbox.insert(tk.END, user)

    def filter_users(self, event=None):
        """Фильтрация пользователей по поисковому запросу"""
        self.update_users_display()

    def add_to_freeipa_group(self):
        """Добавление выбранных пользователей в группу FreeIPA"""
        if not self.freeipa_service:
            messagebox.showerror("Ошибка", "FreeIPA сервис недоступен")
            return
        
        # Получаем выбранных пользователей
        selected_indices = self.freeipa_users_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Предупреждение", "Выберите пользователей для добавления")
            return
        
        selected_users = [self.freeipa_users_listbox.get(i) for i in selected_indices]
        
        # Подтверждение
        if not messagebox.askyesno(
            "Подтверждение",
            f"Добавить {len(selected_users)} пользователей в группу '{self.group_name}'?"
        ):
            return
        
        # Добавляем пользователей
        success_count = 0
        errors = []
        
        for user in selected_users:
            try:
                # Определяем тип сервиса по классу
                service_class_name = self.freeipa_service.__class__.__name__
                
                if service_class_name == 'FreeIPAService':
                    # Синхронный вызов для FreeIPAService
                    result = self.freeipa_service.add_user_to_group(user, self.group_name)
                else:
                    # Асинхронный вызов для FreeIPAIntegration
                    import asyncio
                    import inspect
                    
                    # Проверяем, является ли метод корутиной
                    if inspect.iscoroutinefunction(self.freeipa_service.add_user_to_group):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(self.freeipa_service.add_user_to_group(user, self.group_name))
                        finally:
                            loop.close()
                    else:
                        # Обычный синхронный вызов
                        result = self.freeipa_service.add_user_to_group(user, self.group_name)
                
                if result:
                    success_count += 1
                else:
                    errors.append(f"Не удалось добавить {user}")
            except Exception as e:
                errors.append(f"Ошибка при добавлении {user}: {str(e)}")
        
        # Показываем результат
        if success_count > 0:
            messagebox.showinfo("Успех", f"Добавлено пользователей: {success_count}")
            self.load_freeipa_members()
            self.update_users_display()
        
        if errors:
            messagebox.showerror("Ошибки", "\\n".join(errors[:5]))  # Показываем первые 5 ошибок

    def remove_from_freeipa_group(self):
        """Удаление выбранных пользователей из группы FreeIPA"""
        if not self.freeipa_service:
            messagebox.showerror("Ошибка", "FreeIPA сервис недоступен")
            return
        
        # Получаем выбранных участников
        selected_indices = self.freeipa_members_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Предупреждение", "Выберите участников для удаления")
            return
        
        selected_members = [self.freeipa_members_listbox.get(i) for i in selected_indices]
        
        # Подтверждение
        if not messagebox.askyesno(
            "Подтверждение",
            f"Удалить {len(selected_members)} участников из группы '{self.group_name}'?"
        ):
            return
        
        # Удаляем участников
        success_count = 0
        errors = []
        
        for member in selected_members:
            try:
                # Определяем тип сервиса по классу
                service_class_name = self.freeipa_service.__class__.__name__
                
                if service_class_name == 'FreeIPAService':
                    # Синхронный вызов для FreeIPAService
                    result = self.freeipa_service.remove_user_from_group(member, self.group_name)
                else:
                    # Асинхронный вызов для FreeIPAIntegration
                    import asyncio
                    import inspect
                    
                    # Проверяем, является ли метод корутиной
                    if inspect.iscoroutinefunction(self.freeipa_service.remove_user_from_group):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(self.freeipa_service.remove_user_from_group(member, self.group_name))
                        finally:
                            loop.close()
                    else:
                        # Обычный синхронный вызов
                        result = self.freeipa_service.remove_user_from_group(member, self.group_name)
                
                if result:
                    success_count += 1
                else:
                    errors.append(f"Не удалось удалить {member}")
            except Exception as e:
                errors.append(f"Ошибка при удалении {member}: {str(e)}")
        
        # Показываем результат
        if success_count > 0:
            messagebox.showinfo("Успех", f"Удалено участников: {success_count}")
            self.load_freeipa_members()
            self.update_users_display()
        
        if errors:
            messagebox.showerror("Ошибки", "\\n".join(errors[:5]))

    def sync_with_freeipa(self):
        """Синхронизация участников между Google Workspace и FreeIPA"""
        if not self.freeipa_service:
            messagebox.showerror("Ошибка", "FreeIPA сервис недоступен")
            return
        
        # Здесь можно добавить логику синхронизации
        # Например, добавить всех участников Google в FreeIPA
        
        messagebox.showinfo(
            "Синхронизация",
            "Функция синхронизации будет реализована в следующих версиях"
        )


def show_group_members_management(master, group_id=None, group_name=None, 
                                 google_service=None, freeipa_service=None):
    """Функция для показа окна управления участниками группы"""
    window = GroupMembersManagementWindow(
        master=master,
        group_id=group_id,
        group_name=group_name,
        google_service=google_service,
        freeipa_service=freeipa_service
    )
    return window
