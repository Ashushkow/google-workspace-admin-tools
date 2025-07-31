#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Специализированное окно для управления календарем SPUTНIK (общий).
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from typing import Any, Optional, List, Dict
import threading
import os
from datetime import datetime

from .ui_components import ModernColors, ModernButton, center_window
from ..utils.file_paths import get_export_path


class SputnikCalendarWindow(tk.Toplevel):
    """Окно управления календарем SPUTНIK (общий)"""
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master_window = master
        self.calendar_manager = None
        self.is_window_active = True  # Флаг для отслеживания состояния окна
        
        # Настройка окна
        self.title('📅 Управление календарем SPUTНIK (общий)')
        self.geometry('900x700')
        self.resizable(True, True)
        self.configure(bg=ModernColors.BACKGROUND)
        if master:
            self.transient(master)
            center_window(self, master)
        
        # Обработчик закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        self.setup_ui()
        self.initialize_calendar()
    
    def on_window_close(self):
        """Обработчик закрытия окна"""
        self.is_window_active = False
        self.destroy()
    
    def safe_update_ui(self, update_func):
        """Безопасное обновление UI с проверкой состояния окна"""
        if not self.is_window_active:
            return
        
        try:
            if self.winfo_exists():
                update_func()
        except tk.TclError:
            # Окно было закрыто, игнорируем ошибку
            self.is_window_active = False
        except Exception:
            # Другие ошибки также могут указывать на закрытое окно
            self.is_window_active = False
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        title_label = tk.Label(
            header_frame,
            text='🎯 КАЛЕНДАРЬ SPUTНIK (ОБЩИЙ)',
            font=('Arial', 18, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        title_label.pack(side='left')
        
        # Информация о календаре
        self.info_label = tk.Label(
            header_frame,
            text='Инициализация...',
            font=('Arial', 10),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_SECONDARY
        )
        self.info_label.pack(side='right')
        
        # Панель управления
        control_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        control_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Левая группа кнопок
        left_buttons = tk.Frame(control_frame, bg=ModernColors.BACKGROUND)
        left_buttons.pack(side='left')
        
        ModernButton(
            left_buttons,
            text='🔄 Обновить',
            command=self.refresh_members,
            style='primary'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            left_buttons,
            text='➕ Добавить участника',
            command=self.add_member_dialog,
            style='success'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            left_buttons,
            text='📁 Массовое добавление',
            command=self.bulk_add_members,
            style='info'
        ).pack(side='left', padx=(0, 8))
        
        # Правая группа кнопок
        right_buttons = tk.Frame(control_frame, bg=ModernColors.BACKGROUND)
        right_buttons.pack(side='right')
        
        ModernButton(
            right_buttons,
            text='📊 Статистика',
            command=self.show_statistics,
            style='secondary'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            right_buttons,
            text='💾 Экспорт',
            command=self.export_members,
            style='secondary'
        ).pack(side='left', padx=(0, 8))
        
        # Основная область с участниками
        main_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Поле поиска
        search_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        search_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            search_frame,
            text='🔍 Поиск:',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_members)
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            width=30
        )
        search_entry.pack(side='left', padx=(0, 10))
        
        # Фильтр по роли
        tk.Label(
            search_frame,
            text='Роль:',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left', padx=(0, 5))
        
        self.role_filter = ttk.Combobox(
            search_frame,
            values=['Все', 'Владелец', 'Редактор', 'Читатель'],
            state='readonly',
            width=12
        )
        self.role_filter.set('Все')
        self.role_filter.bind('<<ComboboxSelected>>', self.filter_members)
        self.role_filter.pack(side='left')
        
        # Список участников
        list_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        list_frame.pack(fill='both', expand=True)
        
        # Настройка Treeview
        columns = ('email', 'role', 'actions')
        self.members_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=15,
            selectmode='extended'
        )
        
        # Настройка заголовков
        self.members_tree.heading('email', text='📧 Email участника')
        self.members_tree.heading('role', text='👤 Роль')
        self.members_tree.heading('actions', text='⚙️ Действия')
        
        # Настройка колонок
        self.members_tree.column('email', width=400, anchor='w')
        self.members_tree.column('role', width=150, anchor='center')
        self.members_tree.column('actions', width=200, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.members_tree.yview)
        self.members_tree.configure(yscrollcommand=scrollbar.set)
        
        # Привязка событий
        self.members_tree.bind('<Double-1>', self.on_member_double_click)
        self.members_tree.bind('<Button-3>', self.show_context_menu)
        
        # Упаковка
        self.members_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Контекстное меню
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="✏️ Изменить роль", command=self.change_member_role)
        self.context_menu.add_command(label="🗑️ Удалить участника", command=self.remove_selected_member)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Копировать email", command=self.copy_email)
        
        # Статус бар
        status_frame = tk.Frame(self, bg=ModernColors.SURFACE)
        status_frame.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(
            status_frame,
            text='Готов к работе',
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_SECONDARY,
            anchor='w',
            padx=10,
            pady=5
        )
        self.status_label.pack(side='left', fill='x', expand=True)
        
        self.members_count_label = tk.Label(
            status_frame,
            text='Участников: 0',
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_SECONDARY,
            padx=10,
            pady=5
        )
        self.members_count_label.pack(side='right')
        
        # Кнопка "Загрузить еще" для расширенной загрузки
        load_more_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        load_more_frame.pack(fill='x', pady=(5, 10))
        
        self.load_more_button = tk.Button(
            load_more_frame,
            text='📥 Загрузить больше пользователей (100→500)',
            command=self.load_more_users,
            bg=ModernColors.PRIMARY,
            fg='white',
            font=('Arial', 9),
            relief='flat',
            padx=10,
            pady=5
        )
        self.load_more_button.pack(anchor='center')
        self.load_more_button.pack_forget()  # Скрываем изначально
        
        # ...existing code...
    
    def initialize_calendar(self):
        """Инициализация календаря в отдельном потоке"""
        def init_worker():
            try:
                self.safe_update_ui(lambda: self.status_label.config(text='Подключение к календарю SPUTНIK...'))
                
                from ..api.sputnik_calendar import create_sputnik_calendar_manager
                self.calendar_manager = create_sputnik_calendar_manager()
                
                if self.calendar_manager:
                    calendar_info = self.calendar_manager.get_calendar_info()
                    
                    self.safe_update_ui(lambda: self.info_label.config(
                        text=f'Владелец: {calendar_info.owner if calendar_info else "Неизвестно"}'
                    ))
                    
                    self.safe_update_ui(lambda: self.status_label.config(text='✅ Подключено к календарю SPUTНIK'))
                    self.safe_update_ui(self.load_members)
                else:
                    self.safe_update_ui(lambda: self.status_label.config(text='❌ Ошибка подключения к календарю'))
                    self.safe_update_ui(lambda: messagebox.showerror(
                        "Ошибка",
                        "Не удалось подключиться к календарю SPUTНIK.\n"
                        "Проверьте настройки аутентификации."
                    ))
                    
            except Exception as e:
                self.safe_update_ui(lambda: self.status_label.config(text='❌ Ошибка инициализации'))
                self.safe_update_ui(lambda: messagebox.showerror("Ошибка", f"Ошибка инициализации:\n{str(e)}"))
        
        # Запускаем инициализацию в отдельном потоке
        threading.Thread(target=init_worker, daemon=True).start()
    
    def load_members(self):
        """Загрузка участников календаря"""
        if not self.calendar_manager:
            return
        
        def load_worker():
            try:
                self.safe_update_ui(lambda: self.status_label.config(text='Загрузка участников...'))
                
                members = self.calendar_manager.get_members()
                
                self.safe_update_ui(lambda: self._update_members_list(members))
                self.safe_update_ui(lambda: self.status_label.config(text=f'✅ Загружено участников: {len(members)}'))
                
            except Exception as e:
                self.safe_update_ui(lambda: self.status_label.config(text='❌ Ошибка загрузки'))
                self.safe_update_ui(lambda: messagebox.showerror("Ошибка", f"Ошибка загрузки участников:\n{str(e)}"))
        
        threading.Thread(target=load_worker, daemon=True).start()
    
    def _update_members_list(self, members):
        """Обновление списка участников в UI"""
        if not self.is_window_active:
            return
            
        try:
            # Сохраняем текущий выбор
            selected_items = self.members_tree.selection()
            selected_emails = []
            for item in selected_items:
                values = self.members_tree.item(item)['values']
                if values:
                    selected_emails.append(values[0])
            
            # Очищаем список
            for item in self.members_tree.get_children():
                self.members_tree.delete(item)
            
            # Добавляем участников
            for member in members:
                role_display = self._translate_role(member.role)
                actions = "Изменить • Удалить"
                
                item_id = self.members_tree.insert('', 'end', values=(
                    member.email,
                    role_display,
                    actions
                ))
                
                # Восстанавливаем выбор, если email был выбран ранее
                if member.email in selected_emails:
                    self.members_tree.selection_add(item_id)
            
            # Обновляем счетчик
            self.members_count_label.config(text=f'Участников: {len(members)}')
            
        except tk.TclError:
            # Виджет был уничтожен
            self.is_window_active = False
        except Exception:
            # Другие ошибки также могут указывать на проблемы с виджетами
            self.is_window_active = False
        self.filter_members()
    
    def _translate_role(self, role: str) -> str:
        """Перевод роли на русский язык"""
        translations = {
            'owner': '👑 Владелец',
            'writer': '✏️ Редактор', 
            'reader': '👁️ Читатель',
            'freeBusyReader': '⏰ Просмотр занятости'
        }
        return translations.get(role, role)
    
    def filter_members(self, *args):
        """Улучшенная фильтрация участников по поиску и роли"""
        search_text = self.search_var.get().lower().strip()
        role_filter = self.role_filter.get()
        
        # Получаем все элементы
        all_items = []
        for item in self.members_tree.get_children():
            values = self.members_tree.item(item)['values']
            all_items.append((item, values))
        
        # Удаляем все элементы
        for item, _ in all_items:
            self.members_tree.delete(item)
        
        # Фильтруем и добавляем обратно
        visible_count = 0
        for item, values in all_items:
            email, role, actions = values
            
            # Улучшенный фильтр по тексту поиска
            if search_text:
                # Поиск по email (до @ и после @)
                email_parts = email.lower().split('@')
                name_part = email_parts[0] if email_parts else ''
                domain_part = email_parts[1] if len(email_parts) > 1 else ''
                
                # Проверяем вхождение в разные части
                if not (search_text in email.lower() or 
                       search_text in name_part or 
                       search_text in domain_part or
                       any(search_text in part for part in name_part.split('.'))):
                    continue
            
            # Фильтр по роли
            if role_filter != 'Все':
                if role_filter not in role:
                    continue
            
            # Добавляем элемент обратно
            new_item = self.members_tree.insert('', 'end', values=values)
            visible_count += 1
        
        # Обновляем счетчик с дополнительной информацией
        total_count = len(all_items)
        if visible_count != total_count:
            if search_text:
                self.members_count_label.config(text=f'Найдено: {visible_count} из {total_count} (поиск: "{search_text}")')
            else:
                self.members_count_label.config(text=f'Участников: {visible_count} из {total_count}')
        else:
            self.members_count_label.config(text=f'Участников: {total_count}')
        
        # Если нет результатов поиска, показываем подсказку
        if search_text and visible_count == 0:
            self.status_label.config(text=f'🔍 Не найдено участников по запросу: "{search_text}"')
    
    def refresh_members(self):
        """Обновление списка участников"""
        self.load_members()
    
    def add_member_dialog(self):
        """Диалог добавления участника"""
        AddSputnikMemberDialog(self, self.calendar_manager, self.refresh_members)
    
    def bulk_add_members(self):
        """Массовое добавление участников из файла"""
        if not self.calendar_manager:
            messagebox.showerror("Ошибка", "Календарь не инициализирован")
            return
        
        BulkAddMembersDialog(self, self.calendar_manager, self.refresh_members)
    
    def change_member_role(self):
        """Изменение роли выбранного участника"""
        selection = self.members_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите участника для изменения роли")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Предупреждение", "Выберите только одного участника")
            return
        
        item = self.members_tree.item(selection[0])
        values = item.get('values', [])
        if not values:
            return
        
        email = values[0]
        current_role = values[1]
        
        ChangeSputnikRoleDialog(self, self.calendar_manager, email, current_role, self.refresh_members)
    
    def remove_selected_member(self):
        """Удаление выбранных участников"""
        selection = self.members_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите участника(ов) для удаления")
            return
        
        emails = []
        for item in selection:
            values = self.members_tree.item(item).get('values', [])
            if values:
                emails.append(values[0])
        
        if not emails:
            return
        
        # Подтверждение
        if len(emails) == 1:
            message = f"Удалить участника {emails[0]} из календаря SPUTНIK?"
        else:
            message = f"Удалить {len(emails)} участников из календаря SPUTНIK?"
        
        if not messagebox.askyesno("Подтверждение", message):
            return
        
        # Удаляем участников
        def remove_worker():
            try:
                self.safe_update_ui(lambda: self.status_label.config(text='Удаление участников...'))
                
                successful = 0
                for email in emails:
                    if self.calendar_manager.remove_member(email):
                        successful += 1
                
                self.safe_update_ui(lambda: self.status_label.config(
                    text=f'✅ Удалено участников: {successful}/{len(emails)}'
                ))
                self.safe_update_ui(self.refresh_members)
                
                if successful == len(emails):
                    self.safe_update_ui(lambda: messagebox.showinfo("Успех", "Все участники успешно удалены"))
                else:
                    self.safe_update_ui(lambda: messagebox.showwarning(
                        "Частичный успех",
                        f"Удалено {successful} из {len(emails)} участников"
                    ))
                    
            except Exception as e:
                self.safe_update_ui(lambda: self.status_label.config(text='❌ Ошибка удаления'))
                self.safe_update_ui(lambda: messagebox.showerror("Ошибка", f"Ошибка удаления:\n{str(e)}"))
        
        threading.Thread(target=remove_worker, daemon=True).start()
    
    def copy_email(self):
        """Копирование email в буфер обмена"""
        selection = self.members_tree.selection()
        if not selection:
            return
        
        item = self.members_tree.item(selection[0])
        values = item.get('values', [])
        if values:
            email = values[0]
            self.clipboard_clear()
            self.clipboard_append(email)
            self.status_label.config(text=f'📋 Email скопирован: {email}')
    
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        # Выбираем элемент под курсором
        item = self.members_tree.identify_row(event.y)
        if item:
            self.members_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_member_double_click(self, event):
        """Обработка двойного клика по участнику"""
        self.change_member_role()
    
    def show_statistics(self):
        """Показ статистики календаря"""
        if not self.calendar_manager:
            messagebox.showerror("Ошибка", "Календарь не инициализирован")
            return
        
        SputnikStatisticsWindow(self, self.calendar_manager)
    
    def export_members(self):
        """Экспорт списка участников"""
        if not self.calendar_manager:
            messagebox.showerror("Ошибка", "Календарь не инициализирован")
            return
        
        # Предлагаем сохранить в папку экспорта
        suggested_filename = f"calendar_members_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        suggested_path = get_export_path(suggested_filename)
        
        # Выбор файла для сохранения
        filename = filedialog.asksaveasfilename(
            initialfile=str(suggested_path),
            title="Экспорт участников",
            defaultextension=".csv",
            filetypes=[
                ("CSV файлы", "*.csv"),
                ("Excel файлы", "*.xlsx"),
                ("Все файлы", "*.*")
            ]
        )
        
        if not filename:
            return
        
        def export_worker():
            try:
                self.safe_update_ui(lambda: self.status_label.config(text='Экспорт участников...'))
                
                members_data = self.calendar_manager.export_members_to_dict()
                
                if filename.endswith('.csv'):
                    self._export_to_csv(members_data, filename)
                elif filename.endswith('.xlsx'):
                    self._export_to_excel(members_data, filename)
                else:
                    self._export_to_csv(members_data, filename)
                
                self.safe_update_ui(lambda: self.status_label.config(text=f'✅ Экспорт завершен: {filename}'))
                self.safe_update_ui(lambda: messagebox.showinfo("Успех", f"Данные экспортированы в:\n{filename}"))
                
            except Exception as e:
                self.safe_update_ui(lambda: self.status_label.config(text='❌ Ошибка экспорта'))
                self.safe_update_ui(lambda: messagebox.showerror("Ошибка", f"Ошибка экспорта:\n{str(e)}"))
        
        threading.Thread(target=export_worker, daemon=True).start()
    
    def _export_to_csv(self, members_data, filename):
        """Экспорт в CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if members_data:
                fieldnames = members_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for member in members_data:
                    writer.writerow(member)
    
    def _export_to_excel(self, members_data, filename):
        """Экспорт в Excel"""
        try:
            import pandas as pd
            
            df = pd.DataFrame(members_data)
            df.to_excel(filename, index=False)
            
        except ImportError:
            # Fallback к CSV если pandas не установлен
            messagebox.showwarning(
                "Предупреждение",
                "Pandas не установлен. Экспорт в CSV формате."
            )
            csv_filename = filename.replace('.xlsx', '.csv')
            self._export_to_csv(members_data, csv_filename)
    
    def load_more_users(self):
        """Загрузка дополнительных пользователей (до 500)"""
        self.load_more_button.config(state='disabled', text='🔄 Загрузка...')
        
        def load_more_worker():
            try:
                self.safe_update_ui(lambda: self.loading_label.config(
                    text='📋 Загрузка дополнительных пользователей...',
                    fg='blue'
                ))
                
                # Создаем Directory API сервис
                from googleapiclient.discovery import build
                credentials = self.calendar_manager.calendar_api.credentials
                directory_service = build('admin', 'directory_v1', credentials=credentials)
                
                # Загружаем больше пользователей
                users_result = directory_service.users().list(
                    domain='sputnik8.com',
                    maxResults=500,  # Полная загрузка
                    orderBy='givenName'
                ).execute()
                
                users = users_result.get('users', [])
                
                # Обрабатываем пользователей
                sputnik_users = []
                for user in users:
                    email = user.get('primaryEmail', '')
                    if '@sputnik8.com' in email:
                        full_name = user.get('name', {}).get('fullName', email.split('@')[0])
                        suspended = user.get('suspended', False)
                        
                        sputnik_users.append({
                            'email': email,
                            'name': full_name,
                            'suspended': suspended,
                            'status': 'Заблокирован' if suspended else 'Активен'
                        })
                
                # Сортируем по имени
                sputnik_users.sort(key=lambda x: x['name'])
                
                # Обновляем кэш
                self.users_cache = sputnik_users
                
                # Обновляем UI
                self.safe_update_ui(lambda: self._update_users_list(sputnik_users))
                self.safe_update_ui(lambda: self.loading_label.config(
                    text=f'✅ Загружено {len(sputnik_users)} пользователей (полный список)',
                    fg='green'
                ))
                self.safe_update_ui(lambda: self.load_more_button.pack_forget())
                
            except Exception as e:
                self.safe_update_ui(lambda: self.loading_label.config(
                    text=f'❌ Ошибка расширенной загрузки: {str(e)[:50]}...',
                    fg='red'
                ))
                self.safe_update_ui(lambda: self.load_more_button.config(
                    state='normal', 
                    text='📥 Попробовать еще раз'
                ))
        
        # Запускаем в отдельном потоке
        threading.Thread(target=load_more_worker, daemon=True).start()
    
    # ...existing code...
    
    def on_user_select(self, event):
        """Обработка выбора пользователя"""
        selection = self.users_tree.selection()
        if not selection:
            self.selected_label.config(text='Выберите сотрудника из списка')
            self.add_button.config(state='disabled')
            return
        
        item = self.users_tree.item(selection[0])
        values = item.get('values', [])
        if not values:
            return
        
        name, email, status = values
        name = name.replace('🔗 ', '')  # Убираем префикс для уже добавленных
        
        # Обновляем информацию о выбранном пользователе
        role_desc = self._get_role_description(self.role_var.get())
        self.selected_label.config(
            text=f'👤 Выбран: {name} ({email})\\n🔐 Будет добавлен как: {role_desc}'
        )
        
        # Включаем/отключаем кнопку добавления
        if status == 'Уже в календаре':
            self.add_button.config(state='disabled', text='✅ Уже в календаре')
        elif status == 'Заблокирован':
            self.add_button.config(state='disabled', text='⚠️ Пользователь заблокирован')
        else:
            self.add_button.config(state='normal', text='✅ Добавить к календарю')
    
    def on_user_double_click(self, event):
        """Обработка двойного клика по пользователю"""
        if self.add_button['state'] != 'disabled':
            self.add_member()
    
    def _get_role_description(self, role):
        """Получение описания роли"""
        descriptions = {
            'reader': '👁️ Читатель',
            'writer': '✏️ Редактор',
            'owner': '👑 Владелец'
        }
        return descriptions.get(role, role)
    
    def add_member(self):
        """Добавление выбранного участника"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника из списка")
            return
        
        item = self.users_tree.item(selection[0])
        values = item.get('values', [])
        if not values:
            return
        
        name, email, status = values
        name = name.replace('🔗 ', '')  # Убираем префикс
        role = self.role_var.get()
        
        if status == 'Уже в календаре':
            messagebox.showinfo("Информация", f"Пользователь {name} уже добавлен к календарю SPUTНIK")
            return
        
        if status == 'Заблокирован':
            if not messagebox.askyesno(
                "Предупреждение", 
                f"Пользователь {name} заблокирован.\\nВы уверены, что хотите добавить его к календарю?"
            ):
                return
        
        # Подтверждение добавления
        role_desc = self._get_role_description(role)
        if not messagebox.askyesno(
            "Подтверждение",
            f"Добавить пользователя {name} к календарю SPUTНIK?\\n\\n"
            f"Email: {email}\\n"
            f"Роль: {role_desc}\\n\\n"
            f"Пользователь получит доступ к общему календарю команды."
        ):
            return
        
        def add_worker():
            try:
                success = self.calendar_manager.add_member(email, role, name)
                
                if success:
                    self.safe_update_ui(lambda: messagebox.showinfo(
                        "Успех",
                        f"Пользователь {name} добавлен к календарю SPUTНIK\\n\\n"
                        f"Email: {email}\\n"
                        f"Роль: {role_desc}\\n\\n"
                        f"Пользователь получит уведомление о доступе к календарю."
                    ))
                    if self.refresh_callback:
                        self.safe_update_ui(self.refresh_callback)
                    self.safe_update_ui(self.destroy)
                else:
                    self.safe_update_ui(lambda: messagebox.showerror(
                        "Ошибка",
                        f"Не удалось добавить пользователя {name} к календарю.\\n\\n"
                        f"Возможные причины:\\n"
                        f"• Недостаточно прав доступа\\n"
                        f"• Пользователь уже добавлен\\n"
                        f"• Проблемы с подключением к Google Calendar API"
                    ))
                    
            except Exception as e:
                self.safe_update_ui(lambda: messagebox.showerror(
                    "Ошибка",
                    f"Ошибка добавления пользователя {name}:\\n\\n{str(e)}"
                ))
        
        threading.Thread(target=add_worker, daemon=True).start()


