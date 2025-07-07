# -*- coding: utf-8 -*-
"""
Система уведомлений и мониторинга для отслеживания состояния приложения.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional
from enum import Enum
import psutil
import requests


class NotificationType(Enum):
    """Типы уведомлений"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SystemMonitor:
    """
    Мониторинг системных ресурсов и состояния API.
    """
    
    def __init__(self):
        self.monitoring = False
        self.callbacks: List[Callable] = []
        self.last_check = datetime.now()
        
    def start_monitoring(self):
        """Запускает мониторинг в отдельном потоке"""
        self.monitoring = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()
    
    def stop_monitoring(self):
        """Останавливает мониторинг"""
        self.monitoring = False
    
    def add_callback(self, callback: Callable):
        """Добавляет callback для уведомлений о проблемах"""
        self.callbacks.append(callback)
    
    def _monitor_loop(self):
        """Основной цикл мониторинга"""
        while self.monitoring:
            try:
                self._check_system_resources()
                self._check_api_connectivity()
                time.sleep(30)  # Проверка каждые 30 секунд
            except Exception as e:
                self._notify_callbacks(f"Ошибка мониторинга: {e}", NotificationType.ERROR)
    
    def _check_system_resources(self):
        """Проверяет системные ресурсы"""
        try:
            # Проверка использования памяти
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self._notify_callbacks(
                    f"Высокое использование памяти: {memory.percent:.1f}%", 
                    NotificationType.WARNING
                )
            
            # Проверка использования диска (адаптировано для Windows)
            import os
            if os.name == 'nt':  # Windows
                disk = psutil.disk_usage('C:')
            else:  # Unix/Linux
                disk = psutil.disk_usage('/')
                
            if disk.percent > 90:
                self._notify_callbacks(
                    f"Мало места на диске: {disk.percent:.1f}%", 
                    NotificationType.WARNING
                )
        except Exception as e:
            # Не критично, просто пропускаем проверку ресурсов
            pass
    
    def _check_api_connectivity(self):
        """Проверяет доступность Google API"""
        try:
            response = requests.get(
                "https://www.googleapis.com/admin/directory/v1/", 
                timeout=10
            )
            if response.status_code != 200:
                self._notify_callbacks(
                    "Проблемы с доступностью Google API", 
                    NotificationType.WARNING
                )
        except requests.RequestException:
            self._notify_callbacks(
                "Нет соединения с Google API", 
                NotificationType.ERROR
            )
    
    def _notify_callbacks(self, message: str, notification_type: NotificationType):
        """Уведомляет все зарегистрированные callbacks"""
        for callback in self.callbacks:
            try:
                callback(message, notification_type)
            except Exception as e:
                print(f"Ошибка в callback мониторинга: {e}")


class NotificationCenter:
    """
    Центр уведомлений для отображения всплывающих сообщений.
    """
    
    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.notifications: List[Dict] = []
        self.notification_widgets: List[tk.Toplevel] = []
        
    def show_notification(self, message: str, notification_type: NotificationType, 
                         duration: int = 5000):
        """
        Показывает всплывающее уведомление.
        
        Args:
            message: Текст уведомления
            notification_type: Тип уведомления
            duration: Длительность показа в миллисекундах
        """
        # Создаем всплывающее окно
        notification = tk.Toplevel(self.parent)
        notification.title("")
        notification.geometry("300x80")
        notification.resizable(False, False)
        notification.overrideredirect(True)  # Убираем декорации окна
        
        # Позиционируем в правом нижнем углу
        x = self.parent.winfo_screenwidth() - 320
        y = self.parent.winfo_screenheight() - 100 - (len(self.notification_widgets) * 90)
        notification.geometry(f"300x80+{x}+{y}")
        
        # Цвета для разных типов уведомлений
        colors = {
            NotificationType.INFO: "#3b82f6",
            NotificationType.SUCCESS: "#10b981",
            NotificationType.WARNING: "#f59e0b",
            NotificationType.ERROR: "#ef4444",
            NotificationType.CRITICAL: "#dc2626"
        }
        
        # Создаем содержимое уведомления
        main_frame = tk.Frame(notification, bg=colors[notification_type], relief='solid', bd=1)
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Заголовок
        title_label = tk.Label(
            main_frame, 
            text=notification_type.value.upper(),
            font=('Arial', 9, 'bold'),
            bg=colors[notification_type],
            fg='white'
        )
        title_label.pack(anchor='w', padx=10, pady=(5, 0))
        
        # Сообщение
        message_label = tk.Label(
            main_frame,
            text=message,
            font=('Arial', 8),
            bg=colors[notification_type],
            fg='white',
            wraplength=280
        )
        message_label.pack(anchor='w', padx=10, pady=(0, 5))
        
        # Кнопка закрытия
        close_btn = tk.Button(
            main_frame,
            text="×",
            font=('Arial', 12, 'bold'),
            bg=colors[notification_type],
            fg='white',
            bd=0,
            command=lambda: self._close_notification(notification)
        )
        close_btn.place(x=275, y=5, width=20, height=20)
        
        # Добавляем в список активных уведомлений
        self.notification_widgets.append(notification)
        
        # Автоматическое закрытие
        self.parent.after(duration, lambda: self._close_notification(notification))
        
        # Анимация появления
        self._animate_notification(notification)
    
    def _animate_notification(self, notification: tk.Toplevel):
        """Анимирует появление уведомления"""
        notification.attributes('-alpha', 0.0)
        for i in range(10):
            alpha = i / 10.0
            notification.attributes('-alpha', alpha)
            notification.update()
            time.sleep(0.02)
    
    def _close_notification(self, notification: tk.Toplevel):
        """Закрывает уведомление"""
        if notification in self.notification_widgets:
            self.notification_widgets.remove(notification)
            try:
                notification.destroy()
            except:
                pass
            
            # Перемещаем остальные уведомления вверх
            self._reposition_notifications()
    
    def _reposition_notifications(self):
        """Перемещает уведомления после закрытия одного из них"""
        for i, notification in enumerate(self.notification_widgets):
            x = self.parent.winfo_screenwidth() - 320
            y = self.parent.winfo_screenheight() - 100 - (i * 90)
            notification.geometry(f"300x80+{x}+{y}")


# Глобальные экземпляры
system_monitor = SystemMonitor()
notification_center = None  # Инициализируется в main_window.py
