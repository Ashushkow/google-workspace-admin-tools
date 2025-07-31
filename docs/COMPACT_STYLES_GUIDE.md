# Руководство по использованию компактных стилей

## Быстрый старт

### Импорт модуля
```python
from src.ui.modern_styles import (
    ModernWindowConfig, ModernColors, 
    CompactFrame, CompactLabel, CompactEntry, CompactButton,
    apply_modern_window_style, center_window_modern
)
```

### Создание компактного окна
```python
class MyWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Мое окно')
        
        # Применяем современный стиль
        apply_modern_window_style(self, 'create_user')  # или другой тип
        
        self.create_ui()
        
        # Центрируем окно
        center_window_modern(self, parent)
    
    def create_ui(self):
        # Заголовок
        title_frame = create_title_section(self, 'Заголовок окна')
        title_frame.pack(fill='x', **ModernWindowConfig.PADDING['window'])
        
        # Основной контейнер
        main_frame = CompactFrame(self, padding_type='section')
        main_frame.pack(fill='both', expand=True, **ModernWindowConfig.PADDING['window'])
        
        # Компактные элементы
        CompactLabel(main_frame, text='Метка:', font_type='subtitle').pack()
        entry = CompactEntry(main_frame, width_type='entry_small')
        entry.pack(pady=5)
        
        # Кнопки
        CompactButton(main_frame, text='OK', style='primary').pack(side='left', padx=5)
        CompactButton(main_frame, text='Отмена', style='secondary').pack(side='right', padx=5)
```

## Доступные компоненты

### 1. CompactFrame
Современный фрейм с автоматическими отступами
```python
frame = CompactFrame(parent, padding_type='section')  # 'window', 'section', 'field', 'button', 'small'
```

### 2. CompactLabel
Компактная метка с настраиваемыми шрифтами
```python
label = CompactLabel(parent, text='Текст', font_type='title')  # 'title', 'subtitle', 'label', 'small'
```

### 3. CompactEntry
Поле ввода с современным стилем
```python
entry = CompactEntry(parent, width_type='entry_width')  # 'entry_width', 'entry_small'
```

### 4. CompactButton
Современная кнопка с цветовыми схемами
```python
button = CompactButton(parent, text='Кнопка', style='primary', width_type='button_width')
# Стили: 'primary', 'success', 'danger', 'warning', 'info', 'secondary'
# Размеры: 'button_width', 'button_small'
```

### 5. CompactListbox
Компактный список
```python
listbox = CompactListbox(parent, height_type='listbox_height')
```

### 6. CompactScrolledText
Текстовое поле с прокруткой
```python
text = CompactScrolledText(parent, width=60, height_type='text_height')
text.pack(side='left', fill='both', expand=True)
text.scrollbar.pack(side='right', fill='y')
```

### 7. ButtonRow
Автоматическое размещение кнопок в несколько рядов
```python
button_configs = [
    {'text': 'Кнопка 1', 'command': func1, 'style': 'primary'},
    {'text': 'Кнопка 2', 'command': func2, 'style': 'secondary'},
    # ... до 8 кнопок
]
buttons = ButtonRow(parent, button_configs, max_per_row=4)
buttons.pack(fill='x', pady=10)
```

## Конфигурация размеров

### Размеры окон
```python
WINDOW_SIZES = {
    'create_user': '580x520',
    'edit_user': '880x580', 
    'group_management': '900x650',
    'asana_invite': '380x240',
    'error_log': '720x480',
    # ... и другие
}
```

### Отступы
```python
PADDING = {
    'window': {'padx': 15, 'pady': 12},
    'section': {'padx': 10, 'pady': 8},
    'field': {'padx': 8, 'pady': 6},
    'button': {'padx': 12, 'pady': 4},
    'small': {'padx': 5, 'pady': 3}
}
```

### Шрифты
```python
FONTS = {
    'title': ('Segoe UI', 14, 'bold'),
    'subtitle': ('Segoe UI', 11, 'bold'),
    'label': ('Segoe UI', 9),
    'entry': ('Segoe UI', 9),
    'button': ('Segoe UI', 9),
    'small': ('Segoe UI', 8)
}
```

## Цветовая схема (Material Design)

```python
ModernColors.PRIMARY = "#2563eb"      # Основной синий
ModernColors.SUCCESS = "#10b981"      # Зеленый успех
ModernColors.WARNING = "#f59e0b"      # Оранжевое предупреждение
ModernColors.DANGER = "#ef4444"       # Красная опасность
ModernColors.INFO = "#0ea5e9"         # Информационный голубой
ModernColors.SECONDARY = "#374151"    # Серый второстепенный
ModernColors.BACKGROUND = "#f8fafc"   # Светлый фон
ModernColors.TEXT_PRIMARY = "#1f2937" # Основной текст
```

