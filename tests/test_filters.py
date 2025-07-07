# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки логики фильтрации
"""

def test_filter_logic():
    """Тестируем логику фильтрации"""
    # Тестовые данные
    employees = [
        {'email': 'test1@example.com', 'name': 'Иван Иванов', 'status': 'Active', 'orgunit': '/IT', 'created': '2023-01-15'},
        {'email': 'test2@example.com', 'name': 'Мария Петрова', 'status': 'Suspended', 'orgunit': '/HR', 'created': '2023-02-20'},
        {'email': 'test3@example.com', 'name': 'Петр Сидоров', 'status': 'Active', 'orgunit': '/IT', 'created': '2023-03-10'},
        {'email': 'admin@example.com', 'name': 'Админ Админов', 'status': 'Active', 'orgunit': '/', 'created': '2022-12-01'},
    ]
    
    print("Тестовые данные:")
    for emp in employees:
        print(f"  {emp}")
    
    # Тест 1: Поиск по email
    print("\n=== Тест 1: Поиск по email 'test1' ===")
    query = 'test1'
    filtered = []
    for emp in employees:
        emp_email = emp.get('email', '').lower()
        emp_name = emp.get('name', '').lower()
        if query not in emp_email and query not in emp_name:
            continue
        filtered.append(emp)
    print(f"Результат: {len(filtered)} записей")
    for emp in filtered:
        print(f"  {emp}")
    
    # Тест 2: Фильтр по статусу
    print("\n=== Тест 2: Фильтр по статусу 'Active' ===")
    status = 'Active'
    filtered = []
    for emp in employees:
        if status != "Все" and emp.get('status', '') != status:
            continue
        filtered.append(emp)
    print(f"Результат: {len(filtered)} записей")
    for emp in filtered:
        print(f"  {emp}")
    
    # Тест 3: Фильтр по подразделению
    print("\n=== Тест 3: Фильтр по подразделению '/IT' ===")
    orgunit = '/IT'
    filtered = []
    for emp in employees:
        if orgunit != "Все" and emp.get('orgunit', '') != orgunit:
            continue
        filtered.append(emp)
    print(f"Результат: {len(filtered)} записей")
    for emp in filtered:
        print(f"  {emp}")
    
    # Тест 4: Комбинированный фильтр
    print("\n=== Тест 4: Комбинированный фильтр (Active + /IT) ===")
    status = 'Active'
    orgunit = '/IT'
    filtered = []
    for emp in employees:
        if status != "Все" and emp.get('status', '') != status:
            continue
        if orgunit != "Все" and emp.get('orgunit', '') != orgunit:
            continue
        filtered.append(emp)
    print(f"Результат: {len(filtered)} записей")
    for emp in filtered:
        print(f"  {emp}")

if __name__ == '__main__':
    test_filter_logic()
