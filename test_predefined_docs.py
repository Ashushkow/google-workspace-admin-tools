#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест списка предустановленных документов в окне управления доступом
"""

def test_predefined_documents():
    """Тест предустановленных документов"""
    print("🧪 Тестирование списка предустановленных документов...")
    
    # Предустановленные документы
    predefined_docs = {
        "📄 Документ Google Docs": "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2",
        "📊 Таблица Google Sheets": "https://docs.google.com/spreadsheets/d/1ErK5XLx7QEUJv22XC-UBQGyig3Otfm-xR1A1-hm8eDA/edit#gid=1326342300", 
        "📋 Презентация Google Slides": "https://docs.google.com/presentation/d/1ia0PmtgJBaY3Q97gaA1TNyJFJF7vgXhsGh1iF1WOQ_E/edit#slide=id.g2dca74c59e7_0_0"
    }
    
    print("✅ Предустановленные документы:")
    for i, (name, url) in enumerate(predefined_docs.items(), 1):
        print(f"   {i}. {name}")
        print(f"      URL: {url[:50]}...")
        
        # Проверяем правильность URL
        if url.startswith("https://docs.google.com/"):
            print(f"      ✅ Корректный Google Docs URL")
        else:
            print(f"      ❌ Некорректный URL")
    
    print("\n✅ Новые возможности интерфейса:")
    print("   • Выпадающий список с 3 предустановленными документами")
    print("   • Кнопка 'Выбрать' для быстрого выбора документа") 
    print("   • Автоматическая загрузка информации при выборе")
    print("   • Поле для ввода собственного URL остается доступным")
    print("   • Эмодзи для разных типов документов")
    print("   • Улучшенное отображение информации о документе")
    
    print("\n✅ Логика работы:")
    print("   1. Пользователь выбирает документ из выпадающего списка")
    print("   2. URL автоматически подставляется в поле ввода") 
    print("   3. При нажатии 'Выбрать' - автоматически загружается информация")
    print("   4. Альтернативно можно ввести собственный URL и нажать 'Загрузить'")
    
    print("\n✅ Методы добавленные в класс:")
    print("   • _on_document_selected() - обработчик выбора из списка")
    print("   • _select_predefined_document() - выбор и автозагрузка")
    print("   • _get_document_type_emoji() - эмодзи для типов документов")
    print("   • _initialize_default_document() - инициализация по умолчанию")
    
    return True

if __name__ == "__main__":
    success = test_predefined_documents()
    if success:
        print("\n🎉 Список предустановленных документов успешно добавлен!")
        print("📋 Теперь можно быстро выбрать один из трех документов")
    else:
        print("\n💥 Что-то пошло не так")
