# -*- coding: utf-8 -*-
"""
Централизованное хранилище иконок для UI компонентов.
Использует современные эмодзи для лучшего визуального представления.
"""

# Основные разделы приложения
MAIN_SECTIONS = {
    "employees": "👥",        # Сотрудники
    "groups": "🏢",           # Группы (корпоративная иконка)
    "calendars": "📅",        # Календари
    "documents": "📄",        # Документы
    "sputnik": "🛰️",         # SPUTNIK - спутник (идеально подходит!)
}

# Основные действия
ACTIONS = {
    "create": "➕",           # Создать
    "edit": "✏️",            # Редактировать
    "delete": "🗑️",         # Удалить
    "save": "💾",            # Сохранить
    "cancel": "❌",          # Отмена
    "close": "❌",           # Закрыть
    "refresh": "🔄",         # Обновить
    "search": "🔍",          # Поиск
    "settings": "⚙️",        # Настройки
    "export": "📤",          # Экспорт
    "import": "📥",          # Импорт
    "add": "➕",             # Добавить
    "remove": "➖",          # Убрать
    "copy": "📋",            # Копировать
    "move": "📤",            # Переместить
    "send": "📤",            # Отправить
    "generate": "🔑",        # Сгенерировать (например, пароль)
    "clean": "🧹",           # Очистить
}

# Статусы и состояния
STATUS = {
    "active": "✅",          # Активен
    "inactive": "❌",        # Неактивен
    "blocked": "🔒",         # Заблокирован
    "waiting": "⏳",         # Ожидание
    "loading": "🔄",         # Загрузка
    "error": "⚠️",          # Ошибка
    "warning": "⚠️",         # Предупреждение
    "success": "✅",         # Успех
    "info": "ℹ️",           # Информация
}

# Меню и навигация
MENU = {
    "file": "📁",            # Файл
    "view": "👁️",           # Вид
    "help": "❓",            # Справка
    "theme": "🎨",           # Тема
    "light_theme": "☀️",     # Светлая тема
    "dark_theme": "🌙",      # Тёмная тема
    "blue_theme": "🌊",      # Синяя тема
    "hotkeys": "⌨️",        # Горячие клавиши
    "about": "ℹ️",          # О программе
}

# Технические иконки
TECH = {
    "api": "🔌",             # API
    "database": "🗄️",       # База данных
    "network": "🌐",         # Сеть
    "security": "🛡️",       # Безопасность
    "logs": "📊",            # Логи
    "config": "⚙️",         # Конфигурация
    "oauth": "🔐",           # OAuth авторизация
    "service_account": "🤖", # Service Account
}

# Пользователи и роли
USERS = {
    "user": "👤",            # Пользователь
    "users": "👥",           # Пользователи
    "admin": "👑",           # Администратор
    "owner": "🏆",           # Владелец
    "member": "👤",          # Участник
    "guest": "👻",           # Гость
}

# Календарь и время
CALENDAR = {
    "calendar": "📅",        # Календарь
    "event": "📅",           # Событие
    "date": "📆",            # Дата
    "time": "🕐",            # Время
    "schedule": "🗓️",       # Расписание
}

# Документы и файлы
DOCUMENTS = {
    "document": "📄",        # Документ
    "folder": "📁",          # Папка
    "file": "📄",            # Файл
    "pdf": "📄",             # PDF
    "excel": "📊",           # Excel
    "word": "📄",            # Word
    "presentation": "📊",    # Презентация
}

# Утилиты для получения иконок
def get_action_icon(action: str) -> str:
    """Получить иконку для действия"""
    return ACTIONS.get(action, "")

def get_status_icon(status: str) -> str:
    """Получить иконку для статуса"""
    return STATUS.get(status, "")

def get_section_icon(section: str) -> str:
    """Получить иконку для раздела"""
    return MAIN_SECTIONS.get(section, "")

def get_menu_icon(menu_item: str) -> str:
    """Получить иконку для пункта меню"""
    return MENU.get(menu_item, "")

# Готовые комбинации для часто используемых элементов
READY_LABELS = {
    # Кнопки
    "create_user": f"{ACTIONS['create']} Создать",
    "edit_user": f"{ACTIONS['edit']} Редактировать", 
    "delete_user": f"{ACTIONS['delete']} Удалить",
    "save_changes": f"{ACTIONS['save']} Сохранить изменения",
    "cancel": f"{ACTIONS['cancel']} Отмена",
    "close": f"{ACTIONS['close']} Закрыть",
    "refresh": f"{ACTIONS['refresh']} Обновить",
    "export": f"{ACTIONS['export']} Экспорт",
    "add_member": f"{ACTIONS['add']} Добавить участника",
    "send_invite": f"{ACTIONS['send']} Отправить приглашение",
    "generate_password": f"{ACTIONS['generate']} Сгенерировать",
    "clean_logs": f"{ACTIONS['clean']} Очистить",
    
    # Разделы меню
    "employees_section": f"{MAIN_SECTIONS['employees']} Сотрудники",
    "groups_section": f"{MAIN_SECTIONS['groups']} Группы",
    "calendars_section": f"{MAIN_SECTIONS['calendars']} Календари",
    "documents_section": f"{MAIN_SECTIONS['documents']} Документы",
    "sputnik_section": f"{MAIN_SECTIONS['sputnik']} SPUTNIK",
    
    # Пункты меню
    "file_menu": f"{MENU['file']} Файл",
    "view_menu": f"{MENU['view']} Вид",
    "help_menu": f"{MENU['help']} Справка",
    "light_theme": f"{MENU['light_theme']} Светлая",
    "dark_theme": f"{MENU['dark_theme']} Тёмная",
    "blue_theme": f"{MENU['blue_theme']} Синяя",
}
