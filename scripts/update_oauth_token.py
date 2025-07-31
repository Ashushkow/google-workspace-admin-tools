#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление OAuth токена для Gmail API scopes.
"""

import sys
import os
from pathlib import Path

def update_oauth_token():
    """Обновление OAuth токена с новыми scopes"""
    print("🔄 ОБНОВЛЕНИЕ OAUTH ТОКЕНА ДЛЯ GMAIL API")
    print("=" * 50)
    
    token_file = Path("token.pickle")
    
    if token_file.exists():
        print("🗑️ Удаление старого токена...")
        try:
            token_file.unlink()
            print("✅ Старый токен удален")
        except Exception as e:
            print(f"❌ Ошибка удаления токена: {e}")
            return False
    else:
        print("ℹ️ Старый токен не найден")
    
    print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. 🚀 Запустите приложение: python main.py")
    print("2. 🌐 Откроется браузер для повторной авторизации")
    print("3. ✅ Разрешите доступ к Gmail при авторизации")
    print("4. 🔄 После авторизации запустите: python setup_gmail_api.py")
    
    print("\n⚠️ ВАЖНО:")
    print("При авторизации убедитесь, что разрешили:")
    print("- Чтение и управление почтой Gmail")
    print("- Отправка писем от вашего имени")
    
    return True


def main():
    """Главная функция"""
    print("🔄 OAuth Token Updater для Gmail API")
    print("Этот скрипт обновит токен авторизации для работы с Gmail API.\n")
    
    response = input("Продолжить обновление токена? (y/N): ").strip().lower()
    
    if response in ['y', 'yes', 'да']:
        if update_oauth_token():
            print("\n✅ Готово! Теперь запустите приложение для повторной авторизации.")
        else:
            print("\n❌ Произошла ошибка при обновлении токена.")
    else:
        print("❌ Обновление отменено.")


if __name__ == "__main__":
    main()
