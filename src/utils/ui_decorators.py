"""
Декоратор для централизованной обработки ошибок UI
"""
from functools import wraps
from tkinter import messagebox
from typing import Callable, Any

def handle_ui_errors(operation_name: str):
    """Декоратор для обработки ошибок UI операций"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            if not self.service:
                messagebox.showwarning('Предупреждение', 'Нет подключения к Google API')
                return None
                
            try:
                result = func(self, *args, **kwargs)
                self.log_activity(f'{operation_name} выполнено успешно')
                return result
            except Exception as e:
                error_msg = f'Ошибка {operation_name.lower()}: {str(e)}'
                self.log_activity(error_msg, 'ERROR')
                messagebox.showerror('Ошибка', f'Не удалось {operation_name.lower()}: {str(e)}')
                return None
        return wrapper
    return decorator

# Использование:
@handle_ui_errors("открытие окна сотрудников")
def open_employee_list(self) -> None:
    window = EmployeeListWindow(self, self.service)
