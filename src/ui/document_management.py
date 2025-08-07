#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Окно для управления доступом к Google документам.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
from typing import Optional, List

from .ui_components import ModernColors, ModernButton, center_window
from ..services.document_service import DocumentAccessRequest


logger = logging.getLogger(__name__)


class DocumentManagementWindow:
    """Окно для управления документами"""
    
    def __init__(self, parent, document_service, document_url: str = None):
        self.parent = parent
        self.document_service = document_service
        self.current_document_url = document_url or "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2"
        self.current_doc_info = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("📄 Управление доступом к документам")
        self.window.geometry("700x550")  # Увеличили высоту с 500 до 550
        self.window.configure(bg=ModernColors.BACKGROUND)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(True, True)  # Делаем окно изменяемым по размеру
        
        # Центрируем окно
        center_window(self.window, parent)
        
        self._create_widgets()
        self._setup_context_menu()
        self._setup_url_context_menu()  # Контекстное меню для URL
        self._setup_email_context_menu()  # Контекстное меню для Email
        
        # Автоматически загружаем информацию о документе по умолчанию
        if self.current_document_url:
            self.window.after(100, self._initialize_default_document)
    
    def _get_role_mapping(self):
        """Возвращает маппинг между понятными названиями ролей и API значениями"""
        return {
            "Viewer": "reader",
            "Commenter": "commenter", 
            "Editor": "writer"
        }
    
    def _get_reverse_role_mapping(self):
        """Возвращает обратный маппинг от API значений к понятным названиям"""
        return {
            "reader": "Viewer",
            "commenter": "Commenter",
            "writer": "Editor",
            "owner": "Owner"
        }
    
    def _convert_role_to_api(self, display_role):
        """Конвертирует понятное название роли в API значение"""
        mapping = self._get_role_mapping()
        return mapping.get(display_role, display_role.lower())
    
    def _convert_role_from_api(self, api_role):
        """Конвертирует API значение роли в понятное название"""
        mapping = self._get_reverse_role_mapping()
        return mapping.get(api_role, api_role.capitalize())
    
    def _on_document_selected(self, event):
        """Обработчик выбора документа из списка"""
        selected_doc = self.doc_combo_var.get()
        if selected_doc in self.predefined_docs:
            url = self.predefined_docs[selected_doc]
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
    
    def _select_predefined_document(self):
        """Выбор предустановленного документа и автоматическая загрузка"""
        selected_doc = self.doc_combo_var.get()
        if not selected_doc:
            messagebox.showwarning("Предупреждение", "Выберите документ из списка")
            return
        
        if selected_doc in self.predefined_docs:
            url = self.predefined_docs[selected_doc]
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
            self.current_document_url = url
            
            # Автоматически загружаем информацию о документе
            self._load_document_info()
            
            logger.info(f"Выбран предустановленный документ: {selected_doc}")
    
    def _get_document_type_emoji(self, url):
        """Возвращает эмодзи в зависимости от типа документа"""
        if "/document/" in url:
            return "📄"
        elif "/spreadsheets/" in url:
            return "📊" 
        elif "/presentation/" in url:
            return "📋"
        else:
            return "📎"
    
    def _initialize_default_document(self):
        """Инициализация документа по умолчанию"""
        # Проверяем, есть ли URL по умолчанию среди предустановленных
        for doc_name, doc_url in self.predefined_docs.items():
            if doc_url == self.current_document_url:
                self.doc_combo_var.set(doc_name)
                break
        
        # Загружаем информацию о документе
        self._load_document_info()
    
    def _create_widgets(self):
        """Создание виджетов интерфейса"""
        # Основной контейнер с прокруткой
        main_frame = tk.Frame(self.window, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)  # Уменьшили отступы
        
        # Заголовок
        title_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        title_frame.pack(fill='x', pady=(0, 10))  # Уменьшили отступ
        
        title_label = tk.Label(
            title_frame,
            text="📄 Управление доступом к Google документам",
            font=('Segoe UI', 12, 'bold'),  # Уменьшили размер шрифта
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        title_label.pack()
        
        # Рамка для выбора документа
        doc_select_frame = tk.LabelFrame(
            self.window,
            text="Выбор документа",
            font=('Segoe UI', 9, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            padx=6,
            pady=4
        )
        doc_select_frame.pack(fill='x', padx=10, pady=6)
        
        # Предустановленные документы
        self.predefined_docs = {
            "📄 Документ Google Docs": "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2",
            "📊 Таблица Google Sheets": "https://docs.google.com/spreadsheets/d/1ErK5XLx7QEUJv22XC-UBQGyig3Otfm-xR1A1-hm8eDA/edit#gid=1326342300", 
            "📋 Презентация Google Slides": "https://docs.google.com/presentation/d/1ia0PmtgJBaY3Q97gaA1TNyJFJF7vgXhsGh1iF1WOQ_E/edit#slide=id.g2dca74c59e7_0_0"
        }
        
        # Выпадающий список документов
        doc_combo_frame = tk.Frame(doc_select_frame, bg=ModernColors.BACKGROUND)
        doc_combo_frame.pack(fill='x', pady=(0, 8))
        
        tk.Label(
            doc_combo_frame,
            text="Быстрый выбор:",
            font=('Segoe UI', 9),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left', padx=(0, 8))
        
        self.doc_combo_var = tk.StringVar()
        self.doc_combo = ttk.Combobox(
            doc_combo_frame,
            textvariable=self.doc_combo_var,
            values=list(self.predefined_docs.keys()),
            state="readonly",
            width=35
        )
        self.doc_combo.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self.doc_combo.bind('<<ComboboxSelected>>', self._on_document_selected)
        
        # Кнопка "Выбрать"
        ModernButton(
            doc_combo_frame,
            text="Выбрать",
            command=self._select_predefined_document,
            button_type="primary"
        ).pack(side='right')
        
        # Поле для ввода собственного URL
        url_input_frame = tk.Frame(doc_select_frame, bg=ModernColors.BACKGROUND)
        url_input_frame.pack(fill='x')
        
        tk.Label(
            url_input_frame,
            text="Или введите URL:",
            font=('Segoe UI', 9),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 4))
        
        url_entry_frame = tk.Frame(url_input_frame, bg=ModernColors.BACKGROUND)
        url_entry_frame.pack(fill='x')
        
        self.url_entry = tk.Entry(
            url_entry_frame,
            font=('Segoe UI', 10),
            bg='white',
            fg=ModernColors.TEXT_PRIMARY,
            relief='solid',
            bd=1
        )
        self.url_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.url_entry.insert(0, self.current_document_url)
        
        # Привязываем горячие клавиши для URL поля
        self.url_entry.bind('<Control-c>', lambda e: self._copy_url())
        self.url_entry.bind('<Control-v>', lambda e: self._paste_url())
        self.url_entry.bind('<Control-x>', lambda e: self._cut_url())
        self.url_entry.bind('<Control-a>', lambda e: self._select_all_url())
        
        # Добавляем контекстное меню для поля URL
        self._setup_url_context_menu()
        
        ModernButton(
            url_entry_frame,
            text="Загрузить",
            command=self._load_document_info,
            button_type="primary"
        ).pack(side='right')
        
        # Информация о документе
        self.doc_info_frame = tk.LabelFrame(
            self.window,
            text="Информация о документе",
            font=('Segoe UI', 9, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            padx=6,    # Уменьшили отступы
            pady=4     # Уменьшили отступы
        )
        self.doc_info_frame.pack(fill='x', padx=10, pady=6)  # Уменьшили отступы
        
        self.doc_info_label = tk.Label(
            self.doc_info_frame,
            text="Выберите документ для просмотра информации",
            font=('Segoe UI', 9),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_SECONDARY,
            justify='left'
        )
        self.doc_info_label.pack(anchor='w')
        
        # Управление доступом
        access_frame = tk.LabelFrame(
            self.window,
            text="Управление доступом",
            font=('Segoe UI', 9, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            padx=6,    # Уменьшили отступы
            pady=4     # Уменьшили отступы
        )
        access_frame.pack(fill='x', padx=10, pady=6)  # Уменьшили отступы
        
        # Добавление доступа
        add_access_frame = tk.Frame(access_frame, bg=ModernColors.BACKGROUND)
        add_access_frame.pack(fill='x', pady=(0, 6))  # Уменьшили отступ
        
        tk.Label(
            add_access_frame,
            text="Email:",
            font=('Segoe UI', 9),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left')
        
        self.email_entry = tk.Entry(
            add_access_frame,
            font=('Segoe UI', 9),
            bg='white',
            fg=ModernColors.TEXT_PRIMARY,
            relief='solid',
            bd=1,
            width=28
        )
        self.email_entry.pack(side='left', padx=(8, 8))
        
        # Привязываем горячие клавиши для Email поля
        self.email_entry.bind('<Control-c>', lambda e: self._copy_email())
        self.email_entry.bind('<Control-v>', lambda e: self._paste_email())
        self.email_entry.bind('<Control-x>', lambda e: self._cut_email())
        self.email_entry.bind('<Control-a>', lambda e: self._select_all_email())
        
        tk.Label(
            add_access_frame,
            text="Роль:",
            font=('Segoe UI', 9),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left')
        
        self.role_var = tk.StringVar(value="Viewer")
        role_combo = ttk.Combobox(
            add_access_frame,
            textvariable=self.role_var,
            values=["Viewer", "Commenter", "Editor"],
            state="readonly",
            width=12
        )
        role_combo.pack(side='left', padx=(8, 8))
        
        ModernButton(
            add_access_frame,
            text="Добавить доступ",
            command=self._add_access,
            button_type="success"
        ).pack(side='left', padx=(8, 0))
        
        # Уведомления
        notify_frame = tk.Frame(access_frame, bg=ModernColors.BACKGROUND)
        notify_frame.pack(fill='x', pady=(8, 0))
        
        self.notify_var = tk.BooleanVar(value=True)
        notify_check = tk.Checkbutton(
            notify_frame,
            text="Отправить уведомление по email",
            variable=self.notify_var,
            font=('Segoe UI', 9),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            selectcolor='white'
        )
        notify_check.pack(side='left')
        
        # Список разрешений
        permissions_frame = tk.LabelFrame(
            self.window,
            text="Текущие разрешения",
            font=('Segoe UI', 9, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            padx=6,    # Уменьшили отступы
            pady=4     # Уменьшили отступы
        )
        permissions_frame.pack(fill='both', expand=False, padx=10, pady=6)  # Убрали expand=True
        
        # Таблица разрешений
        columns = ('Email', 'Роль', 'Тип')
        self.permissions_tree = ttk.Treeview(
            permissions_frame,
            columns=columns,
            show='headings',
            height=6  # Уменьшили высоту таблицы с 8 до 6
        )
        
        # Настройка колонок
        self.permissions_tree.heading('Email', text='Email')
        self.permissions_tree.heading('Роль', text='Роль')
        self.permissions_tree.heading('Тип', text='Тип')
        
        self.permissions_tree.column('Email', width=250)  # Уменьшили ширину
        self.permissions_tree.column('Роль', width=120)   # Уменьшили ширину
        self.permissions_tree.column('Тип', width=80)     # Уменьшили ширину
        
        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(permissions_frame, orient='vertical', command=self.permissions_tree.yview)
        self.permissions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.permissions_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Привязываем горячую клавишу Ctrl+C для копирования email из таблицы
        self.permissions_tree.bind('<Control-c>', lambda e: self._copy_selected_email())
        
        # Кнопки управления (фиксированы в нижней части)
        buttons_frame = tk.Frame(self.window, bg=ModernColors.BACKGROUND, height=50)
        buttons_frame.pack(fill='x', padx=10, pady=10, side='bottom')  # Закрепляем снизу
        buttons_frame.pack_propagate(False)  # Фиксируем высоту
        
        # Создаем внутренний фрейм для центрирования кнопок
        inner_buttons_frame = tk.Frame(buttons_frame, bg=ModernColors.BACKGROUND)
        inner_buttons_frame.pack(expand=True, fill='both')
        
        ModernButton(
            inner_buttons_frame,
            text="🔄 Обновить список",  # Добавили иконку
            command=self._refresh_permissions,
            button_type="info"
        ).pack(side='left', padx=(0, 15), pady=10)
        
        ModernButton(
            inner_buttons_frame,
            text="❌ Закрыть",  # Добавили иконку
            command=self.window.destroy,
            button_type="secondary"
        ).pack(side='right', padx=(15, 0), pady=10)
    
    def _setup_url_context_menu(self):
        """Настройка контекстного меню для поля URL с функциями копирования и вставки"""
        self.url_context_menu = tk.Menu(self.window, tearoff=0)
        
        self.url_context_menu.add_command(label="Вырезать", command=self._cut_url)
        self.url_context_menu.add_command(label="Копировать", command=self._copy_url)
        self.url_context_menu.add_command(label="Вставить", command=self._paste_url)
        self.url_context_menu.add_separator()
        self.url_context_menu.add_command(label="Выделить всё", command=self._select_all_url)
        
        def show_url_context_menu(event):
            try:
                self.url_context_menu.post(event.x_root, event.y_root)
            except Exception as e:
                logger.error(f"Ошибка при показе контекстного меню URL: {e}")
        
        self.url_entry.bind("<Button-3>", show_url_context_menu)  # Правая кнопка мыши
    
    def _setup_email_context_menu(self):
        """Настройка контекстного меню для поля Email с функциями копирования и вставки"""
        self.email_context_menu = tk.Menu(self.window, tearoff=0)
        
        self.email_context_menu.add_command(label="Вырезать", command=self._cut_email)
        self.email_context_menu.add_command(label="Копировать", command=self._copy_email)
        self.email_context_menu.add_command(label="Вставить", command=self._paste_email)
        self.email_context_menu.add_separator()
        self.email_context_menu.add_command(label="Выделить всё", command=self._select_all_email)
        
        def show_email_context_menu(event):
            try:
                self.email_context_menu.post(event.x_root, event.y_root)
            except Exception as e:
                logger.error(f"Ошибка при показе контекстного меню Email: {e}")
        
        self.email_entry.bind("<Button-3>", show_email_context_menu)  # Правая кнопка мыши
    
    def _cut_url(self):
        """Вырезать текст из поля URL"""
        try:
            if self.url_entry.selection_present():
                self.url_entry.event_generate("<<Cut>>")
        except tk.TclError:
            pass
    
    def _copy_url(self):
        """Копировать текст из поля URL"""
        try:
            if self.url_entry.selection_present():
                self.url_entry.event_generate("<<Copy>>")
            else:
                # Если нет выделения, копируем весь текст
                self.window.clipboard_clear()
                self.window.clipboard_append(self.url_entry.get())
        except tk.TclError:
            pass
    
    def _paste_url(self):
        """Вставить текст в поле URL"""
        try:
            self.url_entry.event_generate("<<Paste>>")
        except tk.TclError:
            pass
    
    def _select_all_url(self):
        """Выделить весь текст в поле URL"""
        try:
            self.url_entry.select_range(0, tk.END)
            self.url_entry.icursor(tk.END)
        except tk.TclError:
            pass
    
    def _cut_email(self):
        """Вырезать текст из поля Email"""
        try:
            if self.email_entry.selection_present():
                self.email_entry.event_generate("<<Cut>>")
        except tk.TclError:
            pass
    
    def _copy_email(self):
        """Копировать текст из поля Email"""
        try:
            if self.email_entry.selection_present():
                self.email_entry.event_generate("<<Copy>>")
            else:
                # Если нет выделения, копируем весь текст
                self.window.clipboard_clear()
                self.window.clipboard_append(self.email_entry.get())
        except tk.TclError:
            pass
    
    def _paste_email(self):
        """Вставить текст в поле Email"""
        try:
            self.email_entry.event_generate("<<Paste>>")
        except tk.TclError:
            pass
    
    def _select_all_email(self):
        """Выделить весь текст в поле Email"""
        try:
            self.email_entry.select_range(0, tk.END)
            self.email_entry.icursor(tk.END)
        except tk.TclError:
            pass

    def _setup_context_menu(self):
        """Настройка контекстного меню для таблицы разрешений"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="Копировать email", command=self._copy_selected_email)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Изменить роль", command=self._change_role)
        self.context_menu.add_command(label="Удалить доступ", command=self._remove_access)
        
        def show_context_menu(event):
            try:
                # Определяем выбранную строку
                item = self.permissions_tree.identify_row(event.y)
                if item:
                    self.permissions_tree.selection_set(item)
                    self.context_menu.post(event.x_root, event.y_root)
            except Exception as e:
                logger.error(f"Ошибка при показе контекстного меню: {e}")
        
        self.permissions_tree.bind("<Button-3>", show_context_menu)  # Правая кнопка мыши
    
    def _copy_selected_email(self):
        """Копировать email выбранного пользователя из таблицы"""
        try:
            selected_items = self.permissions_tree.selection()
            if not selected_items:
                messagebox.showwarning("Предупреждение", "Выберите пользователя для копирования email")
                return
            
            item = selected_items[0]
            values = self.permissions_tree.item(item)['values']
            if values and len(values) > 0:
                email = values[0]  # Email находится в первой колонке
                self.window.clipboard_clear()
                self.window.clipboard_append(email)
                logger.info(f"Email скопирован в буфер обмена: {email}")
        except Exception as e:
            logger.error(f"Ошибка при копировании email: {e}")
            messagebox.showerror("Ошибка", f"Не удалось скопировать email: {e}")
    
    def _load_document_info(self):
        """Загрузка информации о документе"""
        try:
            url = self.url_entry.get().strip()
            if not url:
                messagebox.showwarning("Предупреждение", "Введите URL документа")
                return
            
            self.current_document_url = url
            
            # Получаем информацию о документе через сервис
            doc_info = self.document_service.get_document_info(url)
            
            if doc_info:
                self.current_doc_info = doc_info
                
                # Получаем эмодзи для типа документа
                doc_emoji = self._get_document_type_emoji(url)
                
                info_text = f"{doc_emoji} Название: {doc_info.name}\n👤 Владелец: {doc_info.owner}\n🔗 URL: {doc_info.url}"
                self.doc_info_label.config(text=info_text)
                
                # Загружаем разрешения
                self._refresh_permissions()
                
                logger.info(f"Загружена информация о документе: {doc_info.name}")
            else:
                messagebox.showerror("Ошибка", "Не удалось получить информацию о документе")
                
        except Exception as e:
            logger.error(f"Ошибка при загрузке информации о документе: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при загрузке документа: {str(e)}")
    
    def _refresh_permissions(self):
        """Обновление списка разрешений"""
        try:
            if not self.current_document_url:
                return
            
            # Очищаем таблицу
            for item in self.permissions_tree.get_children():
                self.permissions_tree.delete(item)
            
            # Получаем список разрешений
            permissions = self.document_service.list_document_permissions(self.current_document_url)
            
            if permissions:
                for perm in permissions:
                    # Показываем информацию о разрешении
                    email = getattr(perm, 'email_address', 'Неизвестно')
                    api_role = getattr(perm, 'role', 'reader')
                    display_role = self._convert_role_from_api(api_role)
                    perm_type = self.document_service.get_permission_type_description(getattr(perm, 'type', 'user'))
                    
                    self.permissions_tree.insert('', 'end', values=(email, display_role, perm_type))
                
                logger.info(f"Обновлен список разрешений: {len(permissions)} элементов")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении разрешений: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при загрузке разрешений: {str(e)}")
    
    def _add_access(self):
        """Добавление доступа к документу"""
        try:
            email = self.email_entry.get().strip()
            display_role = self.role_var.get()
            api_role = self._convert_role_to_api(display_role)
            notify = self.notify_var.get()
            
            if not email:
                messagebox.showwarning("Предупреждение", "Введите email пользователя")
                return
            
            # Простая проверка валидности email
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                messagebox.showwarning("Неверный email", 
                                     f"Введите корректный email адрес.\n"
                                     f"Пример: user@example.com")
                return
            
            # Автоматически включаем уведомления для корпоративных email
            if email.endswith('@sputnik8.com'):
                notify = True  # Принудительно включаем уведомления для корпоративного домена
                logger.info(f"Автоматически включены уведомления для корпоративного email: {email}")
            
            if not self.current_document_url:
                messagebox.showwarning("Предупреждение", "Сначала загрузите информацию о документе")
                return
            
            # Создаем объект запроса на доступ
            request = DocumentAccessRequest(
                document_url=self.current_document_url,
                user_email=email,
                role=api_role,
                notify=notify,
                message=f"Предоставлен доступ к документу с ролью '{display_role}'"
            )
            
            # Предоставляем доступ
            if self.document_service.grant_access(request):
                messagebox.showinfo("Успех", f"Доступ предоставлен пользователю {email}\nРоль: {display_role}")
                self.email_entry.delete(0, tk.END)
                self._refresh_permissions()
                logger.info(f"Предоставлен доступ пользователю {email} с ролью {display_role} ({api_role})")
            else:
                # Более подробное сообщение об ошибке
                error_msg = (
                    f"Не удалось предоставить доступ пользователю {email}.\n\n"
                    f"Возможные причины:\n"
                    f"• Email адрес не существует или недоступен\n"
                    f"• Пользователь заблокировал приглашения к документам\n"
                    f"• Недостаточно прав для предоставления доступа к этому документу\n"
                    f"• Проблемы с подключением к Google API\n"
                    f"• Пользователь уже имеет доступ\n\n"
                    f"Если email не имеет Google аккаунта, система автоматически\n"
                    f"отправит приглашение по email.\n\n"
                    f"Проверьте логи приложения для получения подробной информации."
                )
                messagebox.showerror("Ошибка предоставления доступа", error_msg)
                
        except Exception as e:
            logger.error(f"Ошибка при добавлении доступа: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при добавлении доступа: {str(e)}")
    
    def _remove_access(self):
        """Удаление доступа к документу"""
        try:
            selection = self.permissions_tree.selection()
            if not selection:
                messagebox.showwarning("Предупреждение", "Выберите разрешение для удаления")
                return
            
            item = selection[0]
            email = self.permissions_tree.item(item)['values'][0]
            
            if messagebox.askyesno("Подтверждение", f"Удалить доступ для {email}?"):
                if self.document_service.revoke_access(self.current_document_url, email):
                    messagebox.showinfo("Успех", f"Доступ отозван для пользователя {email}")
                    self._refresh_permissions()
                    logger.info(f"Отозван доступ для пользователя {email}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось отозвать доступ")
                    
        except Exception as e:
            logger.error(f"Ошибка при удалении доступа: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при удалении доступа: {str(e)}")
    
    def _change_role(self):
        """Изменение роли пользователя"""
        try:
            selection = self.permissions_tree.selection()
            if not selection:
                messagebox.showwarning("Предупреждение", "Выберите разрешение для изменения")
                return
            
            item = selection[0]
            email = self.permissions_tree.item(item)['values'][0]
            current_display_role = self.permissions_tree.item(item)['values'][1]
            
            # Создаем диалог выбора новой роли с Combobox
            dialog = tk.Toplevel(self.window)
            dialog.title("Изменение роли")
            dialog.geometry("400x200")
            dialog.configure(bg=ModernColors.BACKGROUND)
            dialog.transient(self.window)
            dialog.grab_set()
            
            # Центрируем диалог
            dialog.geometry("+%d+%d" % (self.window.winfo_rootx() + 50, 
                                       self.window.winfo_rooty() + 50))
            
            # Содержимое диалога
            tk.Label(
                dialog,
                text=f"Изменение роли для пользователя:",
                font=('Segoe UI', 10, 'bold'),
                bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_PRIMARY
            ).pack(pady=(20, 10))
            
            tk.Label(
                dialog,
                text=email,
                font=('Segoe UI', 10),
                bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_SECONDARY
            ).pack(pady=(0, 10))
            
            tk.Label(
                dialog,
                text=f"Текущая роль: {current_display_role}",
                font=('Segoe UI', 9),
                bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_SECONDARY
            ).pack(pady=(0, 15))
            
            # Выбор новой роли
            role_frame = tk.Frame(dialog, bg=ModernColors.BACKGROUND)
            role_frame.pack(pady=10)
            
            tk.Label(
                role_frame,
                text="Новая роль:",
                font=('Segoe UI', 9),
                bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_PRIMARY
            ).pack(side='left', padx=(0, 10))
            
            new_role_var = tk.StringVar(value=current_display_role)
            role_combo = ttk.Combobox(
                role_frame,
                textvariable=new_role_var,
                values=["Viewer", "Commenter", "Editor"],
                state="readonly",
                width=12
            )
            role_combo.pack(side='left')
            
            # Кнопки
            button_frame = tk.Frame(dialog, bg=ModernColors.BACKGROUND)
            button_frame.pack(pady=20)
            
            result = {'confirmed': False, 'new_role': None}
            
            def confirm():
                result['confirmed'] = True
                result['new_role'] = new_role_var.get()
                dialog.destroy()
            
            def cancel():
                dialog.destroy()
            
            ModernButton(
                button_frame,
                text="Изменить",
                command=confirm,
                button_type="success"
            ).pack(side='left', padx=(0, 10))
            
            ModernButton(
                button_frame,
                text="Отмена", 
                command=cancel,
                button_type="secondary"
            ).pack(side='left')
            
            # Ждем закрытия диалога
            dialog.wait_window()
            
            if result['confirmed'] and result['new_role']:
                new_display_role = result['new_role']
                new_api_role = self._convert_role_to_api(new_display_role)
                
                if self.document_service.change_access_role(self.current_document_url, email, new_api_role):
                    messagebox.showinfo("Успех", f"Роль изменена для {email}\nНовая роль: {new_display_role}")
                    self._refresh_permissions()
                    logger.info(f"Изменена роль для {email} на {new_display_role} ({new_api_role})")
                else:
                    messagebox.showerror("Ошибка", "Не удалось изменить роль")
                
        except Exception as e:
            logger.error(f"Ошибка при изменении роли: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при изменении роли: {str(e)}")