class AddSputnikMemberDialog(tk.Toplevel):
    """Оптимизированный диалог добавления участника к календарю SPUTНIK с быстрой загрузкой"""
    
    def __init__(self, parent, calendar_manager, refresh_callback):
        super().__init__(parent)
        self.parent = parent
        self.calendar_manager = calendar_manager
        self.refresh_callback = refresh_callback
        self.domain_users = []
        self.filtered_users = []
        
        # Переменные для управления загрузкой
        self.loading_cancelled = False
        self.loading_thread = None
        self.users_cache = None  # Кэш пользователей
        
        # Настройка окна
        self.title('Добавить участника к календарю SPUTНIK')
        self.geometry('580x420')
        self.resizable(True, True)
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(parent)
        
        center_window(self, parent)
        self.setup_ui()
        self.load_domain_users()
    
    def setup_ui(self):
        """Настройка UI диалога"""
        # Заголовок
        header_label = tk.Label(
            self,
            text='➕ Добавить участника к календарю SPUTНIK',
            font=('Arial', 13, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        header_label.pack(pady=10)
        
        # Основной контейнер
        main_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=15, pady=8)
        
        # Поиск сотрудников
        search_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        search_frame.pack(fill='x', pady=(0, 8))
        
        tk.Label(
            search_frame,
            text='🔍 Поиск сотрудника:',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_users)
        search_entry = tk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=('Arial', 11), 
            width=50
        )
        search_entry.pack(fill='x', pady=(0, 5))
        search_entry.focus()
        
        # Статус загрузки с кнопкой отмены
        loading_frame = tk.Frame(search_frame, bg=ModernColors.BACKGROUND)
        loading_frame.pack(fill='x', pady=(0, 5))
        
        self.loading_label = tk.Label(
            loading_frame,
            text='Загрузка сотрудников домена sputnik8.com...',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_SECONDARY,
            font=('Arial', 9, 'italic')
        )
        self.loading_label.pack(side='left')
        
        self.cancel_button = tk.Button(
            loading_frame,
            text='❌ Отмена',
            command=self.cancel_loading,
            bg=ModernColors.ERROR,
            fg='white',
            font=('Arial', 8),
            relief='flat',
            padx=8,
            pady=2
        )
        self.cancel_button.pack(side='right')
        self.cancel_button.pack_forget()  # Скрываем изначально
        
        # Список сотрудников
        list_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        list_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        tk.Label(
            list_frame,
            text='👥 Выберите сотрудника из списка:',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        # Создаем Treeview для списка пользователей
        columns = ('name', 'email', 'status')
        self.users_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=8
        )
        
        # Настройка колонок
        self.users_tree.heading('name', text='Имя')
        self.users_tree.heading('email', text='Email')
        self.users_tree.heading('status', text='Статус')
        
        self.users_tree.column('name', width=180)
        self.users_tree.column('email', width=250)
        self.users_tree.column('status', width=120)
        
        # Scrollbar для списка
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Упаковка списка
        self.users_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Привязка событий
        self.users_tree.bind('<Double-1>', self.on_user_double_click)
        self.users_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # Кнопка "Загрузить еще" для расширенной загрузки
        load_more_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        load_more_frame.pack(fill='x', pady=(5, 10))
        
        self.load_more_button = tk.Button(
            load_more_frame,
            text='📥 Загрузить больше пользователей (50→500)',
            command=self.load_more_users,
            bg=ModernColors.PRIMARY,
            fg='white',
            font=('Arial', 9),
            relief='flat',
            padx=10,
            pady=5
        )
        self.load_more_button.pack(anchor='center')
        self.load_more_button.pack_forget()  # Скрываем изначально
        
        # Выбор роли
        role_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        role_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            role_frame,
            text='🔐 Права доступа к календарю:',
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        self.role_var = tk.StringVar(value='reader')
        
        # Создаем фрейм для ролей в одну строку
        roles_container = tk.Frame(role_frame, bg=ModernColors.BACKGROUND)
        roles_container.pack(fill='x')
        
        roles = [
            ('reader', '👁️ Просмотр', 'Чтение событий'),
            ('writer', '✏️ Редактирование', 'Создание и изменение'),
            ('owner', '👑 Управление', 'Полный доступ')
        ]
        
        for i, (role_value, role_title, role_desc) in enumerate(roles):
            # Создаем фрейм для каждой роли
            role_column = tk.Frame(roles_container, bg=ModernColors.BACKGROUND)
            role_column.pack(side='left', padx=(0, 15), fill='x', expand=True)
            
            role_button = tk.Radiobutton(
                role_column,
                text=role_title,
                variable=self.role_var,
                value=role_value,
                bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_PRIMARY,
                selectcolor=ModernColors.SURFACE,
                font=('Arial', 9, 'bold'),
                justify='left'
            )
            role_button.pack(anchor='w')
            
            # Описание под радиокнопкой
            desc_label = tk.Label(
                role_column,
                text=role_desc,
                bg=ModernColors.BACKGROUND,
                fg=ModernColors.TEXT_SECONDARY,
                font=('Arial', 8),
                justify='left'
            )
            desc_label.pack(anchor='w')
        
        # Информация о выбранном пользователе
        self.selected_info_frame = tk.Frame(main_frame, bg=ModernColors.SURFACE, relief='groove', bd=1)
        self.selected_info_frame.pack(fill='x', pady=(0, 10))
        
        self.selected_label = tk.Label(
            self.selected_info_frame,
            text='Выберите сотрудника из списка',
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_SECONDARY,
            font=('Arial', 9, 'italic'),
            padx=8,
            pady=5
        )
        self.selected_label.pack(fill='x')
        
        # Кнопки
        buttons_frame = tk.Frame(main_frame, bg=ModernColors.BACKGROUND)
        buttons_frame.pack(fill='x')
        
        self.add_button = ModernButton(
            buttons_frame,
            text='✅ Добавить к календарю',
            command=self.add_member,
            style='success',
            state='disabled'
        )
        self.add_button.pack(side='right', padx=(8, 0))
        
        ModernButton(
            buttons_frame,
            text='❌ Отмена',
            command=self.destroy,
            style='secondary'
        ).pack(side='right')
    
    def cancel_loading(self):
        """Отмена загрузки пользователей"""
        self.loading_cancelled = True
        self.loading_label.config(
            text='❌ Загрузка отменена',
            fg='red'
        )
        self.cancel_button.pack_forget()
        
        # Используем fallback пользователей
        self._create_fallback_users()
    
    def safe_update_ui(self, update_func):
        """Безопасное обновление UI с проверкой состояния окна"""
        try:
            if self.winfo_exists():
                update_func()
        except tk.TclError:
            # Окно было закрыто, игнорируем ошибку
            pass
        except Exception:
            # Другие ошибки также могут указывать на закрытое окно
            pass
    
    def load_domain_users(self):
        """Загрузка пользователей домена с кэшированием и быстрой отменой"""
        # Если есть кэш, используем его
        if self.users_cache:
            self.loading_label.config(
                text='✅ Пользователи загружены из кэша',
                fg='green'
            )
            self._update_users_list(self.users_cache)
            # Показываем кнопку "Загрузить еще", если в кэше мало пользователей
            if len(self.users_cache) <= 50:
                self.load_more_button.pack(anchor='center')
            return
        
        # Показываем кнопку отмены
        self.cancel_button.pack(side='right')
        self.loading_cancelled = False
        
        def load_worker():
            try:
                # Обновляем статус загрузки
                self.safe_update_ui(lambda: self.loading_label.config(
                    text='🔄 Подключение к Google Directory API...',
                    fg='blue'
                ))
                
                # Используем тот же API, что и для календаря
                if not self.calendar_manager or not self.calendar_manager.calendar_api.credentials:
                    self.safe_update_ui(lambda: self.loading_label.config(
                        text='❌ Календарь не инициализирован',
                        fg='red'
                    ))
                    self.safe_update_ui(lambda: self.cancel_button.pack_forget())
                    return
                
                # Создаем Directory API сервис используя те же credentials
                from googleapiclient.discovery import build
                credentials = self.calendar_manager.calendar_api.credentials
                
                directory_service = build('admin', 'directory_v1', credentials=credentials)
                
                # Проверка на отмену после подключения
                if self.loading_cancelled:
                    return
                
                # Обновляем статус
                self.safe_update_ui(lambda: self.loading_label.config(
                    text='📋 Загрузка первых 50 пользователей...',
                    fg='blue'
                ))
                
                # Запрашиваем пользователей домена с ограничением для быстрой загрузки
                users_result = directory_service.users().list(
                    domain='sputnik8.com',
                    maxResults=50,  # Быстрая загрузка
                    orderBy='givenName'
                ).execute()
                
                users = users_result.get('users', [])
                
                # Проверяем на отмену
                if self.loading_cancelled:
                    return
                
                # Обновляем статус обработки
                self.safe_update_ui(lambda: self.loading_label.config(
                    text=f'⚙️ Обработка {len(users)} пользователей...',
                    fg='blue'
                ))
                
                # Обрабатываем пользователей
                sputnik_users = []
                for i, user in enumerate(users):
                    # Проверяем на отмену каждые 5 пользователей для быстрой реакции
                    if i % 5 == 0 and self.loading_cancelled:
                        return
                    
                    email = user.get('primaryEmail', '')
                    if '@sputnik8.com' in email:
                        full_name = user.get('name', {}).get('fullName', email.split('@')[0])
                        suspended = user.get('suspended', False)
                        
                        sputnik_users.append({
                            'email': email,
                            'name': full_name,
                            'suspended': suspended,
                            'status': 'Заблокирован' if suspended else 'Активен'
                        })
                
                # Сортируем по имени
                sputnik_users.sort(key=lambda x: x['name'])
                
                # Финальная проверка на отмену
                if self.loading_cancelled:
                    return
                
                # Сохраняем в кэш
                self.users_cache = sputnik_users
                
                # Обновляем UI в главном потоке
                self.safe_update_ui(lambda: self._update_users_list(sputnik_users))
                self.safe_update_ui(lambda: self.loading_label.config(
                    text=f'✅ Загружено {len(sputnik_users)} пользователей',
                    fg='green'
                ))
                self.safe_update_ui(lambda: self.cancel_button.pack_forget())
                
                # Показываем кнопку "Загрузить еще" если загрузили мало
                if len(sputnik_users) >= 45:  # Показываем если загрузили близко к лимиту
                    self.safe_update_ui(lambda: self.load_more_button.pack(anchor='center'))
                
            except Exception as e:
                # Если не удалось загрузить через API, создаем заглушку
                if not self.loading_cancelled:
                    self.safe_update_ui(lambda: self._create_fallback_users())
                    self.safe_update_ui(lambda: self.loading_label.config(
                        text=f'⚠️ Используются примеры (API недоступен)',
                        fg='orange'
                    ))
                    self.safe_update_ui(lambda: self.cancel_button.pack_forget())
        
        # Запускаем загрузку в отдельном потоке
        self.loading_thread = threading.Thread(target=load_worker, daemon=True)
        self.loading_thread.start()
    
    def load_more_users(self):
        """Загрузка дополнительных пользователей (до 500)"""
        self.load_more_button.config(state='disabled', text='🔄 Загрузка...')
        
        def load_more_worker():
            try:
                self.safe_update_ui(lambda: self.loading_label.config(
                    text='📋 Загрузка дополнительных пользователей...',
                    fg='blue'
                ))
                
                # Создаем Directory API сервис
                from googleapiclient.discovery import build
                credentials = self.calendar_manager.calendar_api.credentials
                directory_service = build('admin', 'directory_v1', credentials=credentials)
                
                # Загружаем больше пользователей
                users_result = directory_service.users().list(
                    domain='sputnik8.com',
                    maxResults=500,  # Полная загрузка
                    orderBy='givenName'
                ).execute()
                
                users = users_result.get('users', [])
                
                # Обрабатываем пользователей
                sputnik_users = []
                for user in users:
                    email = user.get('primaryEmail', '')
                    if '@sputnik8.com' in email:
                        full_name = user.get('name', {}).get('fullName', email.split('@')[0])
                        suspended = user.get('suspended', False)
                        
                        sputnik_users.append({
                            'email': email,
                            'name': full_name,
                            'suspended': suspended,
                            'status': 'Заблокирован' if suspended else 'Активен'
                        })
                
                # Сортируем по имени
                sputnik_users.sort(key=lambda x: x['name'])
                
                # Обновляем кэш
                self.users_cache = sputnik_users
                
                # Обновляем UI
                self.safe_update_ui(lambda: self._update_users_list(sputnik_users))
                self.safe_update_ui(lambda: self.loading_label.config(
                    text=f'✅ Загружено {len(sputnik_users)} пользователей (полный список)',
                    fg='green'
                ))
                self.safe_update_ui(lambda: self.load_more_button.pack_forget())
                
            except Exception as e:
                self.safe_update_ui(lambda: self.loading_label.config(
                    text=f'❌ Ошибка расширенной загрузки: {str(e)[:50]}...',
                    fg='red'
                ))
                self.safe_update_ui(lambda: self.load_more_button.config(
                    state='normal', 
                    text='📥 Попробовать еще раз'
                ))
        
        # Запускаем в отдельном потоке
        threading.Thread(target=load_more_worker, daemon=True).start()
    
    def _create_fallback_users(self):
        """Создание примеров пользователей для демонстрации"""
        fallback_users = [
            {'email': 'andrei.shushkov@sputnik8.com', 'name': 'Андрей Шушков', 'suspended': False, 'status': 'Активен'},
            {'email': 'valerii.sergeev@sputnik8.com', 'name': 'Валерий Сергеев', 'suspended': False, 'status': 'Активен'},
            {'email': 'alice.grigoreva@sputnik8.com', 'name': 'Алиса Григорьева', 'suspended': False, 'status': 'Активен'},
            {'email': 'igor.petrov@sputnik8.com', 'name': 'Игорь Петров', 'suspended': False, 'status': 'Активен'},
            {'email': 'margarita.titova@sputnik8.com', 'name': 'Маргарита Титова', 'suspended': False, 'status': 'Активен'},
            {'email': 'evgeniia.matveeva@sputnik8.com', 'name': 'Евгения Матвеева', 'suspended': False, 'status': 'Активен'},
            {'email': 'example.user@sputnik8.com', 'name': 'Новый Сотрудник', 'suspended': False, 'status': 'Активен'},
        ]
        self._update_users_list(fallback_users)
    
    def _update_users_list(self, users):
        """Обновление списка пользователей"""
        self.domain_users = users
        self.filtered_users = users.copy()
        self._populate_users_tree()
    
    def _populate_users_tree(self):
        """Заполнение дерева пользователей"""
        # Очищаем дерево
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Получаем список участников календаря для проверки дублирования
        existing_members = []
        try:
            members = self.calendar_manager.get_members()
            existing_members = [m.email.lower() for m in members]
        except:
            pass
        
        # Добавляем пользователей
        for user in self.filtered_users:
            status = user['status']
            if user['email'].lower() in existing_members:
                status = 'Уже в календаре'
            
            # Добавляем пользователя в список
            item_id = self.users_tree.insert('', 'end', values=(
                user['name'],
                user['email'],
                status
            ))
            
            # Выделяем пользователей, которые уже в календаре
            if status == 'Уже в календаре':
                self.users_tree.set(item_id, 'name', f"🔗 {user['name']}")
    
    def filter_users(self, *args):
        """Фильтрация пользователей по поиску"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            self.filtered_users = self.domain_users.copy()
        else:
            self.filtered_users = []
            for user in self.domain_users:
                if (search_text in user['name'].lower() or 
                    search_text in user['email'].lower()):
                    self.filtered_users.append(user)
        
        # Обновляем отображение
        self._populate_users_tree()
    
    def on_user_select(self, event):
        """Обработка выбора пользователя"""
        selection = self.users_tree.selection()
        if not selection:
            self.selected_label.config(text='Выберите сотрудника из списка')
            self.add_button.config(state='disabled')
            return
        
        item = self.users_tree.item(selection[0])
        values = item.get('values', [])
        if not values:
            return
        
        name, email, status = values
        
        # Отображаем информацию о выбранном пользователе
        role_text = {
            'reader': 'Читатель (просмотр событий)',
            'writer': 'Редактор (создание и изменение событий)',
            'owner': 'Владелец (полный доступ)'
        }.get(self.role_var.get(), 'Неизвестная роль')
        
        info_text = f"👤 {name}\\n📧 {email}\\n🔐 Роль: {role_text}"
        
        # Проверяем, не добавлен ли уже пользователь
        if status == 'Уже в календаре':
            info_text += "\\n⚠️ Пользователь уже добавлен в календарь"
            self.add_button.config(state='disabled')
        else:
            self.add_button.config(state='normal')
        
        self.selected_label.config(text=info_text)
    
    def on_user_double_click(self, event):
        """Обработка двойного клика по пользователю"""
        if self.add_button['state'] == 'normal':
            self.add_member()
    
    def add_member(self):
        """Добавление выбранного участника к календарю"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для добавления")
            return
        
        item = self.users_tree.item(selection[0])
        values = item.get('values', [])
        if not values:
            return
        
        name, email, status = values
        role = self.role_var.get()
        
        # Подтверждение добавления
        role_names = {
            'reader': 'Читатель (просмотр)',
            'writer': 'Редактор (создание/изменение)',
            'owner': 'Владелец (полный доступ)'
        }
        
        result = messagebox.askyesno(
            "Подтверждение",
            f"Добавить пользователя к календарю SPUTНIK?\\n\\n"
            f"👤 Имя: {name}\\n"
            f"📧 Email: {email}\\n"
            f"🔐 Права: {role_names.get(role, role)}"
        )
        
        if not result:
            return
        
        def add_worker():
            try:
                # Добавляем участника
                self.calendar_manager.add_member(email, role)
                
                # Обновляем UI в главном потоке
                self.safe_update_ui(lambda: messagebox.showinfo(
                    "Успех", 
                    f"Пользователь {name} успешно добавлен к календарю SPUTНIK"
                ))
                self.safe_update_ui(self.refresh_callback)
                self.safe_update_ui(self.destroy)
                
            except Exception as e:
                self.safe_update_ui(lambda: messagebox.showerror(
                    "Ошибка",
                    f"Ошибка добавления пользователя {name}:\\n\\n{str(e)}"
                ))
        
        threading.Thread(target=add_worker, daemon=True).start()


def open_sputnik_calendar_window(master=None):
    """
    Открытие окна управления календарем SPUTНIK
    
    Args:
        master: Родительское окно
    """
    try:
        window = SputnikCalendarWindow(master)
        window.protocol("WM_DELETE_WINDOW", window.destroy)
        return window
    except Exception as e:
        messagebox.showerror(
            "Ошибка",
            f"Не удалось открыть окно календаря SPUTНIK:\\n{str(e)}"
        )
        return None
