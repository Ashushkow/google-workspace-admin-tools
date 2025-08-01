# -*- coding: utf-8 -*-
"""
Окно для управления организационными подразделениями и перемещения пользователей.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import Any, Optional, List, Dict

from .ui_components import ModernColors, center_window
from ..api.users_api import get_user_list
from ..api.orgunits_api import (
    list_orgunits, 
    format_orgunits_for_combobox, 
    get_orgunit_path_from_display_name,
    get_user_orgunit,
    get_display_name_for_orgunit_path,
    move_user_to_orgunit,
    create_orgunit
)


class OrgUnitManagementWindow(tk.Toplevel):
    """
    Окно для управления организационными подразделениями и перемещения пользователей.
    """
    
    def __init__(self, master, service: Any):
        super().__init__(master)
        self.title('Управление организационными подразделениями')
        self.geometry('1000x700')
        self.resizable(True, True)
        self.service = service
        self.configure(bg='SystemButtonFace')
        self.transient(master)
        if master:
            center_window(self, master)

        # Данные
        self.orgunits = []
        self.orgunit_display_names = []
        self.users = []
        self.filtered_users = []
        
        self._load_data()
        self._create_widgets()

    def _load_data(self):
        """Загружает список OU и пользователей"""
        try:
            # Загружаем OU
            self.orgunits = list_orgunits(self.service)
            self.orgunit_display_names = format_orgunits_for_combobox(self.orgunits)
            if not self.orgunit_display_names:
                self.orgunit_display_names = ["🏠 Корневое подразделение"]
            
            # Загружаем пользователей
            self.users = get_user_list(self.service)
            self.filtered_users = self.users.copy()
            
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

    def _create_widgets(self):
        """Создает виджеты окна"""
        # Основной контейнер с горизонтальным разделением
        main_frame = tk.Frame(self, bg='SystemButtonFace')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Левая панель - фильтр по OU
        self._create_filter_panel(main_frame)
        
        # Средняя панель - список пользователей
        self._create_users_panel(main_frame)
        
        # Правая панель - операции
        self._create_operations_panel(main_frame)

    def _create_filter_panel(self, parent):
        """Создает панель фильтрации по OU"""
        filter_frame = tk.Frame(parent, bg='SystemButtonFace', relief='ridge', bd=1)
        filter_frame.pack(side='left', fill='y', padx=(0, 5))

        tk.Label(filter_frame, text='📁 Фильтр по подразделению', 
                bg='SystemButtonFace', font=('Arial', 11, 'bold')).pack(pady=(10, 5))
        
        # Выбор OU для фильтрации
        tk.Label(filter_frame, text='Подразделение:', bg='SystemButtonFace', 
                font=('Arial', 10)).pack(anchor='w', padx=10)
        
        self.filter_combo = ttk.Combobox(filter_frame, width=25, font=('Arial', 10), state='readonly')
        filter_values = ["Все подразделения"] + self.orgunit_display_names
        self.filter_combo['values'] = filter_values
        self.filter_combo.current(0)
        self.filter_combo.pack(padx=10, pady=5)
        self.filter_combo.bind('<<ComboboxSelected>>', self._filter_users)

        # Кнопка обновления
        tk.Button(filter_frame, text='🔄 Обновить', command=self._refresh_data,
                 font=('Arial', 10), width=20).pack(padx=10, pady=10)

        # Статистика
        self.stats_label = tk.Label(filter_frame, text='', bg='SystemButtonFace', 
                                   font=('Arial', 9), justify='left')
        self.stats_label.pack(padx=10, pady=10, anchor='w')
        
        self._update_stats()

    def _create_users_panel(self, parent):
        """Создает панель со списком пользователей"""
        users_frame = tk.Frame(parent, bg='SystemButtonFace', relief='ridge', bd=1)
        users_frame.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(users_frame, text='👥 Пользователи', 
                bg='SystemButtonFace', font=('Arial', 11, 'bold')).pack(pady=(10, 5))

        # Список пользователей с Treeview для показа OU
        self.users_tree = ttk.Treeview(users_frame, columns=('email', 'name', 'ou'), show='headings', height=25)
        self.users_tree.heading('email', text='Email')
        self.users_tree.heading('name', text='Имя')
        self.users_tree.heading('ou', text='Подразделение')
        
        self.users_tree.column('email', width=200, minwidth=150)
        self.users_tree.column('name', width=150, minwidth=100)
        self.users_tree.column('ou', width=200, minwidth=150)
        
        # Скроллбары для списка пользователей
        users_scroll_y = tk.Scrollbar(users_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        users_scroll_x = tk.Scrollbar(users_frame, orient=tk.HORIZONTAL, command=self.users_tree.xview)
        self.users_tree.config(yscrollcommand=users_scroll_y.set, xscrollcommand=users_scroll_x.set)
        
        self.users_tree.pack(side='left', fill='both', expand=True)
        users_scroll_y.pack(side='right', fill='y')
        users_scroll_x.pack(side='bottom', fill='x')
        
        # Заполняем список пользователей
        self._populate_users_list()

    def _create_operations_panel(self, parent):
        """Создает панель операций"""
        ops_frame = tk.Frame(parent, bg='SystemButtonFace', relief='ridge', bd=1)
        ops_frame.pack(side='right', fill='y', padx=(5, 0))

        tk.Label(ops_frame, text='⚙️ Операции', 
                bg='SystemButtonFace', font=('Arial', 11, 'bold')).pack(pady=(10, 15))

        # Выбор целевого OU
        tk.Label(ops_frame, text='Переместить в:', bg='SystemButtonFace', 
                font=('Arial', 10)).pack(anchor='w', padx=10)
        
        self.target_combo = ttk.Combobox(ops_frame, width=25, font=('Arial', 10), state='readonly')
        self.target_combo['values'] = self.orgunit_display_names
        if self.orgunit_display_names:
            self.target_combo.current(0)
        self.target_combo.pack(padx=10, pady=5)

        # Кнопки операций
        tk.Button(ops_frame, text='📁 Переместить выбранного', 
                 command=self._move_selected_user, font=('Arial', 10), 
                 width=22).pack(padx=10, pady=5)

        tk.Button(ops_frame, text='📁 Переместить всех видимых', 
                 command=self._move_all_visible_users, font=('Arial', 10), 
                 width=22).pack(padx=10, pady=5)

        # Разделитель
        tk.Frame(ops_frame, height=2, bg='gray50').pack(fill='x', padx=10, pady=10)

        # Кнопка создания нового OU
        tk.Button(ops_frame, text='➕ Создать подразделение', 
                 command=self._create_new_orgunit, font=('Arial', 10, 'bold'), 
                 width=22).pack(padx=10, pady=5)

        # Разделитель
        tk.Frame(ops_frame, height=2, bg='gray50').pack(fill='x', padx=10, pady=15)

        # Информация о выбранном пользователе
        tk.Label(ops_frame, text='ℹ️ Информация:', bg='SystemButtonFace', 
                font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)
        
        self.info_label = tk.Label(ops_frame, text='Выберите пользователя', bg='SystemButtonFace', 
                                  font=('Arial', 9), justify='left', wraplength=200)
        self.info_label.pack(anchor='w', padx=10, pady=5)

        # Область результатов
        tk.Label(ops_frame, text='📋 Результаты:', bg='SystemButtonFace', 
                font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(15, 5))
        
        self.result_text = scrolledtext.ScrolledText(ops_frame, width=30, height=10, 
                                                    wrap=tk.WORD, font=('Arial', 9))
        self.result_text.pack(padx=10, pady=5)

        # Кнопка закрытия
        tk.Button(ops_frame, text='❌ Закрыть', command=self.destroy, 
                 font=('Arial', 10), width=22).pack(padx=10, pady=(10, 20))

        # Привязываем событие выбора пользователя
        self.users_tree.bind('<<TreeviewSelect>>', self._on_user_select)

    def _populate_users_list(self):
        """Заполняет список пользователей"""
        # Очищаем список
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        # Заполняем отфильтрованными пользователями
        for user in self.filtered_users:
            email = user.get('primaryEmail', '')
            name = f"{user.get('name', {}).get('givenName', '')} {user.get('name', {}).get('familyName', '')}"
            
            # Получаем OU пользователя
            try:
                user_ou_path = get_user_orgunit(self.service, email)
                user_ou_display = get_display_name_for_orgunit_path(user_ou_path, self.orgunits)
            except:
                user_ou_display = "🏠 Корневое подразделение"
            
            self.users_tree.insert('', 'end', values=(email, name, user_ou_display))

    def _filter_users(self, event=None):
        """Фильтрует пользователей по выбранному OU"""
        selected_filter = self.filter_combo.get()
        
        if selected_filter == "Все подразделения":
            self.filtered_users = self.users.copy()
        else:
            # Получаем путь к выбранному OU
            filter_ou_path = get_orgunit_path_from_display_name(selected_filter, self.orgunits)
            
            # Фильтруем пользователей
            self.filtered_users = []
            for user in self.users:
                try:
                    user_ou_path = get_user_orgunit(self.service, user.get('primaryEmail', ''))
                    if user_ou_path == filter_ou_path:
                        self.filtered_users.append(user)
                except:
                    continue
        
        # Обновляем список
        self._populate_users_list()
        self._update_stats()

    def _update_stats(self):
        """Обновляет статистику"""
        total_users = len(self.users)
        filtered_users = len(self.filtered_users)
        
        stats_text = f"👥 Всего: {total_users}\n📋 Показано: {filtered_users}"
        self.stats_label.config(text=stats_text)

    def _on_user_select(self, event):
        """Обработка выбора пользователя"""
        selection = self.users_tree.selection()
        if not selection:
            self.info_label.config(text='Выберите пользователя')
            return
        
        item = self.users_tree.item(selection[0])
        values = item['values']
        
        if values:
            email, name, ou = values
            info_text = f"📧 {email}\n👤 {name}\n📁 {ou}"
            self.info_label.config(text=info_text)

    def _move_selected_user(self):
        """Перемещает выбранного пользователя"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для перемещения")
            return
        
        item = self.users_tree.item(selection[0])
        values = item['values']
        
        if not values:
            return
        
        email = values[0]
        target_ou_display = self.target_combo.get()
        target_ou_path = get_orgunit_path_from_display_name(target_ou_display, self.orgunits)
        
        # Проверяем, что пользователь не находится уже в целевом OU
        current_ou_path = get_user_orgunit(self.service, email)
        if current_ou_path == target_ou_path:
            self._add_result(f"❌ {email} уже находится в {target_ou_display}")
            return
        
        # Перемещаем пользователя
        result = move_user_to_orgunit(self.service, email, target_ou_path)
        
        if result['success']:
            self._add_result(f"✅ {email} перемещен в {target_ou_display}")
            # Обновляем список
            self._refresh_data()
        else:
            self._add_result(f"❌ {email}: {result['message']}")

    def _move_all_visible_users(self):
        """Перемещает всех видимых пользователей"""
        if not self.filtered_users:
            messagebox.showwarning("Предупреждение", "Нет пользователей для перемещения")
            return
        
        target_ou_display = self.target_combo.get()
        target_ou_path = get_orgunit_path_from_display_name(target_ou_display, self.orgunits)
        
        # Подтверждение
        count = len(self.filtered_users)
        if not messagebox.askyesno("Подтверждение", 
                                  f"Переместить {count} пользователей в {target_ou_display}?"):
            return
        
        success_count = 0
        error_count = 0
        
        for user in self.filtered_users:
            email = user.get('primaryEmail', '')
            
            # Проверяем, что пользователь не находится уже в целевом OU
            current_ou_path = get_user_orgunit(self.service, email)
            if current_ou_path == target_ou_path:
                self._add_result(f"⏭️ {email} уже в целевом OU")
                continue
            
            # Перемещаем пользователя
            result = move_user_to_orgunit(self.service, email, target_ou_path)
            
            if result['success']:
                success_count += 1
                self._add_result(f"✅ {email}")
            else:
                error_count += 1
                self._add_result(f"❌ {email}: {result['message']}")
        
        # Итоговая статистика
        self._add_result(f"\n📊 Успешно: {success_count}, Ошибок: {error_count}")
        
        # Обновляем список
        self._refresh_data()

    def _add_result(self, message: str):
        """Добавляет сообщение в область результатов"""
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)

    def _refresh_data(self):
        """Обновляет данные"""
        self._add_result("🔄 Обновление данных...")
        self._load_data()
        self._filter_users()
        self._add_result("✅ Данные обновлены")

    def _create_new_orgunit(self):
        """Создает новое организационное подразделение"""
        CreateOrgUnitDialog(self, self.service, self._on_orgunit_created)

    def _on_orgunit_created(self):
        """Callback после создания нового OU"""
        self._refresh_data()
        self._add_result("✅ Список подразделений обновлен")


