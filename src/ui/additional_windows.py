# -*- coding: utf-8 -*-
"""
Окна для работы с группами и дополнительные диалоги.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import requests
from typing import Any, Optional

from .ui_components import ModernColors, ModernButton, center_window
from ..api.groups_api import list_groups, add_user_to_group
from ..config.enhanced_config import config


class AsanaInviteWindow(tk.Toplevel):
    """
    Окно для отправки приглашений в Asana.
    Позволяет ввести email и имя, получить workspace ID и отправить приглашение через API Asana.
    """
    
    def __init__(self, master=None):
        super().__init__(master)
        self.title('Приглашение в Asana')
        self.geometry('420x270')
        self.resizable(False, False)
        self.configure(bg='#f7f7fa')
        self.transient(master)
        if master:
            center_window(self, master)
            
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        tk.Label(self, text='Отправка приглашения в Asana', 
                font=('Arial', 13, 'bold'), bg='#f7f7fa').grid(
                row=0, column=0, columnspan=2, pady=(12, 2))
        
        tk.Label(self, text='Email:', anchor='e', bg='#f7f7fa').grid(
            row=1, column=0, sticky='e', padx=10, pady=8)
        self.entry_email = tk.Entry(self, width=32, font=('Arial', 11))
        self.entry_email.grid(row=1, column=1, padx=5)
        
        tk.Label(self, text='Имя:', anchor='e', bg='#f7f7fa').grid(
            row=2, column=0, sticky='e', padx=10, pady=8)
        self.entry_name = tk.Entry(self, width=32, font=('Arial', 11))
        self.entry_name.grid(row=2, column=1, padx=5)
        
        self.btn_invite = tk.Button(
            self, text='Отправить приглашение', command=self.send_invite,
            bg='#4caf50', fg='white', font=('Arial', 11, 'bold'), 
            activebackground='#388e3c')
        self.btn_invite.grid(row=3, column=0, columnspan=2, pady=15, ipadx=10, ipady=2)
        
        self.txt_result = scrolledtext.ScrolledText(
            self, width=48, height=5, wrap=tk.WORD, font=('Arial', 10))
        self.txt_result.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
        self.txt_result.config(state=tk.DISABLED)
        
        self.btn_close = tk.Button(
            self, text='Закрыть', command=self.destroy,
            bg='#e57373', fg='white', font=('Arial', 10, 'bold'), 
            activebackground='#b71c1c')
        self.btn_close.grid(row=5, column=0, columnspan=2, pady=(5, 10), ipadx=10, ipady=1)

    def send_invite(self):
        """Отправка приглашения в Asana через API"""
        email = self.entry_email.get().strip()
        name = self.entry_name.get().strip()
        
        self.txt_result.config(state=tk.NORMAL)
        self.txt_result.delete(1.0, tk.END)
        
        if not email or not name:
            self.txt_result.insert(tk.END, 'Пожалуйста, заполните все поля!\n')
            self.txt_result.config(state=tk.DISABLED)
            self.entry_email.focus_set()
            return
        
        # Получаем настройки Asana из конфигурации
        settings = config.settings
        asana_token = settings.get('asana_token', 
                                  '2/1204610324552816/1210701765324768:d0419d24cf3e05b6479dd294cec6fd8a')
        workspace_name = settings.get('asana_workspace', 'sputnik8.com')
        
        headers = {'Authorization': f'Bearer {asana_token}'}
        
        try:
            # Получаем список рабочих пространств
            ws_resp = requests.get('https://app.asana.com/api/1.0/workspaces', headers=headers)
            if ws_resp.status_code != 200:
                self.txt_result.insert(tk.END, f'Ошибка получения workspaces: {ws_resp.text}\n')
                self.txt_result.config(state=tk.DISABLED)
                return
            
            workspaces = ws_resp.json().get('data', [])
            ws_id = next((ws.get('gid') for ws in workspaces 
                         if ws.get('name') == workspace_name), None)
            
            if not ws_id:
                self.txt_result.insert(tk.END, 
                                     f'Рабочее пространство {workspace_name} не найдено.\n')
                self.txt_result.config(state=tk.DISABLED)
                return
            
            # Отправляем приглашение пользователю
            invite_url = f'https://app.asana.com/api/1.0/workspaces/{ws_id}/addUser'
            data = {'data': {'user': email}}
            invite_resp = requests.post(
                invite_url, 
                headers={**headers, 'Content-Type': 'application/json'}, 
                json=data
            )
            
            if invite_resp.status_code in (200, 201):
                self.txt_result.insert(tk.END, f'Приглашение отправлено на {email}\n')
            else:
                self.txt_result.insert(tk.END, 
                                     f'Ошибка отправки приглашения: {invite_resp.text}\n')
                
        except Exception as e:
            self.txt_result.insert(tk.END, f'Ошибка: {str(e)}\n')
        finally:
            self.txt_result.config(state=tk.DISABLED)


class AddToGroupWindow(tk.Toplevel):
    """
    Окно для добавления пользователя в группу.
    Позволяет выбрать пользователя и группу, затем добавить пользователя в выбранную группу.
    """
    
    def __init__(self, master=None, service=None):
        super().__init__(master)
        self.service = service
        self.title('Добавить в группу')
        self.geometry('480x400')
        self.resizable(False, False)
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(master)
        if master:
            center_window(self, master)
            
        self.setup_ui()
        self.load_groups()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        title_label = tk.Label(
            self, text='Добавление пользователя в группу',
            font=('Arial', 14, 'bold'), bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        title_label.pack(pady=(15, 20))
        
        # Email пользователя
        email_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        email_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(email_frame, text='Email пользователя:', 
                font=('Arial', 11), bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_PRIMARY).pack(anchor='w')
        
        self.entry_email = tk.Entry(
            email_frame, width=50, font=('Arial', 11),
            bg='white', fg=ModernColors.TEXT_PRIMARY,
            relief='solid', bd=1
        )
        self.entry_email.pack(fill='x', pady=(5, 0))
        
        # Выбор группы
        group_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        group_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        tk.Label(group_frame, text='Выберите группу:', 
                font=('Arial', 11), bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_PRIMARY).pack(anchor='w')
        
        # Listbox для групп
        listbox_frame = tk.Frame(group_frame, bg=ModernColors.BACKGROUND)
        listbox_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        self.listbox_groups = tk.Listbox(
            listbox_frame, font=('Arial', 10),
            bg='white', fg=ModernColors.TEXT_PRIMARY,
            selectbackground=ModernColors.PRIMARY,
            relief='solid', bd=1
        )
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.listbox_groups.pack(side='left', fill='both', expand=True)
        self.listbox_groups.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox_groups.yview)
        
        # Кнопки
        button_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        button_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        ModernButton(
            button_frame, text='Добавить в группу',
            command=self.add_to_group, style='primary'
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame, text='Закрыть',
            command=self.destroy, style='secondary'
        ).pack(side='right')

    def load_groups(self):
        """Загрузка списка групп"""
        if not self.service:
            messagebox.showerror('Ошибка', 'Сервис Google API недоступен')
            return
            
        try:
            groups = list_groups(self.service)
            self.listbox_groups.delete(0, tk.END)
            
            for group in groups:
                display_text = f"{group.get('name', 'Без названия')} ({group.get('email', '')})"
                self.listbox_groups.insert(tk.END, display_text)
                
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка загрузки групп: {str(e)}')

    def add_to_group(self):
        """Добавление пользователя в выбранную группу"""
        user_email = self.entry_email.get().strip()
        
        if not user_email:
            messagebox.showwarning('Предупреждение', 'Введите email пользователя')
            return
            
        selection = self.listbox_groups.curselection()
        if not selection:
            messagebox.showwarning('Предупреждение', 'Выберите группу')
            return
            
        try:
            groups = list_groups(self.service)
            selected_group = groups[selection[0]]
            group_email = selected_group.get('email')
            
            if not group_email:
                messagebox.showerror('Ошибка', 'У выбранной группы нет email')
                return
                
            success = add_user_to_group(self.service, user_email, group_email)
            
            if success:
                messagebox.showinfo(
                    'Успех', 
                    f'Пользователь {user_email} добавлен в группу {selected_group.get("name")}'
                )
                self.destroy()
            else:
                messagebox.showerror('Ошибка', 'Не удалось добавить пользователя в группу')
                
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка при добавлении в группу: {str(e)}')


class ErrorLogWindow(tk.Toplevel):
    """
    Окно для просмотра логов ошибок.
    """
    
    def __init__(self, master=None):
        super().__init__(master)
        self.title('Журнал ошибок')
        self.geometry('600x400')
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(master)
        if master:
            center_window(self, master)
            
        self.setup_ui()
        self.load_logs()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        title_label = tk.Label(
            self, text='Журнал ошибок приложения',
            font=('Arial', 14, 'bold'), bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        title_label.pack(pady=(15, 10))
        
        # Текстовое поле для логов
        text_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        text_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        self.text_logs = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, font=('Consolas', 10),
            bg='white', fg=ModernColors.TEXT_PRIMARY
        )
        self.text_logs.pack(fill='both', expand=True)
        
        # Кнопки
        button_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ModernButton(
            button_frame, text='Обновить',
            command=self.load_logs, style='primary'
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame, text='Очистить',
            command=self.clear_logs, style='secondary'
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            button_frame, text='Закрыть',
            command=self.destroy, style='secondary'
        ).pack(side='right')

    def load_logs(self):
        """Загрузка логов из файла"""
        try:
            with open('admin_log.json', 'r', encoding='utf-8') as f:
                import json
                logs = json.load(f)
                
            self.text_logs.delete(1.0, tk.END)
            
            for log_entry in logs:
                timestamp = log_entry.get('timestamp', 'Неизвестно')
                level = log_entry.get('level', 'INFO')
                message = log_entry.get('message', '')
                
                log_line = f"[{timestamp}] {level}: {message}\n"
                self.text_logs.insert(tk.END, log_line)
                
        except FileNotFoundError:
            self.text_logs.delete(1.0, tk.END)
            self.text_logs.insert(tk.END, "Файл логов не найден.\n")
        except Exception as e:
            self.text_logs.delete(1.0, tk.END)
            self.text_logs.insert(tk.END, f"Ошибка чтения логов: {str(e)}\n")

    def clear_logs(self):
        """Очистка логов"""
        try:
            with open('admin_log.json', 'w', encoding='utf-8') as f:
                import json
                json.dump([], f)
            self.load_logs()
            messagebox.showinfo('Успех', 'Логи очищены')
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось очистить логи: {str(e)}')
