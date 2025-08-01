# -*- coding: utf-8 -*-
"""
Окно для создания пользователя в "Моей Команде" (MyTeam)
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
from typing import Optional, Callable

from .ui_components import ModernColors, center_window
from .modern_styles import (
    apply_modern_window_style, CompactFrame, CompactLabel, 
    CompactEntry, CompactButton, create_title_section
)
from ..api.myteam_api import MyTeamAPI, MyTeamUser, MyTeamApiConfig, validate_myteam_user_data


class MyTeamUserWindow(tk.Toplevel):
    """
    Окно для создания нового пользователя в "Моей Команде"
    """
    
    def __init__(self, master, api_token: str = "", on_created: Optional[Callable] = None):
        super().__init__(master)
        self.title('Создать пользователя в "Моей Команде"')
        self.geometry('800x700')
        self.resizable(False, False)
        self.api_token = api_token
        self.on_created = on_created
        self.transient(master)
        
        # Применяем современный стиль
        apply_modern_window_style(self, 'dialog')
        
        if master:
            center_window(self, master)

        # Инициализируем API
        self.api_client = None
        self._init_api_client()
        
        self._create_widgets()
        self._test_api_connection()

    def _init_api_client(self):
        """Инициализация API клиента"""
        try:
            config = MyTeamApiConfig(
                base_url="https://sputnik8.ismyteam.ru",
                api_token=self.api_token,
                timeout=30
            )
            self.api_client = MyTeamAPI(config)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка инициализации API: {e}")

    def _create_widgets(self):
        """Создает виджеты окна"""
        # Заголовок
        header_frame = create_title_section(self, '👥 Создание пользователя в "Моей Команде"')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))

        # Основной контейнер с прокруткой
        main_container = CompactFrame(self, padding_type='container')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        # API статус
        self._create_api_status_section(main_container)
        
        # Форма создания пользователя
        self._create_user_form(main_container)
        
        # Кнопки управления
        self._create_control_buttons(main_container)
        
        # Область результата
        self._create_result_area(main_container)
        
        # Кнопка закрытия
        self._create_close_button(main_container)

    def _create_api_status_section(self, parent):
        """Создает секцию статуса API"""
        status_frame = CompactFrame(parent, padding_type='section')
        status_frame.pack(fill='x', pady=(0, 15))
        
        CompactLabel(status_frame, text='🔗 Статус подключения к API:', 
                    font_type='section_header').pack(anchor='w')
        
        self.status_frame = CompactFrame(status_frame, padding_type='minimal')
        self.status_frame.pack(fill='x', pady=(5, 0))
        
        self.status_label = CompactLabel(self.status_frame, text='⏳ Проверка подключения...', 
                                        font_type='info')
        self.status_label.pack(anchor='w')
        
        # Поле для API токена
        token_frame = CompactFrame(status_frame, padding_type='minimal')
        token_frame.pack(fill='x', pady=(10, 0))
        
        CompactLabel(token_frame, text='API Токен:', font_type='label').pack(anchor='w')
        self.entry_token = CompactEntry(token_frame, width_type='wide_entry')
        self.entry_token.pack(fill='x', pady=(2, 0))
        
        if self.api_token:
            self.entry_token.insert(0, self.api_token)
        else:
            self.entry_token.insert(0, "Введите API токен для доступа к \"Моей Команде\"")
            self.entry_token.bind('<FocusIn>', self._clear_token_placeholder)
        
        # Кнопка тестирования
        CompactButton(token_frame, text='🔄 Проверить подключение', 
                     command=self._test_api_connection, style='secondary',
                     width_type='button_width').pack(pady=(5, 0), anchor='w')

    def _create_user_form(self, parent):
        """Создает форму для ввода данных пользователя"""
        form_frame = CompactFrame(parent, padding_type='section')
        form_frame.pack(fill='x', pady=(0, 15))
        
        CompactLabel(form_frame, text='👤 Данные пользователя:', 
                    font_type='section_header').pack(anchor='w')
        
        # Основные поля
        fields_frame = CompactFrame(form_frame, padding_type='form')
        fields_frame.pack(fill='x', pady=(10, 0))
        
        # Имя
        CompactLabel(fields_frame, text='Имя *:', font_type='label').grid(
            row=0, column=0, sticky='e', padx=(0, 10), pady=5)
        self.entry_first_name = CompactEntry(fields_frame, width_type='entry_width')
        self.entry_first_name.grid(row=0, column=1, sticky='ew', pady=5)
        
        # Фамилия
        CompactLabel(fields_frame, text='Фамилия *:', font_type='label').grid(
            row=1, column=0, sticky='e', padx=(0, 10), pady=5)
        self.entry_last_name = CompactEntry(fields_frame, width_type='entry_width')
        self.entry_last_name.grid(row=1, column=1, sticky='ew', pady=5)
        
        # Email
        CompactLabel(fields_frame, text='Email *:', font_type='label').grid(
            row=2, column=0, sticky='e', padx=(0, 10), pady=5)
        self.entry_email = CompactEntry(fields_frame, width_type='entry_width')
        self.entry_email.grid(row=2, column=1, sticky='ew', pady=5)
        
        # Username (автогенерация)
        CompactLabel(fields_frame, text='Username:', font_type='label').grid(
            row=3, column=0, sticky='e', padx=(0, 10), pady=5)
        self.entry_username = CompactEntry(fields_frame, width_type='entry_width')
        self.entry_username.grid(row=3, column=1, sticky='ew', pady=5)
        
        # Телефон
        CompactLabel(fields_frame, text='Телефон:', font_type='label').grid(
            row=4, column=0, sticky='e', padx=(0, 10), pady=5)
        self.entry_phone = CompactEntry(fields_frame, width_type='entry_width')
        self.entry_phone.grid(row=4, column=1, sticky='ew', pady=5)
        
        # Отдел
        CompactLabel(fields_frame, text='Отдел:', font_type='label').grid(
            row=5, column=0, sticky='e', padx=(0, 10), pady=5)
        self.entry_department = CompactEntry(fields_frame, width_type='entry_width')
        self.entry_department.grid(row=5, column=1, sticky='ew', pady=5)
        
        # Должность
        CompactLabel(fields_frame, text='Должность:', font_type='label').grid(
            row=6, column=0, sticky='e', padx=(0, 10), pady=5)
        self.entry_position = CompactEntry(fields_frame, width_type='entry_width')
        self.entry_position.grid(row=6, column=1, sticky='ew', pady=5)
        
        # Настройка растягивания колонок
        fields_frame.columnconfigure(1, weight=1)
        
        # Привязка событий для автогенерации username
        self.entry_email.bind('<KeyRelease>', self._update_username)
        
        # Информация об обязательных полях
        info_label = CompactLabel(form_frame, text='* - обязательные поля', 
                                 font_type='info')
        info_label.pack(anchor='w', pady=(5, 0))

    def _create_control_buttons(self, parent):
        """Создает кнопки управления"""
        buttons_frame = CompactFrame(parent, padding_type='section')
        buttons_frame.pack(fill='x', pady=(0, 15))
        
        button_container = CompactFrame(buttons_frame, padding_type='minimal')
        button_container.pack()
        
        self.btn_create = CompactButton(button_container, text='➕ Создать пользователя', 
                                       command=self._create_user, style='primary',
                                       width_type='wide_button')
        self.btn_create.pack(side='left', padx=(0, 10))
        
        CompactButton(button_container, text='🔄 Очистить форму', 
                     command=self._clear_form, style='secondary',
                     width_type='button_width').pack(side='left')

    def _create_result_area(self, parent):
        """Создает область для отображения результатов"""
        result_frame = CompactFrame(parent, padding_type='section')
        result_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        CompactLabel(result_frame, text='📋 Результат операции:', 
                    font_type='section_header').pack(anchor='w')
        
        # Текстовая область для результата
        self.txt_result = scrolledtext.ScrolledText(
            result_frame, 
            height=8, 
            wrap=tk.WORD, 
            font=('Consolas', 9),
            bg='#f8f9fa',
            fg='#495057',
            relief='flat',
            bd=1
        )
        self.txt_result.pack(fill='both', expand=True, pady=(10, 0))
        self.txt_result.config(state=tk.DISABLED)

    def _create_close_button(self, parent):
        """Создает кнопку закрытия"""
        close_frame = CompactFrame(parent, padding_type='minimal')
        close_frame.pack(fill='x', pady=(0, 10))
        
        CompactButton(close_frame, text='❌ Закрыть', command=self.destroy, 
                     style='secondary', width_type='button_width').pack()

    def _clear_token_placeholder(self, event=None):
        """Очищает placeholder в поле токена"""
        current_text = self.entry_token.get()
        if current_text.startswith("Введите API токен"):
            self.entry_token.delete(0, tk.END)

    def _update_username(self, event=None):
        """Автоматически генерирует username на основе email"""
        email = self.entry_email.get().strip()
        if email and '@' in email:
            username = email.split('@')[0]
            self.entry_username.delete(0, tk.END)
            self.entry_username.insert(0, username)

    def _test_api_connection(self):
        """Тестирует подключение к API в отдельном потоке"""
        def test_connection():
            try:
                self.status_label.config(text='⏳ Проверка подключения...', fg='#6c757d')
                self.update()
                
                # Обновляем токен из поля ввода
                token = self.entry_token.get().strip()
                if token and not token.startswith("Введите API токен"):
                    self.api_token = token
                    self._init_api_client()
                
                if not self.api_client:
                    self.status_label.config(text='❌ API клиент не инициализирован', fg='#dc3545')
                    return
                
                # Тестируем подключение
                result = self.api_client.test_connection()
                
                if result['success']:
                    accessible_endpoints = [ep for ep, data in result['endpoints'].items() 
                                          if data.get('accessible', False)]
                    auth_required = any(data.get('requires_auth', False) 
                                      for data in result['endpoints'].values())
                    
                    if accessible_endpoints:
                        status_text = f'✅ Подключение установлено ({len(accessible_endpoints)} endpoints доступны)'
                        if auth_required and not self.api_token:
                            status_text += ' - требуется API токен'
                        self.status_label.config(text=status_text, fg='#28a745')
                        self.btn_create.config(state='normal')
                    else:
                        self.status_label.config(text='⚠️ API доступен, но endpoints недоступны', fg='#ffc107')
                        self.btn_create.config(state='disabled')
                else:
                    self.status_label.config(text=f'❌ Ошибка подключения: {result.get("error", "Unknown")}', fg='#dc3545')
                    self.btn_create.config(state='disabled')
                    
            except Exception as e:
                self.status_label.config(text=f'❌ Ошибка тестирования: {str(e)}', fg='#dc3545')
                self.btn_create.config(state='disabled')
        
        # Запускаем в отдельном потоке
        threading.Thread(target=test_connection, daemon=True).start()

    def _validate_form(self) -> bool:
        """Валидация формы"""
        first_name = self.entry_first_name.get().strip()
        last_name = self.entry_last_name.get().strip()
        email = self.entry_email.get().strip()
        phone = self.entry_phone.get().strip()
        department = self.entry_department.get().strip()
        position = self.entry_position.get().strip()
        
        # Используем функцию валидации из API модуля
        validation_result = validate_myteam_user_data(
            email, first_name, last_name, phone, department, position
        )
        
        if not validation_result['valid']:
            error_message = "Ошибки валидации:\n" + "\n".join(validation_result['errors'])
            messagebox.showwarning('Ошибка валидации', error_message)
            return False
        
        return True

    def _create_user(self):
        """Создает пользователя через API"""
        if not self._validate_form():
            return
        
        if not self.api_client:
            messagebox.showerror('Ошибка', 'API клиент не инициализирован')
            return
        
        def create_user_async():
            try:
                # Отключаем кнопку на время выполнения
                self.btn_create.config(state='disabled', text='⏳ Создание...')
                self.update()
                
                # Собираем данные пользователя
                user = MyTeamUser(
                    email=self.entry_email.get().strip(),
                    first_name=self.entry_first_name.get().strip(),
                    last_name=self.entry_last_name.get().strip(),
                    username=self.entry_username.get().strip(),
                    phone=self.entry_phone.get().strip(),
                    department=self.entry_department.get().strip(),
                    position=self.entry_position.get().strip(),
                    is_active=True
                )
                
                # Создаем пользователя
                result = self.api_client.create_user(user)
                
                # Отображаем результат
                self._display_result(result)
                
                # Вызываем callback если успешно
                if result['success'] and self.on_created:
                    self.on_created()
                
            except Exception as e:
                error_result = {
                    'success': False,
                    'message': f'Непредвиденная ошибка: {str(e)}',
                    'error_code': 'unexpected_error'
                }
                self._display_result(error_result)
            
            finally:
                # Включаем кнопку обратно
                self.btn_create.config(state='normal', text='➕ Создать пользователя')
        
        # Запускаем в отдельном потоке
        threading.Thread(target=create_user_async, daemon=True).start()

    def _display_result(self, result: dict):
        """Отображает результат операции"""
        self.txt_result.config(state=tk.NORMAL)
        self.txt_result.delete(1.0, tk.END)
        
        if result['success']:
            message = f"✅ УСПЕХ\n{result['message']}\n\n"
            if 'user_data' in result and result['user_data']:
                message += "Данные созданного пользователя:\n"
                for key, value in result['user_data'].items():
                    message += f"  {key}: {value}\n"
            if 'endpoint_used' in result:
                message += f"\nИспользованный endpoint: {result['endpoint_used']}\n"
        else:
            message = f"❌ ОШИБКА\n{result['message']}\n\n"
            if 'error_code' in result:
                message += f"Код ошибки: {result['error_code']}\n"
            if 'details' in result:
                message += f"Детали: {result['details']}\n"
        
        self.txt_result.insert(tk.END, message)
        self.txt_result.config(state=tk.DISABLED)

    def _clear_form(self):
        """Очищает форму"""
        self.entry_first_name.delete(0, tk.END)
        self.entry_last_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_username.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.entry_department.delete(0, tk.END)
        self.entry_position.delete(0, tk.END)
        
        # Очищаем результат
        self.txt_result.config(state=tk.NORMAL)
        self.txt_result.delete(1.0, tk.END)
        self.txt_result.config(state=tk.DISABLED)


def open_myteam_user_window(master=None, api_token: str = "", on_created: Optional[Callable] = None):
    """
    Открывает окно создания пользователя в "Моей Команде"
    
    Args:
        master: Родительское окно
        api_token: API токен для авторизации
        on_created: Callback функция, вызываемая после успешного создания пользователя
    """
    try:
        window = MyTeamUserWindow(master, api_token, on_created)
        return window
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть окно создания пользователя: {e}")
        return None