## Примеры использования

### Простое окно с формой
```python
def create_simple_form(parent):
    window = tk.Toplevel(parent)
    apply_modern_window_style(window, 'create_user')
    
    # Заголовок
    title_frame = create_title_section(window, 'Простая форма')
    title_frame.pack(fill='x', **ModernWindowConfig.PADDING['window'])
    
    # Форма
    form_frame = CompactFrame(window, padding_type='section')
    form_frame.pack(fill='both', expand=True, **ModernWindowConfig.PADDING['window'])
    
    # Поля
    CompactLabel(form_frame, text='Имя:').grid(row=0, column=0, sticky='e', **ModernWindowConfig.PADDING['field'])
    name_entry = CompactEntry(form_frame, width_type='entry_small')
    name_entry.grid(row=0, column=1, **ModernWindowConfig.PADDING['field'])
    
    CompactLabel(form_frame, text='Email:').grid(row=1, column=0, sticky='e', **ModernWindowConfig.PADDING['field'])
    email_entry = CompactEntry(form_frame, width_type='entry_small')
    email_entry.grid(row=1, column=1, **ModernWindowConfig.PADDING['field'])
    
    # Кнопки
    buttons_frame = CompactFrame(form_frame, padding_type='small')
    buttons_frame.grid(row=2, column=0, columnspan=2, **ModernWindowConfig.PADDING['button'])
    
    CompactButton(buttons_frame, text='Сохранить', style='success').pack(side='left', padx=5)
    CompactButton(buttons_frame, text='Отмена', style='secondary').pack(side='right', padx=5)
    
    center_window_modern(window, parent)
```

### Окно со списком и кнопками
```python
def create_list_window(parent):
    window = tk.Toplevel(parent)
    apply_modern_window_style(window, 'group_management')
    
    # Заголовок
    title_frame = create_title_section(window, 'Список элементов')
    title_frame.pack(fill='x', **ModernWindowConfig.PADDING['window'])
    
    # Основной контейнер
    main_frame = CompactFrame(window, padding_type='section')
    main_frame.pack(fill='both', expand=True, **ModernWindowConfig.PADDING['window'])
    
    # Кнопки управления в два ряда
    button_configs = [
        {'text': '➕ Добавить', 'style': 'primary'},
        {'text': '✏️ Изменить', 'style': 'secondary'},
        {'text': '🗑️ Удалить', 'style': 'danger'},
        {'text': '🔄 Обновить', 'style': 'info'}
    ]
    
    buttons = ButtonRow(main_frame, button_configs, max_per_row=2)
    buttons.pack(fill='x', pady=(0, 10))
    
    # Список
    listbox = CompactListbox(main_frame, height_type='listbox_height')
    listbox.pack(fill='both', expand=True, pady=(0, 10))
    
    # Кнопка закрытия
    CompactButton(main_frame, text='Закрыть', style='secondary').pack(pady=5)
    
    center_window_modern(window, parent)
```

## Миграция с старых стилей

### Замена обычных компонентов
```python
# Было:
tk.Label(parent, text='Текст', font=('Arial', 11))
tk.Entry(parent, width=40, font=('Arial', 11))
tk.Button(parent, text='Кнопка', font=('Arial', 11))

# Стало:
CompactLabel(parent, text='Текст', font_type='label')
CompactEntry(parent, width_type='entry_width')
CompactButton(parent, text='Кнопка', style='primary')
```

### Замена размеров окон
```python
# Было:
self.geometry('800x600')

# Стало:
apply_modern_window_style(self, 'group_management')  # автоматически установит '900x650'
```

### Замена отступов
```python
# Было:
frame.pack(padx=20, pady=15)

# Стало:
frame.pack(**ModernWindowConfig.PADDING['window'])  # padx=15, pady=12
```

## Советы по использованию

1. **Выбор типа окна**: Используйте подходящий тип из `WINDOW_SIZES` для автоматической настройки размера
2. **Единообразие**: Применяйте одинаковые отступы через `ModernWindowConfig.PADDING`
3. **Цветовое кодирование**: Используйте разные стили кнопок для разных действий (success для сохранения, danger для удаления)
4. **Компактность**: Размещайте кнопки в несколько рядов с помощью `ButtonRow`
5. **Читаемость**: Используйте подходящие размеры шрифтов из `ModernWindowConfig.FONTS`
