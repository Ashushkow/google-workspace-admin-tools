# -*- coding: utf-8 -*-
"""
Окна для работы с пользователями.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import string
import random
from typing import Any, Optional

from .ui_components import ModernColors, center_window
from ..api.users_api import create_user, update_user as api_update_user, delete_user, get_user_list
from ..api.orgunits_api import (
    list_orgunits, 
    format_orgunits_for_combobox, 
    get_orgunit_path_from_display_name,
    get_user_orgunit,
    get_display_name_for_orgunit_path,
    move_user_to_orgunit
)


class CreateUserWindow(tk.Toplevel):
    """
    Окно для создания нового пользователя Google Workspace.
    """
    
    def __init__(self, master, service: Any, on_created: Optional[callable] = None):
        super().__init__(master)
        self.title('Создать пользователя')
        self.geometry('700x600')  # Увеличиваем высоту для нового поля
        self.resizable(False, False)
        self.service = service
        self.on_created = on_created
        self.transient(master)
        if master:
            center_window(self, master)

        # Загружаем список OU
        self.orgunits = []
        self.orgunit_display_names = []
        self._load_orgunits()

        self._create_widgets()
        self._bind_events()

    def _load_orgunits(self):
        """Загружает список организационных подразделений"""
        try:
            self.orgunits = list_orgunits(self.service)
            self.orgunit_display_names = format_orgunits_for_combobox(self.orgunits)
            if not self.orgunit_display_names:
                # Если не удалось загрузить OU, добавляем только корневое
                self.orgunit_display_names = ["/ (Root Organization)"]
        except Exception as e:
            print(f"Ошибка загрузки OU: {e}")
            # В случае ошибки показываем только корневое подразделение
            self.orgunit_display_names = ["/ (Root Organization)"]

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
        email_frame = tk.Frame(self)
        email_frame.grid(row=2, column=0, columnspan=2, sticky='w', padx=16, pady=8)
        
        tk.Label(email_frame, text='Email (будет сгенерирован):', font=('Arial', 11)).grid(
            row=0, column=0, sticky='e')
        self.entry_email = tk.Entry(email_frame, width=50, font=('Arial', 11), state='readonly')
        self.entry_email.grid(row=0, column=1, padx=8)
        
        # Подсказка для primary email
        tk.Label(email_frame, text='📧 Должен быть в домене @sputnik8.com', 
                 font=('Arial', 9), fg='#666666').grid(row=1, column=1, sticky='w', padx=8)

        # Secondary Email
        secondary_frame = tk.Frame(self)
        secondary_frame.grid(row=3, column=0, columnspan=2, sticky='w', padx=16, pady=8)
        
        tk.Label(secondary_frame, text='Secondary Email:', font=('Arial', 11)).grid(
            row=0, column=0, sticky='e')
        self.entry_secondary = tk.Entry(secondary_frame, width=50, font=('Arial', 11))
        self.entry_secondary.grid(row=0, column=1, padx=8)
        self._add_validation(self.entry_secondary, 64)
        
        # Подсказка для secondary email
        tk.Label(secondary_frame, text='💡 Может быть любой домен (Gmail, Yahoo и т.д.) для восстановления', 
                 font=('Arial', 9), fg='#666666').grid(row=1, column=1, sticky='w', padx=8)

        # Phone Number
        tk.Label(self, text='Phone Number:', font=('Arial', 11)).grid(
            row=6, column=0, sticky='e', padx=16, pady=8)
        self.entry_phone = tk.Entry(self, width=50, font=('Arial', 11))
        self.entry_phone.grid(row=6, column=1, padx=8)
        self._add_validation(self.entry_phone, 20)

        # Organizational Unit
        tk.Label(self, text='Подразделение (OU):', font=('Arial', 11)).grid(
            row=7, column=0, sticky='e', padx=16, pady=8)
        self.combo_orgunit = ttk.Combobox(self, width=47, font=('Arial', 11), state='readonly')
        self.combo_orgunit['values'] = self.orgunit_display_names
        if self.orgunit_display_names:
            self.combo_orgunit.current(0)  # Выбираем первый элемент (корневое OU) по умолчанию
        self.combo_orgunit.grid(row=7, column=1, padx=8, sticky='w')

        # Password
        tk.Label(self, text='Password:', font=('Arial', 11)).grid(
            row=8, column=0, sticky='e', padx=16, pady=8)
        self.entry_pass = tk.Entry(self, width=36, font=('Arial', 11), show='*')
        self.entry_pass.grid(row=8, column=1, padx=8, sticky='w')
        self._add_validation(self.entry_pass, 32)

        # Generate Password Button
        self.btn_gen_pass = tk.Button(self, text='🔑 Сгенерировать', 
                                     command=self.generate_password, 
                                     font=('Arial', 9), width=16)
        self.btn_gen_pass.grid(row=8, column=1, padx=8, sticky='e')

        # Create Button
        self.btn_create = tk.Button(self, text='➕ Создать', command=self.create_user, 
                                   font=('Arial', 11, 'bold'), width=18)
        self.btn_create.grid(row=9, column=0, columnspan=2, pady=18)

        # Result Text Area
        self.txt_result = scrolledtext.ScrolledText(self, width=80, height=5, 
                                                   wrap=tk.WORD, font=('Arial', 10))
        self.txt_result.grid(row=10, column=0, columnspan=2, padx=16, pady=8)
        self.txt_result.config(state=tk.DISABLED)

        # Close Button
        self.btn_close = tk.Button(self, text='❌ Закрыть', command=self.destroy, 
                                  font=('Arial', 10), width=18)
        self.btn_close.grid(row=11, column=0, columnspan=2, pady=(2, 12))

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
        
        # Получаем выбранное OU
        selected_ou_display = self.combo_orgunit.get()
        org_unit_path = get_orgunit_path_from_display_name(selected_ou_display, self.orgunits)
        
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
        
        # Дополнительная проверка домена primary email
        if '@' in email:
            email_domain = email.split('@')[-1].lower()
            if email_domain not in ['sputnik8.com']:
                result = messagebox.askyesno(
                    'Проверьте email домен',
                    f'Primary Email должен быть в домене @sputnik8.com\n\n'
                    f'Вы указали: {email}\n'
                    f'Домен: {email_domain}\n\n'
                    f'Возможно, вы хотели указать этот адрес как Secondary Email?\n\n'
                    f'Продолжить создание пользователя?'
                )
                if not result:
                    return
        
        # Создаем пользователя с указанием OU
        result = create_user(
            self.service, email, first_name, last_name, password,
            secondary_email=secondary_email, phone=phone, org_unit_path=org_unit_path
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
        self.geometry('800x550')  # Увеличиваем высоту для нового поля OU
        self.resizable(False, False)
        self.service = service
        self.configure(bg='SystemButtonFace')
        self.transient(master)
        if master:
            center_window(self, master)

        # Загружаем список OU
        self.orgunits = []
        self.orgunit_display_names = []
        self._load_orgunits()
        
        self._load_users()
        self._create_widgets()

    def _load_orgunits(self):
        """Загружает список организационных подразделений"""
        try:
            self.orgunits = list_orgunits(self.service)
            self.orgunit_display_names = format_orgunits_for_combobox(self.orgunits)
            if not self.orgunit_display_names:
                # Если не удалось загрузить OU, добавляем только корневое
                self.orgunit_display_names = ["🏠 Корневое подразделение"]
        except Exception as e:
            print(f"Ошибка загрузки OU: {e}")
            # В случае ошибки показываем только корневое подразделение
            self.orgunit_display_names = ["🏠 Корневое подразделение"]

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

        # Подразделение (OU)
        tk.Label(right_frame, text='Подразделение (OU):', bg='SystemButtonFace', 
                font=('Arial', 10)).grid(row=4, column=0, sticky='e', pady=4)
        self.combo_orgunit = ttk.Combobox(right_frame, width=32, font=('Arial', 10), state='readonly')
        self.combo_orgunit['values'] = self.orgunit_display_names
        if self.orgunit_display_names:
            self.combo_orgunit.current(0)  # По умолчанию выбираем первый элемент
        self.combo_orgunit.grid(row=4, column=1, pady=4)

        # Кнопки
        self.btn_update = tk.Button(right_frame, text='💾 Сохранить изменения', 
                                   command=self.update_user, font=('Arial', 10, 'bold'), width=22)
        self.btn_update.grid(row=5, column=0, columnspan=2, pady=12)

        self.btn_delete = tk.Button(right_frame, text='🗑️ Удалить пользователя', 
                                   command=self.delete_user, font=('Arial', 10, 'bold'), width=22)
        self.btn_delete.grid(row=6, column=0, columnspan=2, pady=(0, 10))

        # Область результата
        self.txt_result = scrolledtext.ScrolledText(right_frame, width=45, height=3, 
                                                   wrap=tk.WORD, font=('Arial', 9))
        self.txt_result.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        self.txt_result.config(state=tk.DISABLED)

        # Кнопка закрытия
        self.btn_close = tk.Button(right_frame, text='❌ Закрыть', command=self.destroy, 
                                  font=('Arial', 10, 'bold'), width=22)
        self.btn_close.grid(row=8, column=0, columnspan=2, pady=(2, 10))

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
        
        # Загружаем и устанавливаем текущее OU пользователя
        try:
            user_ou_path = get_user_orgunit(self.service, user['primaryEmail'])
            user_ou_display = get_display_name_for_orgunit_path(user_ou_path, self.orgunits)
            
            # Находим индекс в списке отображаемых названий
            try:
                ou_index = self.orgunit_display_names.index(user_ou_display)
                self.combo_orgunit.current(ou_index)
            except ValueError:
                # Если OU не найдено в списке, устанавливаем корневое
                self.combo_orgunit.current(0)
        except Exception as e:
            print(f"Ошибка загрузки OU пользователя: {e}")
            # В случае ошибки устанавливаем корневое OU
            self.combo_orgunit.current(0)
        
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
        
        # Получаем выбранное OU
        selected_ou_display = self.combo_orgunit.get()
        new_org_unit_path = get_orgunit_path_from_display_name(selected_ou_display, self.orgunits)
        
        # Получаем текущее OU пользователя для сравнения
        current_org_unit_path = get_user_orgunit(self.service, email)
        
        # Формируем поля для обновления (исключаем OU)
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
        if not email and not fields and new_org_unit_path == current_org_unit_path:
            self._show_result('Укажите email и хотя бы одно новое значение!')
            return
        
        result_messages = []
        
        # Обновляем основные данные пользователя (если есть изменения)
        if fields:
            result = api_update_user(self.service, email, fields)
            result_messages.append(result)
        
        # Перемещаем пользователя в другое OU (если нужно)
        if new_org_unit_path != current_org_unit_path:
            ou_result = move_user_to_orgunit(self.service, email, new_org_unit_path)
            if ou_result['success']:
                ou_display = get_display_name_for_orgunit_path(new_org_unit_path, self.orgunits)
                result_messages.append(f"📁 Пользователь перемещен в: {ou_display}")
            else:
                result_messages.append(f"❌ Ошибка перемещения: {ou_result['message']}")
        
        # Объединяем все результаты
        final_result = "\n".join(result_messages) if result_messages else "Нет изменений для применения"
        self._show_result(final_result)

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
