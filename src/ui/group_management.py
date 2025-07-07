# -*- coding: utf-8 -*-
"""
Продвинутое управление группами - создание, редактирование, удаление и управление членством.
"""

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from typing import Any, Optional, List, Dict

from .ui_components import ModernColors, ModernButton, center_window
from ..api.groups_api import (
    list_groups, create_group, delete_group, update_group,
    get_group_members, add_user_to_group, remove_user_from_group
)
from ..api.users_api import get_user_list
from ..utils.data_cache import data_cache


class GroupManagementWindow(tk.Toplevel):
    """
    Окно для продвинутого управления группами.
    Включает создание, редактирование, удаление групп и управление членством.
    """
    
    def __init__(self, master=None, service=None):
        super().__init__(master)
        self.service = service
        self.title('Управление группами')
        self.geometry('800x600')
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(master)
        if master:
            center_window(self, master)
            
        self.selected_group = None
        self.setup_ui()
        self.load_groups()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        title_label = tk.Label(
            self, text='Управление группами',
            font=('Arial', 16, 'bold'), bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        title_label.pack(pady=(15, 20))
        
        # Основной контейнер
        main_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Левая панель - список групп
        left_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Кнопки управления группами
        group_buttons_frame = tk.Frame(left_frame, bg=ModernColors.BACKGROUND)
        group_buttons_frame.pack(fill='x', pady=(0, 10))
        
        ModernButton(
            group_buttons_frame, text='Создать группу',
            command=self.create_group, style='primary'
        ).pack(side='left', padx=(0, 5))
        
        ModernButton(
            group_buttons_frame, text='Редактировать',
            command=self.edit_group, style='secondary'
        ).pack(side='left', padx=(0, 5))
        
        ModernButton(
            group_buttons_frame, text='Удалить',
            command=self.delete_group, style='danger'
        ).pack(side='left', padx=(0, 5))
        
        ModernButton(
            group_buttons_frame, text='Обновить',
            command=self.load_groups, style='secondary'
        ).pack(side='right')
        
        # Список групп
        tk.Label(left_frame, text='Группы:', font=('Arial', 12, 'bold'),
                bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(anchor='w')
        
        groups_frame = tk.Frame(left_frame, bg=ModernColors.BACKGROUND)
        groups_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        # Treeview для групп
        self.groups_tree = ttk.Treeview(
            groups_frame, columns=('email', 'members'), show='tree headings',
            height=15
        )
        
        self.groups_tree.heading('#0', text='Название')
        self.groups_tree.heading('email', text='Email')
        self.groups_tree.heading('members', text='Участники')
        
        self.groups_tree.column('#0', width=200)
        self.groups_tree.column('email', width=200)
        self.groups_tree.column('members', width=80)
        
        groups_scrollbar = ttk.Scrollbar(groups_frame, orient='vertical', 
                                       command=self.groups_tree.yview)
        self.groups_tree.configure(yscrollcommand=groups_scrollbar.set)
        
        self.groups_tree.pack(side='left', fill='both', expand=True)
        groups_scrollbar.pack(side='right', fill='y')
        
        self.groups_tree.bind('<<TreeviewSelect>>', self.on_group_select)
        
        # Правая панель - участники группы
        right_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Кнопки управления участниками
        members_buttons_frame = tk.Frame(right_frame, bg=ModernColors.BACKGROUND)
        members_buttons_frame.pack(fill='x', pady=(0, 10))
        
        ModernButton(
            members_buttons_frame, text='Добавить участника',
            command=self.add_member, style='primary'
        ).pack(side='left', padx=(0, 5))
        
        ModernButton(
            members_buttons_frame, text='Удалить участника',
            command=self.remove_member, style='danger'
        ).pack(side='left', padx=(0, 5))
        
        # Список участников
        tk.Label(right_frame, text='Участники группы:', font=('Arial', 12, 'bold'),
                bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(anchor='w')
        
        members_frame = tk.Frame(right_frame, bg=ModernColors.BACKGROUND)
        members_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        # Listbox для участников
        self.members_listbox = tk.Listbox(
            members_frame, font=('Arial', 10),
            bg='white', fg=ModernColors.TEXT_PRIMARY,
            selectbackground=ModernColors.PRIMARY
        )
        
        members_scrollbar = tk.Scrollbar(members_frame, orient='vertical',
                                       command=self.members_listbox.yview)
        self.members_listbox.configure(yscrollcommand=members_scrollbar.set)
        
        self.members_listbox.pack(side='left', fill='both', expand=True)
        members_scrollbar.pack(side='right', fill='y')
        
        # Кнопка закрытия
        ModernButton(
            self, text='Закрыть', command=self.destroy, style='secondary'
        ).pack(pady=(10, 0))

    def load_groups(self):
        """Загрузка списка групп"""
        if not self.service:
            messagebox.showerror('Ошибка', 'Сервис Google API недоступен')
            return
            
        try:
            # Очищаем список
            for item in self.groups_tree.get_children():
                self.groups_tree.delete(item)
            
            groups = list_groups(self.service)
            
            for group in groups:
                name = group.get('name', 'Без названия')
                email = group.get('email', '')
                members_count = group.get('directMembersCount', 0)
                
                self.groups_tree.insert('', 'end', text=name, 
                                      values=(email, members_count))
                
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка загрузки групп: {str(e)}')

    def on_group_select(self, event):
        """Обработка выбора группы"""
        selection = self.groups_tree.selection()
        if not selection:
            return
            
        item = self.groups_tree.item(selection[0])
        group_email = item['values'][0]
        
        if group_email:
            self.selected_group = group_email
            self.load_group_members(group_email)

    def load_group_members(self, group_email: str):
        """Загрузка участников группы"""
        try:
            self.members_listbox.delete(0, tk.END)
            
            members = get_group_members(self.service, group_email)
            
            for member in members:
                member_email = member.get('email', '')
                member_name = member.get('name', member_email)
                display_text = f"{member_name} ({member_email})"
                self.members_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка загрузки участников: {str(e)}')

    def create_group(self):
        """Создание новой группы"""
        dialog = GroupEditDialog(self, self.service, mode='create')
        self.wait_window(dialog)
        
        if dialog.result:
            self.load_groups()

    def edit_group(self):
        """Редактирование выбранной группы"""
        if not self.selected_group:
            messagebox.showwarning('Предупреждение', 'Выберите группу для редактирования')
            return
            
        # Получаем данные группы
        try:
            groups = list_groups(self.service)
            group_data = next((g for g in groups if g.get('email') == self.selected_group), None)
            
            if not group_data:
                messagebox.showerror('Ошибка', 'Группа не найдена')
                return
                
            dialog = GroupEditDialog(self, self.service, mode='edit', group_data=group_data)
            self.wait_window(dialog)
            
            if dialog.result:
                self.load_groups()
                
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка при редактировании группы: {str(e)}')

    def delete_group(self):
        """Удаление выбранной группы"""
        if not self.selected_group:
            messagebox.showwarning('Предупреждение', 'Выберите группу для удаления')
            return
            
        result = messagebox.askyesno(
            'Подтверждение', 
            f'Вы уверены, что хотите удалить группу {self.selected_group}?\n'
            'Это действие нельзя отменить!'
        )
        
        if result:
            try:
                success = delete_group(self.service, self.selected_group)
                if success:
                    messagebox.showinfo('Успех', 'Группа успешно удалена')
                    self.selected_group = None
                    self.members_listbox.delete(0, tk.END)
                    self.load_groups()
                else:
                    messagebox.showerror('Ошибка', 'Не удалось удалить группу')
            except Exception as e:
                messagebox.showerror('Ошибка', f'Ошибка удаления группы: {str(e)}')

    def add_member(self):
        """Добавление участника в группу"""
        if not self.selected_group:
            messagebox.showwarning('Предупреждение', 'Выберите группу')
            return
            
        # Диалог выбора пользователя
        dialog = UserSelectionDialog(self, self.service)
        self.wait_window(dialog)
        
        if dialog.result:
            user_email = dialog.result
            try:
                success = add_user_to_group(self.service, user_email, self.selected_group)
                if success:
                    messagebox.showinfo('Успех', f'Пользователь {user_email} добавлен в группу')
                    self.load_group_members(self.selected_group)
                else:
                    messagebox.showerror('Ошибка', 'Не удалось добавить пользователя в группу')
            except Exception as e:
                messagebox.showerror('Ошибка', f'Ошибка добавления пользователя: {str(e)}')

    def remove_member(self):
        """Удаление участника из группы"""
        if not self.selected_group:
            messagebox.showwarning('Предупреждение', 'Выберите группу')
            return
            
        selection = self.members_listbox.curselection()
        if not selection:
            messagebox.showwarning('Предупреждение', 'Выберите участника для удаления')
            return
            
        member_text = self.members_listbox.get(selection[0])
        # Извлекаем email из строки формата "Name (email)"
        member_email = member_text.split('(')[-1].rstrip(')')
        
        result = messagebox.askyesno(
            'Подтверждение',
            f'Удалить {member_email} из группы {self.selected_group}?'
        )
        
        if result:
            try:
                success = remove_user_from_group(self.service, member_email, self.selected_group)
                if success:
                    messagebox.showinfo('Успех', f'Пользователь {member_email} удален из группы')
                    self.load_group_members(self.selected_group)
                else:
                    messagebox.showerror('Ошибка', 'Не удалось удалить пользователя из группы')
            except Exception as e:
                messagebox.showerror('Ошибка', f'Ошибка удаления пользователя: {str(e)}')


class GroupEditDialog(tk.Toplevel):
    """Диалог для создания/редактирования группы"""
    
    def __init__(self, master, service, mode='create', group_data=None):
        super().__init__(master)
        self.service = service
        self.mode = mode
        self.group_data = group_data or {}
        self.result = None
        
        self.title('Создание группы' if mode == 'create' else 'Редактирование группы')
        self.geometry('400x300')
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(master)
        self.grab_set()
        center_window(self, master)
        
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        title_text = 'Создание новой группы' if self.mode == 'create' else 'Редактирование группы'
        title_label = tk.Label(
            self, text=title_text,
            font=('Arial', 14, 'bold'), bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        title_label.pack(pady=(15, 20))
        
        # Форма
        form_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        form_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Название группы
        tk.Label(form_frame, text='Название группы:', font=('Arial', 11),
                bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(anchor='w')
        
        self.name_entry = tk.Entry(form_frame, font=('Arial', 11), width=40)
        self.name_entry.pack(fill='x', pady=(5, 10))
        
        # Email группы
        tk.Label(form_frame, text='Email группы:', font=('Arial', 11),
                bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(anchor='w')
        
        self.email_entry = tk.Entry(form_frame, font=('Arial', 11), width=40)
        self.email_entry.pack(fill='x', pady=(5, 10))
        
        # Описание
        tk.Label(form_frame, text='Описание:', font=('Arial', 11),
                bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(anchor='w')
        
        self.description_text = tk.Text(form_frame, height=4, font=('Arial', 11))
        self.description_text.pack(fill='x', pady=(5, 10))
        
        # Заполняем поля при редактировании
        if self.mode == 'edit' and self.group_data:
            self.name_entry.insert(0, self.group_data.get('name', ''))
            self.email_entry.insert(0, self.group_data.get('email', ''))
            self.description_text.insert(1.0, self.group_data.get('description', ''))
            
        # Кнопки
        button_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        save_text = 'Создать' if self.mode == 'create' else 'Сохранить'
        ModernButton(
            button_frame, text=save_text,
            command=self.save_group, style='primary'
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame, text='Отмена',
            command=self.destroy, style='secondary'
        ).pack(side='right')

    def save_group(self):
        """Сохранение группы"""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        description = self.description_text.get(1.0, tk.END).strip()
        
        if not name or not email:
            messagebox.showwarning('Предупреждение', 'Заполните название и email группы')
            return
            
        try:
            if self.mode == 'create':
                success = create_group(self.service, name, email, description)
                if success:
                    messagebox.showinfo('Успех', 'Группа успешно создана')
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror('Ошибка', 'Не удалось создать группу')
            else:
                success = update_group(self.service, email, name, description)
                if success:
                    messagebox.showinfo('Успех', 'Группа успешно обновлена')
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror('Ошибка', 'Не удалось обновить группу')
                    
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка сохранения группы: {str(e)}')


class UserSelectionDialog(tk.Toplevel):
    """Диалог для выбора пользователя"""
    
    def __init__(self, master, service):
        super().__init__(master)
        self.service = service
        self.result = None
        
        self.title('Выбор пользователя')
        self.geometry('500x400')
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(master)
        self.grab_set()
        center_window(self, master)
        
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        title_label = tk.Label(
            self, text='Выберите пользователя',
            font=('Arial', 14, 'bold'), bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        title_label.pack(pady=(15, 20))
        
        # Поиск
        search_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        search_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(search_frame, text='Поиск:', font=('Arial', 11),
                bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(anchor='w')
        
        self.search_entry = tk.Entry(search_frame, font=('Arial', 11))
        self.search_entry.pack(fill='x', pady=(5, 0))
        self.search_entry.bind('<KeyRelease>', self.filter_users)
        
        # Список пользователей
        users_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        users_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        self.users_listbox = tk.Listbox(
            users_frame, font=('Arial', 10),
            bg='white', fg=ModernColors.TEXT_PRIMARY,
            selectbackground=ModernColors.PRIMARY
        )
        
        users_scrollbar = tk.Scrollbar(users_frame, orient='vertical',
                                     command=self.users_listbox.yview)
        self.users_listbox.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_listbox.pack(side='left', fill='both', expand=True)
        users_scrollbar.pack(side='right', fill='y')
        
        self.users_listbox.bind('<Double-Button-1>', self.select_user)
        
        # Кнопки
        button_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ModernButton(
            button_frame, text='Выбрать',
            command=self.select_user, style='primary'
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame, text='Отмена',
            command=self.destroy, style='secondary'
        ).pack(side='right')

    def load_users(self):
        """Загрузка списка пользователей"""
        try:
            self.all_users = get_user_list(self.service)
            self.filter_users()
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка загрузки пользователей: {str(e)}')

    def filter_users(self, event=None):
        """Фильтрация пользователей по поисковому запросу"""
        search_text = self.search_entry.get().lower()
        
        self.users_listbox.delete(0, tk.END)
        
        for user in self.all_users:
            email = user.get('primaryEmail', '')
            name = user.get('name', {}).get('fullName', '')
            
            if search_text in email.lower() or search_text in name.lower():
                display_text = f"{name} ({email})"
                self.users_listbox.insert(tk.END, display_text)

    def select_user(self, event=None):
        """Выбор пользователя"""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning('Предупреждение', 'Выберите пользователя')
            return
            
        user_text = self.users_listbox.get(selection[0])
        # Извлекаем email из строки формата "Name (email)"
        user_email = user_text.split('(')[-1].rstrip(')')
        
        self.result = user_email
        self.destroy()
