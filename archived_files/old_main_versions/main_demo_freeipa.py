#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый запуск приложения с demo данными для тестирования FreeIPA
"""

import sys
import asyncio
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def patch_service_adapter_for_demo():
    """Патчим ServiceAdapter для использования только demo данных"""
    from src.api.service_adapter import ServiceAdapter
    
    # Переопределяем _ensure_data_loaded для использования только demo данных
    def demo_ensure_data_loaded(self):
        """Принудительно использует demo данные"""
        if not hasattr(self, '_data_loaded') or not self._data_loaded:
            print("🧪 Принудительное использование demo данных для тестирования...")
            self._demo_fallback_mode = True
            self._initialize_demo_data()
            self._data_loaded = True
            print(f"✅ Demo данные загружены: {len(self._users)} пользователей, {len(self._groups)} групп")
    
    # Заменяем метод
    ServiceAdapter._ensure_data_loaded = demo_ensure_data_loaded

async def main():
    """Запуск приложения с demo данными"""
    print("=" * 70)
    print("🧪 DEMO РЕЖИМ - ADMIN TEAM TOOLS")
    print("📊 Тестирование FreeIPA интеграции")
    print("=" * 70)
    print("⚡ Использование demo данных для быстрого запуска")
    print("🔗 FreeIPA интеграция доступна в меню 'Интеграции'")
    print("=" * 70)
    print()
    
    try:
        # Патчим ServiceAdapter
        patch_service_adapter_for_demo()
        
        # Создаем и запускаем приложение
        from src.core.application import Application
        app = Application()
        return await app.start()
        
    except KeyboardInterrupt:
        print("\n⏹️ Приложение остановлено пользователем")
        return 0
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

def cli_main():
    """Синхронная точка входа"""
    try:
        return asyncio.run(main())
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return 1

if __name__ == "__main__":
    exit_code = cli_main()
    print(f"\n🏁 Приложение завершено с кодом: {exit_code}")
    sys.exit(exit_code)
