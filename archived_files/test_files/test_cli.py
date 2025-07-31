#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой CLI тест для FreeIPA
"""

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.cli.freeipa_simple import freeipa
    
    if __name__ == '__main__':
        freeipa()
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)
