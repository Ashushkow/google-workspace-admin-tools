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
        
        # Автоматически загружаем информацию о документе по умолчанию
        if self.current_document_url:
            self.window.after(100, self._load_document_info)
    
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
        
        # Рамка для ввода URL документа
        url_frame = tk.LabelFrame(
            self.window,
            text="URL документа",
            font=('Segoe UI', 9, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            padx=6,    # Уменьшили отступы
            pady=4     # Уменьшили отступы
        )
        url_frame.pack(fill='x', padx=10, pady=6)  # Уменьшили отступы
        
        url_input_frame = tk.Frame(url_frame, bg=ModernColors.BACKGROUND)
        url_input_frame.pack(fill='x')
        
        self.url_entry = tk.Entry(
            url_input_frame,
            font=('Segoe UI', 10),
            bg='white',
            fg=ModernColors.TEXT_PRIMARY,
            relief='solid',
            bd=1
        )
        self.url_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.url_entry.insert(0, self.current_document_url)
        
        # Добавляем контекстное меню для поля URL
        self._setup_url_context_menu()
        
        ModernButton(
            url_input_frame,
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
        
        tk.Label(
            add_access_frame,
            text="Роль:",
            font=('Segoe UI', 9),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left')
        
        self.role_var = tk.StringVar(value="reader")
        role_combo = ttk.Combobox(
            add_access_frame,
            textvariable=self.role_var,
            values=["reader", "commenter", "writer"],
            state="readonly",
            width=10
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

    def _setup_context_menu(self):
        """Настройка контекстного меню для таблицы разрешений"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
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
                info_text = f"Название: {doc_info.name}\nВладелец: {doc_info.owner}\nURL: {doc_info.url}"
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
                    role = self.document_service.get_role_description(getattr(perm, 'role', 'reader'))
                    perm_type = self.document_service.get_permission_type_description(getattr(perm, 'type', 'user'))
                    
                    self.permissions_tree.insert('', 'end', values=(email, role, perm_type))
                
                logger.info(f"Обновлен список разрешений: {len(permissions)} элементов")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении разрешений: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при загрузке разрешений: {str(e)}")
    
    def _add_access(self):
        """Добавление доступа к документу"""
        try:
            email = self.email_entry.get().strip()
            role = self.role_var.get()
            notify = self.notify_var.get()
            
            if not email:
                messagebox.showwarning("Предупреждение", "Введите email пользователя")
                return
            
            if not self.current_document_url:
                messagebox.showwarning("Предупреждение", "Сначала загрузите информацию о документе")
                return
            
            # Создаем объект запроса на доступ
            request = DocumentAccessRequest(
                document_url=self.current_document_url,
                user_email=email,
                role=role,
                notify=notify,
                message=f"Предоставлен доступ к документу с ролью '{role}'"
            )
            
            # Предоставляем доступ
            if self.document_service.grant_access(request):
                messagebox.showinfo("Успех", f"Доступ предоставлен пользователю {email}")
                self.email_entry.delete(0, tk.END)
                self._refresh_permissions()
                logger.info(f"Предоставлен доступ пользователю {email} с ролью {role}")
            else:
                messagebox.showerror("Ошибка", "Не удалось предоставить доступ")
                
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
            current_role = self.permissions_tree.item(item)['values'][1]
            
            # Диалог выбора новой роли
            new_role = simpledialog.askstring(
                "Изменение роли",
                f"Текущая роль для {email}: {current_role}\n\nВведите новую роль (reader/commenter/writer):",
                initialvalue="reader"
            )
            
            if new_role and new_role in ['reader', 'commenter', 'writer']:
                if self.document_service.change_access_role(self.current_document_url, email, new_role):
                    messagebox.showinfo("Успех", f"Роль изменена для {email}")
                    self._refresh_permissions()
                    logger.info(f"Изменена роль для {email} на {new_role}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось изменить роль")
            elif new_role:
                messagebox.showwarning("Предупреждение", "Неверная роль. Используйте: reader, commenter, writer")
                
        except Exception as e:
            logger.error(f"Ошибка при изменении роли: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при изменении роли: {str(e)}")
