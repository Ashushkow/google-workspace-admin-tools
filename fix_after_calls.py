#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для замены небезопасных вызовов self.after на безопасные self.safe_update_ui
"""

import re

def fix_after_calls():
    file_path = 'src/ui/sputnik_calendar_ui.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем все вхождения self.after(0, lambda: на self.safe_update_ui(lambda:
        content = re.sub(r'self\.after\(0,\s*lambda:', 'self.safe_update_ui(lambda:', content)
        
        # Также заменяем self.after(0, self.method) на self.safe_update_ui(self.method)
        content = re.sub(r'self\.after\(0,\s*(self\.\w+)\)', r'self.safe_update_ui(\1)', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print('✅ Замена выполнена успешно')
        
    except Exception as e:
        print(f'❌ Ошибка: {e}')

if __name__ == '__main__':
    fix_after_calls()
