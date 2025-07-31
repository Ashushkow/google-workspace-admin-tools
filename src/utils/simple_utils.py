# -*- coding: utf-8 -*-
"""
Утилиты для улучшения стабильности и удобства работы.
Объединяет только самые необходимые функции.
"""

import asyncio
import threading
import time
import functools
from typing import Callable, Any, Optional
from datetime import datetime
from googleapiclient.errors import HttpError
from tkinter import messagebox
import tkinter as tk
import logging

logger = logging.getLogger(__name__)


class SimpleAsyncManager:
    """Простой менеджер для выполнения async функций из tkinter"""
    
    def __init__(self):
        self.results = []
    
    def run_async(self, coro_func: Callable, callback: Optional[Callable] = None, 
                  error_callback: Optional[Callable] = None, *args, **kwargs):
        """Запускает корутину в отдельном потоке с event loop"""
        def worker():
            try:
                # Создаем новый event loop для потока
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Если функция - это корутина-функция, вызываем её
                    if asyncio.iscoroutinefunction(coro_func):
                        result = loop.run_until_complete(coro_func(*args, **kwargs))
                    else:
                        # Если это обычная функция, просто вызываем
                        result = coro_func(*args, **kwargs)
                    
                    if callback:
                        callback(result)
                        
                except Exception as e:
                    logger.error(f"Ошибка в async операции: {e}")
                    if error_callback:
                        error_callback(e)
                    else:
                        print(f"Ошибка в async операции: {e}")
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.error(f"Критическая ошибка async менеджера: {e}")
                if error_callback:
                    error_callback(e)
                else:
                    print(f"Ошибка в async операции: {e}")
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
    def run_sync_in_thread(self, func: Callable, callback: Optional[Callable] = None, 
                          error_callback: Optional[Callable] = None, *args, **kwargs):
        """Запускает обычную функцию в отдельном потоке (совместимость)"""
        def worker():
            try:
                result = func(*args, **kwargs)
                if callback:
                    callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)
                else:
                    print(f"Ошибка в sync операции: {e}")
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()


class SimpleErrorHandler:
    """Простая обработка ошибок Google API с автоповтором"""
    
    @staticmethod
    def handle_api_error(error: HttpError, context: str = "") -> str:
        """Возвращает понятное сообщение об ошибке API"""
        if hasattr(error, 'resp') and error.resp:
            status_code = error.resp.status
            
            if status_code == 403:
                return "Недостаточно прав для выполнения операции"
            elif status_code == 404:
                return "Запрашиваемый ресурс не найден"
            elif status_code == 429:
                return "Превышен лимит запросов. Попробуйте через минуту"
            elif status_code >= 500:
                return "Ошибка сервера Google. Попробуйте позже"
            else:
                return f"Ошибка API (код {status_code})"
        else:
            return "Ошибка соединения с Google API"
    
    @staticmethod
    def with_retry(max_retries: int = 2, delay: float = 1.0):
        """Декоратор для автоматического повтора при ошибках"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries:
                            raise
                        print(f"Попытка {attempt + 1} неудачна, повтор через {delay}с...")
                        time.sleep(delay)
                return None
            return wrapper
        return decorator


class SimpleProgressDialog:
    """Простой диалог прогресса для длительных операций"""
    
    def __init__(self, parent, title: str = "Обработка..."):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("250x80")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (125)
        y = (self.dialog.winfo_screenheight() // 2) - (40)
        self.dialog.geometry(f"250x80+{x}+{y}")
        
        tk.Label(self.dialog, text="Пожалуйста, подождите...", 
                font=('Arial', 10)).pack(pady=20)
        
        self.progress_text = tk.Label(self.dialog, text="●", font=('Arial', 12))
        self.progress_text.pack()
        
        self._animate()
    
    def _animate(self):
        """Простая анимация"""
        current = self.progress_text.cget("text")
        if current == "●":
            next_text = "●●"
        elif current == "●●":
            next_text = "●●●"
        else:
            next_text = "●"
        
        self.progress_text.config(text=next_text)
        self.dialog.after(500, self._animate)
    
    def close(self):
        """Закрывает диалог"""
        try:
            self.dialog.destroy()
        except:
            pass


def show_api_error(parent, error: Exception, context: str = ""):
    """Показывает пользователю понятное сообщение об ошибке"""
    if isinstance(error, HttpError):
        message = SimpleErrorHandler.handle_api_error(error, context)
    else:
        message = f"Произошла ошибка: {str(error)}"
    
    messagebox.showerror("Ошибка", message, parent=parent)


# Глобальные экземпляры для простоты использования
async_manager = SimpleAsyncManager()
error_handler = SimpleErrorHandler()
