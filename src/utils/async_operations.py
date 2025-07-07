# -*- coding: utf-8 -*-
"""
Асинхронные операции для предотвращения блокировки UI.
"""

import threading
import tkinter as tk
from typing import Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import queue


class AsyncOperationManager:
    """
    Менеджер асинхронных операций для предотвращения блокировки UI.
    """
    
    def __init__(self, max_workers: int = 5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.result_queue = queue.Queue()
        
    def run_async(self, func: Callable, callback: Optional[Callable] = None, 
                  error_callback: Optional[Callable] = None, *args, **kwargs):
        """
        Запускает функцию асинхронно и вызывает callback при завершении.
        
        Args:
            func: Функция для выполнения
            callback: Функция для вызова при успешном выполнении
            error_callback: Функция для вызова при ошибке
            *args, **kwargs: Аргументы для func
        """
        def worker():
            try:
                result = func(*args, **kwargs)
                if callback:
                    # Планируем callback в основном потоке
                    self.result_queue.put(('success', callback, result))
            except Exception as e:
                if error_callback:
                    self.result_queue.put(('error', error_callback, e))
                else:
                    self.result_queue.put(('error', None, e))
        
        self.executor.submit(worker)
    
    def process_results(self, root: tk.Tk):
        """
        Обрабатывает результаты асинхронных операций в основном потоке.
        Нужно вызывать периодически через root.after()
        """
        try:
            while True:
                status, callback, result = self.result_queue.get_nowait()
                if callback:
                    callback(result)
        except queue.Empty:
            pass
        finally:
            # Планируем следующую проверку
            root.after(100, lambda: self.process_results(root))


class ProgressDialog:
    """
    Диалог с индикатором прогресса для длительных операций.
    """
    
    def __init__(self, parent, title: str = "Обработка...", 
                 message: str = "Пожалуйста, подождите..."):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x120")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем диалог
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (120 // 2)
        self.dialog.geometry(f"300x120+{x}+{y}")
        
        # Создаем интерфейс
        tk.Label(self.dialog, text=message, font=('Arial', 10)).pack(pady=20)
        
        # Простой индикатор прогресса (анимированный текст)
        self.progress_label = tk.Label(self.dialog, text="●", font=('Arial', 12))
        self.progress_label.pack()
        
        self.animate_progress()
    
    def animate_progress(self):
        """Анимирует индикатор прогресса"""
        current = self.progress_label.cget("text")
        if current == "●":
            next_text = "●●"
        elif current == "●●":
            next_text = "●●●"
        else:
            next_text = "●"
        
        self.progress_label.config(text=next_text)
        self.dialog.after(500, self.animate_progress)
    
    def close(self):
        """Закрывает диалог"""
        self.dialog.destroy()
