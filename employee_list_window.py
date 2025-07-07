# -*- coding: utf-8 -*-
"""
Окно для отображения списка сотрудников с фильтрацией и сортировкой.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
from typing import Any, List, Dict

from ui_components import ModernColors, ModernButton, center_window
from users_api import get_user_list
from data_cache import data_cache


class EmployeeListWindow(tk.Toplevel):
    """
    Современное окно для отображения списка сотрудников с улучшенным UX.
    """
    
    def __init__(self, master, service: Any):
        super().__init__(master)
        self.title('👥 Список сотрудников')
        self.geometry('950x600')
        self.resizable(True, True)
        self.service = service
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(master)
        if master:
            center_window(self, master)

        # Инициализация данных
        self.employees = []
        self.all_employees = []

        self._create_widgets()
        self.load_employees()

    def _create_widgets(self):
        """Создает виджеты окна"""
        self._create_header()
        self._create_filters()
        self._create_table()
        self._create_bottom_panel()

    def _create_header(self):
        """Создает заголовок окна"""
        header_frame = tk.Frame(self, bg=ModernColors.PRIMARY, height=45)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text='👥 Список сотрудников', 
                font=('Segoe UI', 16, 'bold'), bg=ModernColors.PRIMARY, 
                fg='white', pady=10).pack()

    def _create_filters(self):
        """Создает панель фильтров"""
        main_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Фрейм фильтров
        filter_frame = tk.LabelFrame(main_frame, text="🔍 Фильтры и поиск", 
                                    bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY,
                                    font=('Segoe UI', 11, 'bold'), relief='flat', bd=1)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        filter_inner = tk.Frame(filter_frame, bg=ModernColors.BACKGROUND)
        filter_inner.pack(padx=10, pady=8)
        
        # Первая строка фильтров
        self._create_filter_row1(filter_inner)
        
        # Вторая строка фильтров
        self._create_filter_row2(filter_inner)
        
        # Сохраняем ссылку на main_frame для таблицы
        self.main_frame = main_frame

    def _create_filter_row1(self, parent):
        """Создает первую строку фильтров"""
        filter_row1 = tk.Frame(parent, bg=ModernColors.BACKGROUND)
        filter_row1.pack(fill='x', pady=5)
        
        # Поиск
        tk.Label(filter_row1, text='Поиск:', bg=ModernColors.BACKGROUND, 
                fg=ModernColors.TEXT_PRIMARY, font=('Segoe UI', 9, 'bold')).pack(
                side='left', padx=(0, 3))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_row1, textvariable=self.search_var, 
                               font=('Segoe UI', 9), width=20, relief='flat', 
                               bd=1, bg=ModernColors.SURFACE)
        search_entry.pack(side='left', padx=(0, 15))
        search_entry.bind('<KeyRelease>', self.apply_filters)
        
        # Статус
        tk.Label(filter_row1, text='Статус:', bg=ModernColors.BACKGROUND, 
                fg=ModernColors.TEXT_PRIMARY, font=('Segoe UI', 9, 'bold')).pack(
                side='left', padx=(0, 3))
        
        self.status_var = tk.StringVar(value="Все")
        status_combo = ttk.Combobox(filter_row1, textvariable=self.status_var, 
                                   values=["Все", "Active", "Suspended"], 
                                   state="readonly", width=10, font=('Segoe UI', 9))
        status_combo.pack(side='left', padx=(0, 15))
        status_combo.bind('<<ComboboxSelected>>', self.apply_filters)

    def _create_filter_row2(self, parent):
        """Создает вторую строку фильтров"""
        filter_row2 = tk.Frame(parent, bg=ModernColors.BACKGROUND)
        filter_row2.pack(fill='x', pady=5)
        
        # Подразделение
        tk.Label(filter_row2, text='Подразделение:', bg=ModernColors.BACKGROUND, 
                fg=ModernColors.TEXT_PRIMARY, font=('Segoe UI', 9, 'bold')).pack(
                side='left', padx=(0, 3))
        
        self.orgunit_var = tk.StringVar(value="Все")
        self.orgunit_combo = ttk.Combobox(filter_row2, textvariable=self.orgunit_var, 
                                         state="readonly", width=15, font=('Segoe UI', 9))
        self.orgunit_combo.pack(side='left', padx=(0, 15))
        self.orgunit_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Даты
        tk.Label(filter_row2, text='Дата с:', bg=ModernColors.BACKGROUND, 
                fg=ModernColors.TEXT_PRIMARY, font=('Segoe UI', 9, 'bold')).pack(
                side='left', padx=(0, 3))
        
        self.date_from_var = tk.StringVar()
        date_from_entry = tk.Entry(filter_row2, textvariable=self.date_from_var, 
                                  font=('Segoe UI', 9), width=10, relief='flat', bd=1)
        date_from_entry.pack(side='left', padx=(0, 8))
        date_from_entry.bind('<KeyRelease>', self.apply_filters)
        
        tk.Label(filter_row2, text='по:', bg=ModernColors.BACKGROUND, 
                fg=ModernColors.TEXT_PRIMARY, font=('Segoe UI', 9, 'bold')).pack(
                side='left', padx=(0, 3))
        
        self.date_to_var = tk.StringVar()
        date_to_entry = tk.Entry(filter_row2, textvariable=self.date_to_var, 
                                font=('Segoe UI', 9), width=10, relief='flat', bd=1)
        date_to_entry.pack(side='left', padx=(0, 15))
        date_to_entry.bind('<KeyRelease>', self.apply_filters)
        
        # Кнопки управления
        reset_btn = ModernButton(filter_row2, text='Сбросить фильтры', 
                                command=self.reset_filters, button_type='secondary', icon='🔄')
        reset_btn.pack(side='left', padx=(0, 10))
        
        refresh_btn = ModernButton(filter_row2, text='Обновить данные', 
                                  command=self.refresh_data, button_type='primary', icon='🔄')
        refresh_btn.pack(side='left')

    def _create_table(self):
        """Создает таблицу данных"""
        table_frame = tk.LabelFrame(self.main_frame, text="📊 Данные сотрудников", 
                                   bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY,
                                   font=('Segoe UI', 11, 'bold'), relief='flat', bd=1)
        table_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Настройка стилей Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Modern.Treeview", 
                       background=ModernColors.SURFACE,
                       foreground=ModernColors.TEXT_PRIMARY,
                       rowheight=22,
                       fieldbackground=ModernColors.SURFACE,
                       font=('Segoe UI', 9))
        style.configure("Modern.Treeview.Heading", 
                       background=ModernColors.PRIMARY_LIGHT,
                       foreground='white',
                       font=('Segoe UI', 9, 'bold'))

        # Создание Treeview
        self.tree = ttk.Treeview(table_frame, 
                                columns=('email', 'name', 'status', 'orgunit', 'created'), 
                                show='headings', height=15, style="Modern.Treeview")
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Заголовки колонок
        self.tree.heading('email', text='📧 Email', 
                         command=lambda: self.sort_column('email', False))
        self.tree.heading('name', text='👤 Имя', 
                         command=lambda: self.sort_column('name', False))
        self.tree.heading('status', text='🔘 Статус', 
                         command=lambda: self.sort_column('status', False))
        self.tree.heading('orgunit', text='🏢 Подразделение', 
                         command=lambda: self.sort_column('orgunit', False))
        self.tree.heading('created', text='📅 Дата создания', 
                         command=lambda: self.sort_column('created', False))

        # Ширина колонок
        self.tree.column('email', width=200, anchor='w')
        self.tree.column('name', width=160, anchor='w')
        self.tree.column('status', width=80, anchor='center')
        self.tree.column('orgunit', width=160, anchor='w')
        self.tree.column('created', width=100, anchor='center')

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y', padx=(0, 10), pady=10)
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _create_bottom_panel(self):
        """Создает нижнюю панель"""
        bottom_frame = tk.Frame(self, bg=ModernColors.SURFACE, height=40)
        bottom_frame.pack(fill='x', side='bottom')
        bottom_frame.pack_propagate(False)
        
        bottom_inner = tk.Frame(bottom_frame, bg=ModernColors.SURFACE)
        bottom_inner.pack(fill='both', expand=True, padx=15, pady=8)

        # Счетчик записей
        self.total_label = tk.Label(bottom_inner, text="Загрузка...", 
                                   bg=ModernColors.SURFACE, fg=ModernColors.TEXT_SECONDARY, 
                                   font=('Segoe UI', 9), anchor='w')
        self.total_label.pack(side='left')

        # Кнопка закрытия
        close_btn = ModernButton(bottom_inner, text='Закрыть', command=self.destroy, 
                                button_type='secondary', icon='❌')
        close_btn.pack(side='right')

    def load_employees(self):
        """Загружает список сотрудников асинхронно"""
        self.total_label.config(text="⏳ Загрузка данных...")
        
        # Сброс фильтров
        self.search_var.set("")
        self.status_var.set("Все")
        self.orgunit_var.set("Все")
        self.date_from_var.set("")
        self.date_to_var.set("")
        
        def load_data_async():
            """Асинхронная загрузка данных пользователей"""
            try:
                users = get_user_list(self.service)
                
                employees = []
                for user in users:
                    employee = {
                        'email': user.get('primaryEmail', ''),
                        'name': user.get('name', {}).get('fullName', ''),
                        'status': 'Suspended' if user.get('suspended', False) else 'Active',
                        'orgunit': user.get('orgUnitPath', ''),
                        'created': user.get('creationTime', '')[:10] if user.get('creationTime') else ''
                    }
                    employees.append(employee)
                
                self.after_idle(self._update_ui_with_data, employees)
                
            except Exception as e:
                self.after_idle(self._show_load_error, str(e))
        
        threading.Thread(target=load_data_async, daemon=True).start()
    
    def _update_ui_with_data(self, employees: List[Dict]):
        """Обновляет UI с загруженными данными"""
        try:
            self.employees = employees
            self.all_employees = self.employees.copy()
            
            # Заполняем список подразделений для фильтра
            orgunits = list(set(emp['orgunit'] for emp in self.employees if emp['orgunit']))
            orgunits.sort()
            self.orgunit_combo['values'] = ["Все"] + orgunits
            
            self.display_employees(self.employees)
            
        except Exception as e:
            self._show_load_error(f"Ошибка обработки данных: {e}")
    
    def _show_load_error(self, error_message: str):
        """Показывает ошибку загрузки"""
        self.total_label.config(text="❌ Ошибка загрузки")
        messagebox.showerror('Ошибка', f'Не удалось загрузить список сотрудников: {error_message}')

    def display_employees(self, employees: List[Dict]):
        """Отображает сотрудников в Treeview с оптимизацией"""
        # Очищаем существующие записи
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Добавляем новые записи батчами для лучшей производительности
        batch_size = 100
        for i in range(0, len(employees), batch_size):
            batch = employees[i:i + batch_size]
            for emp in batch:
                self.tree.insert('', 'end', values=(
                    emp['email'], emp['name'], emp['status'], 
                    emp['orgunit'], emp['created']
                ))
            
            self.update_idletasks()
        
        # Обновляем счетчик
        if hasattr(self, 'total_label'):
            self.total_label.config(text=f"📊 Показано: {len(employees)} из {len(self.all_employees)}")

    def apply_filters(self, event=None):
        """Применяет все активные фильтры"""
        query = self.search_var.get().lower()
        status = self.status_var.get()
        orgunit = self.orgunit_var.get()
        date_from = self.date_from_var.get().strip()
        date_to = self.date_to_var.get().strip()
        
        filtered = []
        for emp in self.all_employees:
            # Фильтр по поиску (email и имя)
            if query and not (query in emp['email'].lower() or query in emp['name'].lower()):
                continue
            
            # Фильтр по статусу
            if status != "Все" and emp['status'] != status:
                continue
            
            # Фильтр по подразделению
            if orgunit != "Все" and emp['orgunit'] != orgunit:
                continue
            
            # Фильтр по дате создания
            if date_from or date_to:
                emp_date = emp['created']
                if date_from and emp_date < date_from:
                    continue
                if date_to and emp_date > date_to:
                    continue
            
            filtered.append(emp)
        
        self.display_employees(filtered)

    def reset_filters(self):
        """Сбрасывает все фильтры"""
        self.search_var.set("")
        self.status_var.set("Все")
        self.orgunit_var.set("Все")
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.display_employees(self.all_employees)
    
    def refresh_data(self):
        """Принудительно обновляет данные пользователей"""
        data_cache.clear_cache()
        self.load_employees()

    def sort_column(self, col: str, reverse: bool):
        """Сортирует данные в колонке"""
        # Получаем текущие отображаемые данные
        current_data = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            current_data.append({
                'email': values[0],
                'name': values[1], 
                'status': values[2],
                'orgunit': values[3],
                'created': values[4]
            })
        
        # Сортируем текущие данные
        current_data.sort(key=lambda x: x[col], reverse=reverse)
        self.display_employees(current_data)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
