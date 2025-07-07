# -*- coding: utf-8 -*-
"""
Окна для работы с пользователями.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import string
import random
from typing import Any, Optional

from .ui_components import ModernColors, center_window
from ..api.users_api import create_user, update_user, delete_user, get_user_list


class CreateUserWindow(tk.Toplevel):
    """
    Окно для создания нового пользователя Google Workspace.
    """
    
    def __init__(self, master, service: Any, on_created: Optional[callable] = None):
        super().__init__(master)
        self.title('Создать пользователя')
        self.geometry('700x540')
        self.resizable(False, False)
        self.service = service
        self.on_created = on_created
        self.transient(master)
        if master:
            center_window(self, master)

        self._create_widgets()
        self._bind_events()

    def _create_widgets(self):
        """Создает виджеты окна"""
        # First Name
        tk.Label(self, text='First Name:', font=('Arial', 11)).grid(
            row=0, column=0, sticky='e', padx=16, pady=12)
        self.entry_first = tk.Entry(self, width=50, font=('Arial', 11))
        self.entry_first.grid(row=0, column=1, padx=8)
        self._add_validation(self.entry_first, 32)

        # Last Name
        tk.Label(self, text='Last Name:', font=('Arial', 11)).grid(
            row=1, column=0, sticky='e', padx=16, pady=8)
        self.entry_last = tk.Entry(self, width=50, font=('Arial', 11))
        self.entry_last.grid(row=1, column=1, padx=8)
        self._add_validation(self.entry_last, 32)

        # Email (автогенерация)
        tk.Label(self, text='Email (будет сгенерирован):', font=('Arial', 11)).grid(
            row=2, column=0, sticky='e', padx=16, pady=8)
        self.entry_email = tk.Entry(self, width=50, font=('Arial', 11), state='readonly')
        self.entry_email.grid(row=2, column=1, padx=8)

        # Secondary Email
        tk.Label(self, text='Secondary Email:', font=('Arial', 11)).grid(
            row=3, column=0, sticky='e', padx=16, pady=8)
        self.entry_secondary = tk.Entry(self, width=50, font=('Arial', 11))
        self.entry_secondary.grid(row=3, column=1, padx=8)
        self._add_validation(self.entry_secondary, 64)

        # Phone Number
        tk.Label(self, text='Phone Number:', font=('Arial', 11)).grid(
            row=4, column=0, sticky='e', padx=16, pady=8)
        self.entry_phone = tk.Entry(self, width=50, font=('Arial', 11))
        self.entry_phone.grid(row=4, column=1, padx=8)
        self._add_validation(self.entry_phone, 20)

        # Password
        tk.Label(self, text='Password:', font=('Arial', 11)).grid(
            row=5, column=0, sticky='e', padx=16, pady=8)
        self.entry_pass = tk.Entry(self, width=36, font=('Arial', 11), show='*')
        self.entry_pass.grid(row=5, column=1, padx=8, sticky='w')
        self._add_validation(self.entry_pass, 32)

        # Generate Password Button
        self.btn_gen_pass = tk.Button(self, text='Сгенерировать', 
                                     command=self.generate_password, 
                                     font=('Arial', 9), width=14)
        self.btn_gen_pass.grid(row=5, column=1, padx=8, sticky='e')

        # Create Button
        self.btn_create = tk.Button(self, text='Создать', command=self.create_user, 
                                   font=('Arial', 11, 'bold'), width=18)
        self.btn_create.grid(row=6, column=0, columnspan=2, pady=18)

        # Result Text Area
        self.txt_result = scrolledtext.ScrolledText(self, width=80, height=5, 
                                                   wrap=tk.WORD, font=('Arial', 10))
        self.txt_result.grid(row=7, column=0, columnspan=2, padx=16, pady=7)
        self.txt_result.config(state=tk.DISABLED)

        # Close Button
        self.btn_close = tk.Button(self, text='Закрыть', command=self.destroy, 
                                  font=('Arial', 10), width=18)
        self.btn_close.grid(row=8, column=0, columnspan=2, pady=(2, 12))

    def _add_validation(self, entry: tk.Entry, maxlen: int):
        """Добавляет валидацию длины для поля ввода"""
        vcmd = self.register(lambda P: len(P) <= maxlen)
        entry.config(validate="key", validatecommand=(vcmd, '%P'))

    def _bind_events(self):
        """Привязывает события"""
        self.entry_first.bind('<KeyRelease>', self.update_email)
        self.entry_last.bind('<KeyRelease>', self.update_email)

    def update_email(self, event=None):
        """Автоматически формирует email по шаблону имя.фамилия@sputnik8.com"""
        first = self.entry_first.get().strip().lower().replace(' ', '')
        last = self.entry_last.get().strip().lower().replace(' ', '')
        
        if first and last:
            email = f"{first}.{last}@sputnik8.com"
        else:
            email = ""
        
        self.entry_email.config(state='normal')
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, email)
        self.entry_email.config(state='readonly')

    def generate_password(self):
        """Генерирует безопасный пароль длиной 8 символов"""
        length = 8
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.SystemRandom().choice(chars) for _ in range(length))
        
        self.entry_pass.delete(0, tk.END)
        self.entry_pass.insert(0, password)

    def create_user(self):
        """Создание пользователя через Google Directory API"""
        # Получаем данные из полей
        first_name = self.entry_first.get().strip()
        last_name = self.entry_last.get().strip()
        email = self.entry_email.get().strip()
        secondary_email = self.entry_secondary.get().strip()
        phone = self.entry_phone.get().strip()
        password = self.entry_pass.get().strip()
        
        # Проверка на пробелы в начале или конце
        for field, value in [
            ('First Name', first_name), 
            ('Last Name', last_name), 
            ('Email', email),
            ('Secondary Email', secondary_email),
            ('Phone Number', phone), 
            ('Password', password)
        ]:
            if value != value.strip():
                messagebox.showwarning('Warning', 
                    f"{field} should not start or end with a space!")
                return
        
        # Проверяем обязательные поля
        if not all([first_name, last_name, email, password]):
            messagebox.showwarning('Warning', 
                'Заполните обязательные поля (First Name, Last Name, Email, Password)!')
            return
        
        # Создаем пользователя
        result = create_user(
            self.service, email, first_name, last_name, password,
            secondary_email=secondary_email, phone=phone
        )
        
        # Отображаем результат
        self.txt_result.config(state=tk.NORMAL)
        self.txt_result.delete(1.0, tk.END)
        self.txt_result.insert(tk.END, result)
        self.txt_result.config(state=tk.DISABLED)
        
        # Вызываем callback если успешно
        if self.on_created and "создан" in result:
            self.on_created()


class EditUserWindow(tk.Toplevel):
    """Окно для выбора, редактирования и удаления пользователя Google Workspace"""
    
    def __init__(self, master, service: Any):
        super().__init__(master)
        self.title('Изменить данные пользователя')
        self.geometry('800x450')
        self.resizable(False, False)
        self.service = service
        self.configure(bg='SystemButtonFace')
        self.transient(master)
        if master:
            center_window(self, master)

        self._load_users()
        self._create_widgets()

    def _load_users(self):
        """Загружает список пользователей"""
        users = get_user_list(self.service)
        self.user_map = {
            f"{u['primaryEmail']} ({u['name']['fullName']})": u 
            for u in users
        }

    def _create_widgets(self):
        """Создает виджеты окна"""
        # Левая панель - список пользователей
        left_frame = tk.Frame(self, bg='SystemButtonFace')
        left_frame.pack(side='left', fill='y', padx=(20, 10), pady=20)
        
        tk.Label(left_frame, text='Сотрудники:', bg='SystemButtonFace', 
                font=('Arial', 10, 'bold')).pack(anchor='w')
        
        self.user_listbox = tk.Listbox(left_frame, width=38, height=18, font=('Arial', 10))
        self.user_listbox.pack(side='left', fill='y')
        
        user_scroll = tk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.user_listbox.yview)
        user_scroll.pack(side='left', fill='y')
        self.user_listbox.config(yscrollcommand=user_scroll.set)
        
        # Заполняем список пользователей
        for label in self.user_map:
            self.user_listbox.insert(tk.END, label)
        
        self.user_listbox.bind('<<ListboxSelect>>', self.on_user_select)

        # Правая панель - форма редактирования
        self._create_edit_form()

    def _create_edit_form(self):
        """Создает форму редактирования"""
        right_frame = tk.Frame(self, bg='SystemButtonFace')
        right_frame.pack(side='left', fill='both', expand=True, padx=10, pady=20)

        # Email (только для чтения)
        tk.Label(right_frame, text='Email:', bg='SystemButtonFace', 
                font=('Arial', 10)).grid(row=0, column=0, sticky='e', pady=4)
        self.entry_email = tk.Entry(right_frame, width=35, font=('Arial', 10), state='readonly')
        self.entry_email.grid(row=0, column=1, pady=4)

        # Новое имя
        tk.Label(right_frame, text='Новое имя:', bg='SystemButtonFace', 
                font=('Arial', 10)).grid(row=1, column=0, sticky='e', pady=4)
        self.entry_first = tk.Entry(right_frame, width=35, font=('Arial', 10))
        self.entry_first.grid(row=1, column=1, pady=4)

        # Новая фамилия
        tk.Label(right_frame, text='Новая фамилия:', bg='SystemButtonFace', 
                font=('Arial', 10)).grid(row=2, column=0, sticky='e', pady=4)
        self.entry_last = tk.Entry(right_frame, width=35, font=('Arial', 10))
        self.entry_last.grid(row=2, column=1, pady=4)

        # Новый пароль
        tk.Label(right_frame, text='Новый пароль (опционально):', bg='SystemButtonFace', 
                font=('Arial', 10)).grid(row=3, column=0, sticky='e', pady=4)
        self.entry_pass = tk.Entry(right_frame, width=35, font=('Arial', 10), show='*')
        self.entry_pass.grid(row=3, column=1, pady=4)

        # Кнопки
        self.btn_update = tk.Button(right_frame, text='Сохранить изменения', 
                                   command=self.update_user, font=('Arial', 10, 'bold'), width=20)
        self.btn_update.grid(row=4, column=0, columnspan=2, pady=12)

        self.btn_delete = tk.Button(right_frame, text='Удалить пользователя', 
                                   command=self.delete_user, font=('Arial', 10, 'bold'), width=20)
        self.btn_delete.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        # Область результата
        self.txt_result = scrolledtext.ScrolledText(right_frame, width=45, height=3, 
                                                   wrap=tk.WORD, font=('Arial', 9))
        self.txt_result.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        self.txt_result.config(state=tk.DISABLED)

        # Кнопка закрытия
        self.btn_close = tk.Button(right_frame, text='Закрыть', command=self.destroy, 
                                  font=('Arial', 10, 'bold'), width=20)
        self.btn_close.grid(row=7, column=0, columnspan=2, pady=(2, 10))

    def on_user_select(self, event):
        """Обработка выбора пользователя"""
        selection = self.user_listbox.curselection()
        if not selection:
            return
        
        label = self.user_listbox.get(selection[0])
        user = self.user_map[label]
        
        # Заполняем поля данными пользователя
        self.entry_email.config(state='normal')
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, user['primaryEmail'])
        self.entry_email.config(state='readonly')
        
        self.entry_first.delete(0, tk.END)
        self.entry_first.insert(0, user['name'].get('givenName', ''))
        
        self.entry_last.delete(0, tk.END)
        self.entry_last.insert(0, user['name'].get('familyName', ''))
        
        self.entry_pass.delete(0, tk.END)
        
        # Очищаем результат
        self.txt_result.config(state=tk.NORMAL)
        self.txt_result.delete(1.0, tk.END)
        self.txt_result.config(state=tk.DISABLED)

    def update_user(self):
        """Обновление данных пользователя"""
        email = self.entry_email.get().strip()
        first = self.entry_first.get().strip()
        last = self.entry_last.get().strip()
        password = self.entry_pass.get().strip()
        
        # Формируем поля для обновления
        fields = {}
        if first or last:
            fields['name'] = {}
            if first:
                fields['name']['givenName'] = first
            if last:
                fields['name']['familyName'] = last
        if password:
            fields['password'] = password
        
        # Проверяем, что есть что обновлять
        if not email or not fields:
            self._show_result('Укажите email и хотя бы одно новое значение!')
            return
        
        # Обновляем пользователя
        result = update_user(self.service, email, fields)
        self._show_result(result)

    def delete_user(self):
        """Удаление пользователя"""
        email = self.entry_email.get().strip()
        if not email:
            messagebox.showwarning('Внимание', 'Выберите пользователя для удаления.')
            return
        
        # Подтверждение удаления
        confirm = messagebox.askyesno('Подтвердите удаление', 
                                     f'Удалить пользователя {email}?')
        if not confirm:
            return
        
        try:
            result = delete_user(self.service, email)
            self._show_result(result)
            
            # Удаляем из списка если успешно
            if 'успешно удалён' in result:
                idx = self.user_listbox.curselection()
                if idx:
                    self.user_listbox.delete(idx[0])
                
                # Очищаем поля
                self.entry_email.config(state='normal')
                self.entry_email.delete(0, tk.END)
                self.entry_email.config(state='readonly')
                self.entry_first.delete(0, tk.END)
                self.entry_last.delete(0, tk.END)
                self.entry_pass.delete(0, tk.END)
                
        except Exception as e:
            self._show_result(f'Ошибка удаления пользователя: {e}')

    def _show_result(self, message: str):
        """Отображает результат операции"""
        self.txt_result.config(state=tk.NORMAL)
        self.txt_result.delete(1.0, tk.END)
        self.txt_result.insert(tk.END, message + '\n')
        self.txt_result.config(state=tk.DISABLED)
