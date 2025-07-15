"""
Конфигурация UI для главного окна
"""

class MainWindowConfig:
    """Конфигурация главного окна приложения"""
    
    # Основные параметры окна
    TITLE = 'Admin Team Tools v2.0 - Управление пользователями Google Workspace'
    GEOMETRY = '600x400'
    MIN_WIDTH = 500
    MIN_HEIGHT = 350
    
    # Временные задержки (в миллисекундах)
    DELAYED_INIT_DELAY = 1000
    STATISTICS_LOAD_DELAY = 2000
    RETRY_DELAY = 500
    
    # UI элементы
    HEADER_HEIGHT = 60
    TOOLBAR_HEIGHT = 80
    STATUS_BAR_HEIGHT = 25
    
    # Стили кнопок
    BUTTON_STYLES = {
        'primary': 'primary',
        'secondary': 'secondary', 
        'success': 'success',
        'warning': 'warning',
        'danger': 'danger',
        'info': 'info'
    }
    
    # Сообщения
    MESSAGES = {
        'no_connection': 'Нет подключения к Google API',
        'ready': 'Готов к работе',
        'connected': 'Подключен к Google Workspace API',
        'loading': 'Загрузка данных...',
        'updated': 'Данные обновлены'
    }
    
    # Экспорт
    EXPORT_FORMATS = [
        ('CSV files', '*.csv'),
        ('All files', '*.*')
    ]
