#!/bin/bash
# -*- coding: utf-8 -*-
"""
Скрипт для управления UX версиями Admin Team Tools
Позволяет переключаться между оригинальной и улучшенной версией
"""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔄 UX Version Manager - Admin Team Tools"
echo "======================================="

# Проверяем наличие файлов
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Основной файл main.py не найден!${NC}"
    exit 1
fi

if [ ! -f "main_ux_improved.py" ]; then
    echo -e "${RED}❌ Улучшенная версия main_ux_improved.py не найдена!${NC}"
    exit 1
fi

# Определяем текущую версию
current_version=""
if grep -q "UX IMPROVED VERSION" main.py; then
    current_version="improved"
else
    current_version="original"
fi

echo -e "📊 Текущая версия: ${BLUE}$current_version${NC}"
echo ""

echo "Выберите действие:"
echo "1) Переключиться на улучшенную UX версию"
echo "2) Вернуться к оригинальной версии"  
echo "3) Показать различия между версиями"
echo "4) Создать резервную копию текущей версии"
echo "5) Выход"
echo ""

read -p "Введите номер (1-5): " choice

case $choice in
    1)
        if [ "$current_version" = "improved" ]; then
            echo -e "${YELLOW}⚠️ Уже используется улучшенная версия!${NC}"
        else
            echo -e "${BLUE}🔄 Переключение на улучшенную UX версию...${NC}"
            cp main.py "main_original_backup_$(date +%Y%m%d_%H%M%S).py"
            cp main_ux_improved.py main.py
            echo -e "${GREEN}✅ Успешно переключено на улучшенную версию!${NC}"
            echo -e "${YELLOW}💾 Оригинал сохранен как main_original_backup_*.py${NC}"
        fi
        ;;
    2)
        if [ "$current_version" = "original" ]; then
            echo -e "${YELLOW}⚠️ Уже используется оригинальная версия!${NC}"
        else
            echo -e "${BLUE}🔄 Возврат к оригинальной версии...${NC}"
            
            # Ищем последний backup оригинала
            backup_file=$(ls -t main_original_backup_*.py 2>/dev/null | head -n1)
            if [ -n "$backup_file" ]; then
                cp "$backup_file" main.py
                echo -e "${GREEN}✅ Успешно восстановлена оригинальная версия из $backup_file${NC}"
            else
                echo -e "${RED}❌ Backup оригинальной версии не найден!${NC}"
                echo -e "${YELLOW}💡 Попробуйте восстановить из git: git checkout HEAD~1 main.py${NC}"
            fi
        fi
        ;;
    3)
        echo -e "${BLUE}📋 Показ различий между версиями...${NC}"
        if command -v diff &> /dev/null; then
            echo "=== ОСНОВНЫЕ РАЗЛИЧИЯ ==="
            if [ "$current_version" = "improved" ]; then
                backup_file=$(ls -t main_original_backup_*.py 2>/dev/null | head -n1)
                if [ -n "$backup_file" ]; then
                    diff -u "$backup_file" main.py | head -20
                else
                    echo "Backup оригинала не найден для сравнения"
                fi
            else
                diff -u main.py main_ux_improved.py | head -20
            fi
        else
            echo -e "${YELLOW}⚠️ Команда diff недоступна${NC}"
        fi
        ;;
    4)
        backup_name="main_manual_backup_$(date +%Y%m%d_%H%M%S).py"
        cp main.py "$backup_name"
        echo -e "${GREEN}✅ Резервная копия создана: $backup_name${NC}"
        ;;
    5)
        echo -e "${BLUE}👋 Выход из менеджера версий${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Неверный выбор!${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎯 Операция завершена!${NC}"
echo ""
echo "📋 Полезные команды:"
echo "  • python main.py          - запуск приложения"
echo "  • bash switch_ux.sh       - повторный вызов этого скрипта"
echo "  • ls -la main*.py          - список всех версий"
echo ""