class CreateOrgUnitDialog(tk.Toplevel):
    """Диалог для создания нового организационного подразделения"""
    
    def __init__(self, parent, service, on_created_callback=None):
        super().__init__(parent)
        self.title('Создать подразделение')
        self.geometry('500x400')
        self.resizable(False, False)
        self.service = service
        self.on_created_callback = on_created_callback
        self.configure(bg='SystemButtonFace')
        self.transient(parent)
        self.grab_set()  # Делаем диалог модальным
        
        if parent:
            center_window(self, parent)

        # Загружаем список OU для выбора родительского
        self.orgunits = []
        self.orgunit_display_names = []
        self._load_orgunits()
        
        self._create_widgets()

    def _load_orgunits(self):
        """Загружает список организационных подразделений"""
        try:
            self.orgunits = list_orgunits(self.service)
            self.orgunit_display_names = format_orgunits_for_combobox(self.orgunits)
            if not self.orgunit_display_names:
                self.orgunit_display_names = ["🏠 Корневое подразделение"]
        except Exception as e:
            print(f"Ошибка загрузки OU: {e}")
            self.orgunit_display_names = ["🏠 Корневое подразделение"]

    def _create_widgets(self):
        """Создает виджеты диалога"""
        # Заголовок
        title_label = tk.Label(self, text='➕ Создание нового подразделения', 
                              bg='SystemButtonFace', font=('Arial', 14, 'bold'))
        title_label.pack(pady=20)

        # Основная форма
        form_frame = tk.Frame(self, bg='SystemButtonFace')
        form_frame.pack(fill='both', expand=True, padx=30, pady=10)

        # Название подразделения
        tk.Label(form_frame, text='Название подразделения:', bg='SystemButtonFace', 
                font=('Arial', 11)).grid(row=0, column=0, sticky='e', padx=10, pady=10)
        self.name_entry = tk.Entry(form_frame, width=30, font=('Arial', 11))
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.name_entry.focus()

        # Родительское подразделение
        tk.Label(form_frame, text='Родительское подразделение:', bg='SystemButtonFace', 
                font=('Arial', 11)).grid(row=1, column=0, sticky='e', padx=10, pady=10)
        self.parent_combo = ttk.Combobox(form_frame, width=27, font=('Arial', 11), state='readonly')
        self.parent_combo['values'] = self.orgunit_display_names
        if self.orgunit_display_names:
            self.parent_combo.current(0)  # По умолчанию корневое
        self.parent_combo.grid(row=1, column=1, padx=10, pady=10)

        # Описание (опционально)
        tk.Label(form_frame, text='Описание (опционально):', bg='SystemButtonFace', 
                font=('Arial', 11)).grid(row=2, column=0, sticky='ne', padx=10, pady=10)
        self.description_text = scrolledtext.ScrolledText(form_frame, width=25, height=4, 
                                                         wrap=tk.WORD, font=('Arial', 10))
        self.description_text.grid(row=2, column=1, padx=10, pady=10)

        # Кнопки
        buttons_frame = tk.Frame(self, bg='SystemButtonFace')
        buttons_frame.pack(fill='x', padx=30, pady=20)

        tk.Button(buttons_frame, text='✅ Создать', command=self._create_orgunit,
                 font=('Arial', 11, 'bold'), width=15).pack(side='left', padx=10)
        
        tk.Button(buttons_frame, text='❌ Отмена', command=self.destroy,
                 font=('Arial', 11), width=15).pack(side='right', padx=10)

        # Область результата
        self.result_label = tk.Label(self, text='', bg='SystemButtonFace', 
                                    font=('Arial', 10), wraplength=400, justify='center')
        self.result_label.pack(pady=10)

        # Привязываем Enter к созданию
        self.bind('<Return>', lambda e: self._create_orgunit())

    def _create_orgunit(self):
        """Создает организационное подразделение"""
        name = self.name_entry.get().strip()
        description = self.description_text.get(1.0, tk.END).strip()
        parent_display = self.parent_combo.get()
        
        # Валидация
        if not name:
            self.result_label.config(text='❌ Укажите название подразделения', fg='red')
            return
        
        # Проверяем на недопустимые символы
        invalid_chars = ['/', '\\', '<', '>', ':', '"', '|', '?', '*']
        if any(char in name for char in invalid_chars):
            self.result_label.config(text='❌ Название содержит недопустимые символы', fg='red')
            return
        
        # Получаем путь к родительскому OU
        parent_ou_path = get_orgunit_path_from_display_name(parent_display, self.orgunits)
        
        # Создаем подразделение
        self.result_label.config(text='⏳ Создание подразделения...', fg='blue')
        self.update()
        
        result = create_orgunit(self.service, name, parent_ou_path, description)
        
        if result['success']:
            self.result_label.config(text=f'✅ {result["message"]}', fg='green')
            
            # Вызываем callback если есть
            if self.on_created_callback:
                self.after(1000, self.on_created_callback)
            
            # Закрываем диалог через 2 секунды
            self.after(2000, self.destroy)
        else:
            self.result_label.config(text=f'❌ {result["message"]}', fg='red')
