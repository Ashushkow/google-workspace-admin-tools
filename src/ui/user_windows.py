# -*- coding: utf-8 -*-
"""
Окна для работы с пользователями.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import string
import random
from typing import Any, Optional

from .ui_components import ModernColors, ModernButton, center_window
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
        self.title('Создание пользователя')
        self.geometry('800x800')  # Увеличиваем размер окна для лучшей видимости
        self.resizable(True, True)  # Делаем окно масштабируемым
        self.service = service
        self.on_created = on_created
        self.transient(master)
        if master:
            center_window(self, master)
        
        # Применяем современные стили
        self.configure(bg=ModernColors.BACKGROUND)
        
        # Устанавливаем минимальный размер окна
        self.minsize(700, 600)

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
        # Создаем основной контейнер с современным стилем
        main_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок окна
        title_frame = tk.Frame(main_frame, bg=ModernColors.PRIMARY, height=50)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text='🆕 Создание нового пользователя',
            font=('Segoe UI', 14, 'bold'),
            fg='white',
            bg=ModernColors.PRIMARY
        )
        title_label.pack(expand=True)
        
        # Контейнер для формы
        form_frame = tk.Frame(main_frame, bg=ModernColors.SURFACE, relief='solid', bd=1)
        form_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Внутренний контейнер формы с отступами
        inner_frame = tk.Frame(form_frame, bg=ModernColors.SURFACE)
        inner_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Настраиваем grid для масштабирования
        inner_frame.columnconfigure(1, weight=1)  # Поля ввода будут растягиваться

        # First Name
        self._create_field_with_label(inner_frame, 'First Name:', 0)
        self.entry_first = self._create_modern_entry(inner_frame, 0, 50)
        self._add_validation(self.entry_first, 32)

        # Last Name
        self._create_field_with_label(inner_frame, 'Last Name:', 1)
        self.entry_last = self._create_modern_entry(inner_frame, 1, 50)
        self._add_validation(self.entry_last, 32)

        # Email (автогенерация)
        email_frame = tk.Frame(inner_frame, bg=ModernColors.SURFACE)
        email_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(12, 8))
        email_frame.columnconfigure(1, weight=1)
        
        tk.Label(email_frame, text='Email (будет сгенерирован):', 
                font=('Segoe UI', 10, 'bold'), fg=ModernColors.TEXT_PRIMARY, 
                bg=ModernColors.SURFACE).grid(row=0, column=0, sticky='w')
        
        self.entry_email = tk.Entry(email_frame, font=('Segoe UI', 10), 
                                   state='readonly', bg=ModernColors.BACKGROUND,
                                   relief='solid', bd=1)
        self.entry_email.grid(row=0, column=1, sticky='ew', padx=(10, 0))
        
        # Подсказка для primary email
        tk.Label(email_frame, text='📧 Рабочая почта сотрудника в домене @sputnik8.com', 
                 font=('Segoe UI', 9), fg=ModernColors.TEXT_SECONDARY,
                 bg=ModernColors.SURFACE).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(2, 0))

        # Secondary Email
        secondary_frame = tk.Frame(inner_frame, bg=ModernColors.SURFACE)
        secondary_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(12, 8))
        secondary_frame.columnconfigure(1, weight=1)
        
        tk.Label(secondary_frame, text='Secondary Email:', 
                font=('Segoe UI', 10, 'bold'), fg=ModernColors.TEXT_PRIMARY,
                bg=ModernColors.SURFACE).grid(row=0, column=0, sticky='w')
        
        self.entry_secondary = self._create_modern_entry_in_frame(secondary_frame, 0, 1, 50)
        self._add_validation(self.entry_secondary, 64)
        
        # Подсказка для secondary email
        tk.Label(secondary_frame, text='💡 Может быть любой домен (Gmail, Yahoo и т.д.) для восстановления', 
                 font=('Segoe UI', 9), fg=ModernColors.TEXT_SECONDARY,
                 bg=ModernColors.SURFACE).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(2, 0))

        # Phone Number
        self._create_field_with_label(inner_frame, 'Phone Number:', 6)
        self.entry_phone = self._create_modern_entry(inner_frame, 6, 50)
        self._add_validation(self.entry_phone, 20)

        # Organizational Unit
        self._create_field_with_label(inner_frame, 'Подразделение (OU):', 7)
        self.combo_orgunit = ttk.Combobox(inner_frame, font=('Segoe UI', 10), state='readonly')
        self.combo_orgunit['values'] = self.orgunit_display_names
        if self.orgunit_display_names:
            self.combo_orgunit.current(0)  # Выбираем первый элемент (корневое OU) по умолчанию
        self.combo_orgunit.grid(row=7, column=1, sticky='ew', padx=(10, 0), pady=(8, 8))

        # Password с кнопкой генерации в одной строке
        password_frame = tk.Frame(inner_frame, bg=ModernColors.SURFACE)
        password_frame.grid(row=8, column=0, columnspan=2, sticky='ew', pady=(12, 8))
        password_frame.columnconfigure(1, weight=1)
        
        tk.Label(password_frame, text='Password:', 
                font=('Segoe UI', 10, 'bold'), fg=ModernColors.TEXT_PRIMARY,
                bg=ModernColors.SURFACE).grid(row=0, column=0, sticky='w')
        
        self.entry_pass = tk.Entry(password_frame, font=('Segoe UI', 10), show='*',
                                  relief='solid', bd=1, bg='white')
        self.entry_pass.grid(row=0, column=1, sticky='ew', padx=(10, 10))
        self._add_validation(self.entry_pass, 32)
        # Добавляем контекстное меню для копирования/вставки
        self._add_context_menu(self.entry_pass)

        # Generate Password Button
        self.btn_gen_pass = ModernButton(password_frame, text='🔑 Сгенерировать', 
                                        command=self.generate_password, 
                                        style='secondary',
                                        font=('Segoe UI', 9))
        self.btn_gen_pass.grid(row=0, column=2, padx=(0, 0))

        # Кнопки действий
        button_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        button_frame.pack(fill='x', pady=(10, 0))

        # Create Button
        self.btn_create = ModernButton(button_frame, text='➕ Создать пользователя', 
                                      command=self.create_user, 
                                      style='primary',
                                      font=('Segoe UI', 11, 'bold'))
        self.btn_create.pack(side='left', padx=(0, 10))

        # Close Button
        self.btn_close = ModernButton(button_frame, text='❌ Закрыть', 
                                     command=self.destroy, 
                                     style='secondary',
                                     font=('Segoe UI', 10))
        self.btn_close.pack(side='right')

        # Result Text Area
        result_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        result_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        tk.Label(result_frame, text='Результат операции:', 
                font=('Segoe UI', 10, 'bold'), fg=ModernColors.TEXT_PRIMARY,
                bg=ModernColors.BACKGROUND).pack(anchor='w')
        
        self.txt_result = scrolledtext.ScrolledText(result_frame, height=6, 
                                                   wrap=tk.WORD, font=('Segoe UI', 10),
                                                   bg='white', relief='solid', bd=1)
        self.txt_result.pack(fill='both', expand=True, pady=(5, 0))
        self.txt_result.config(state=tk.DISABLED)
        
        # Добавляем контекстное меню для области результата
        self._add_result_context_menu(self.txt_result)

    def _create_field_with_label(self, parent, text, row):
        """Создает стандартную метку для поля"""
        label = tk.Label(parent, text=text, font=('Segoe UI', 10, 'bold'), 
                        fg=ModernColors.TEXT_PRIMARY, bg=ModernColors.SURFACE)
        label.grid(row=row, column=0, sticky='w', pady=(8, 8))
        return label

    def _create_modern_entry(self, parent, row, width):
        """Создает современное поле ввода с поддержкой копирования/вставки"""
        entry = tk.Entry(parent, font=('Segoe UI', 10), 
                        relief='solid', bd=1, bg='white')
        entry.grid(row=row, column=1, sticky='ew', padx=(10, 0), pady=(8, 8))
        # Добавляем контекстное меню для копирования/вставки
        self._add_context_menu(entry)
        return entry

    def _create_modern_entry_in_frame(self, parent, row, column, width):
        """Создает современное поле ввода в указанном фрейме"""
        entry = tk.Entry(parent, font=('Segoe UI', 10), 
                        relief='solid', bd=1, bg='white')
        entry.grid(row=row, column=column, sticky='ew', padx=(10, 0))
        # Добавляем контекстное меню для копирования/вставки
        self._add_context_menu(entry)
        return entry

    def _add_context_menu(self, entry):
        """Добавляет контекстное меню с операциями копирования/вставки"""
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

        def copy_text():
            try:
                entry.clipboard_clear()
                entry.clipboard_append(entry.selection_get())
            except tk.TclError:
                # Нет выделенного текста
                pass

        def paste_text():
            try:
                clipboard_text = entry.clipboard_get()
                # Вставляем в позицию курсора
                cursor_pos = entry.index(tk.INSERT)
                entry.insert(cursor_pos, clipboard_text)
            except tk.TclError:
                # Буфер обмена пуст
                pass

        def cut_text():
            try:
                entry.clipboard_clear()
                entry.clipboard_append(entry.selection_get())
                entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                # Нет выделенного текста
                pass

        def select_all():
            entry.select_range(0, tk.END)

        context_menu = tk.Menu(entry, tearoff=0)
        context_menu.add_command(label="Копировать", command=copy_text)
        context_menu.add_command(label="Вставить", command=paste_text)
        context_menu.add_command(label="Вырезать", command=cut_text)
        context_menu.add_separator()
        context_menu.add_command(label="Выделить всё", command=select_all)

        entry.bind("<Button-3>", show_context_menu)  # Правая кнопка мыши

    def _add_result_context_menu(self, text_widget):
        """Добавляет контекстное меню для области результата с операциями копирования"""
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

        def copy_selection():
            """Копирует выделенный текст из области результата"""
            try:
                # Временно включаем виджет для копирования
                current_state = text_widget.cget('state')
                text_widget.config(state='normal')
                
                selected_text = text_widget.selection_get()
                if selected_text:
                    text_widget.clipboard_clear()
                    text_widget.clipboard_append(selected_text)
                
                # Восстанавливаем состояние
                text_widget.config(state=current_state)
            except tk.TclError:
                # Нет выделенного текста
                pass

        def copy_all():
            """Копирует весь текст из области результата"""
            try:
                current_state = text_widget.cget('state')
                text_widget.config(state='normal')
                
                all_text = text_widget.get('1.0', tk.END).strip()
                if all_text:
                    text_widget.clipboard_clear()
                    text_widget.clipboard_append(all_text)
                
                text_widget.config(state=current_state)
            except tk.TclError:
                pass

        def select_all():
            """Выделяет весь текст в области результата"""
            try:
                current_state = text_widget.cget('state')
                text_widget.config(state='normal')
                
                text_widget.tag_add('sel', '1.0', tk.END)
                
                text_widget.config(state=current_state)
            except tk.TclError:
                pass

        context_menu = tk.Menu(text_widget, tearoff=0)
        context_menu.add_command(label="📋 Копировать выделенное", command=copy_selection)
        context_menu.add_command(label="📄 Копировать всё", command=copy_all)
        context_menu.add_separator()
        context_menu.add_command(label="🔍 Выделить всё", command=select_all)

        text_widget.bind("<Button-3>", show_context_menu)  # Правая кнопка мыши
        
        # Добавляем горячие клавиши для области результата
        text_widget.bind('<Control-c>', lambda e: copy_selection())
        text_widget.bind('<Control-a>', lambda e: select_all())

    def _add_validation(self, entry: tk.Entry, maxlen: int):
        """Добавляет валидацию длины для поля ввода"""
        vcmd = self.register(lambda P: len(P) <= maxlen)
        entry.config(validate="key", validatecommand=(vcmd, '%P'))

    def _bind_events(self):
        """Привязывает события"""
        self.entry_first.bind('<KeyRelease>', self.update_email)
        self.entry_last.bind('<KeyRelease>', self.update_email)
        
        # Добавляем горячие клавиши для копирования/вставки ко всем полям
        self._bind_hotkeys(self.entry_first)
        self._bind_hotkeys(self.entry_last)
        self._bind_hotkeys(self.entry_secondary)
        self._bind_hotkeys(self.entry_phone)
        self._bind_hotkeys(self.entry_pass)

    def _bind_hotkeys(self, entry):
        """Добавляет стандартные горячие клавиши для копирования/вставки"""
        entry.bind('<Control-c>', lambda e: self._copy_selection(entry))
        entry.bind('<Control-v>', lambda e: self._paste_clipboard(entry))
        entry.bind('<Control-x>', lambda e: self._cut_selection(entry))
        entry.bind('<Control-a>', lambda e: self._select_all(entry))

    def _copy_selection(self, entry):
        """Копирует выделенный текст"""
        try:
            entry.clipboard_clear()
            entry.clipboard_append(entry.selection_get())
        except tk.TclError:
            pass

    def _paste_clipboard(self, entry):
        """Вставляет текст из буфера обмена"""
        try:
            clipboard_text = entry.clipboard_get()
            cursor_pos = entry.index(tk.INSERT)
            entry.insert(cursor_pos, clipboard_text)
        except tk.TclError:
            pass

    def _cut_selection(self, entry):
        """Вырезает выделенный текст"""
        try:
            entry.clipboard_clear()
            entry.clipboard_append(entry.selection_get())
            entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    def _select_all(self, entry):
        """Выделяет весь текст в поле"""
        entry.select_range(0, tk.END)
        return 'break'  # Предотвращаем дальнейшую обработку события

    def update_email(self, event=None):
        """Автоматически формирует email по шаблону имя.фамилия@sputnik8.com"""
        first = self.entry_first.get().strip().lower().replace(' ', '')
        last = self.entry_last.get().strip().lower().replace(' ', '')
        
        if first and last:
            # Жестко задаем рабочий домен sputnik8.com для сотрудников
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
    
    def __init__(self, master, service: Any, on_updated: Optional[callable] = None):
        super().__init__(master)
        self.title('Изменить данные пользователя')
        self.geometry('800x550')  # Увеличиваем высоту для нового поля OU
        self.resizable(False, False)
        self.service = service
        self.on_updated = on_updated
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
        
        # Вызываем callback если есть изменения
        if self.on_updated and result_messages:
            self.on_updated()

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
                
                # Вызываем callback при успешном удалении
                if self.on_updated:
                    self.on_updated()
                
        except Exception as e:
            self._show_result(f'Ошибка удаления пользователя: {e}')

    def _show_result(self, message: str):
        """Отображает результат операции"""
        self.txt_result.config(state=tk.NORMAL)
        self.txt_result.delete(1.0, tk.END)
        self.txt_result.insert(tk.END, message + '\n')
        self.txt_result.config(state=tk.DISABLED)
