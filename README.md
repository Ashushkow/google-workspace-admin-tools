<div align="center">

#  Admin Team Tools

### Профессиональное приложение для управления Google Workspace

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.2.0-brightgreen.svg)](https://github.com/Ashushkow/google-workspace-admin-tools/releases/tag/v2.2.0)
[![Tests](https://img.shields.io/badge/tests-25%2B%20passing-success.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-75%25-green.svg)](#testing)
[![Release](https://img.shields.io/badge/release-ready%20to%20use-success.svg)](https://github.com/Ashushkow/google-workspace-admin-tools/releases/tag/v2.2.0)

**Современное решение для администрирования пользователей, групп и календарей Google Workspace**

> **🎉 НОВЫЙ РЕЛИЗ v2.2.0!** Готовый к использованию Windows executable доступен для скачивания!  
> **📦 [Скачать AdminTeamTools_v2.2.0_Release.zip](https://github.com/Ashushkow/google-workspace-admin-tools/releases/tag/v2.2.0)**

[ Быстрый старт](#-быстрый-старт)  
[ Скачать релиз](#-скачать-готовое-приложение)  
[ Документация](#-документация)  
[ Возможности](#-возможности)  
[ API](#-api-и-интеграции)  
[ Статистика](#-статистика-проекта)

*Интуитивный интерфейс для управления Google Workspace*

</div>

---

## 🎯 Скачать готовое приложение

### 📦 Релиз v2.2.0 - Готов к использованию!

**Скачайте уже скомпилированное приложение для Windows:**

🔗 **[AdminTeamTools_v2.2.0_Release.zip](https://github.com/Ashushkow/google-workspace-admin-tools/releases/tag/v2.2.0)** (36.1 МБ)

#### 🚀 Что в релизе:
- ✅ **AdminTeamTools_v2.2.0.exe** - готовое приложение (36.5 МБ)
- ✅ **README_INSTALL.md** - подробная инструкция по установке
- ✅ **Скрипт запуска** - удобный bat файл для запуска
- ✅ **Шаблоны конфигурации** - credentials.json и .env файлы

#### ⚡ Быстрый старт с готовым приложением:
1. Скачайте и распакуйте архив
2. Настройте `credentials.json` (подробно в README_INSTALL.md)
3. Запустите через `Запуск Admin Team Tools.bat`

#### 🔧 Требования:
- Windows 10/11 (64-bit)
- Права администратора Google Workspace
- Интернет для Google API

---

##  Что это?

**Admin Team Tools**  это мощное desktop-приложение с графическим интерфейсом для управления Google Workspace. Приложение предоставляет удобные инструменты для администраторов, позволяя эффективно управлять пользователями, группами и календарями организации.

###  Ключевые особенности:

-  **Безопасная OAuth 2.0 авторизация**  интерактивная аутентификация через браузер
-  **Современный GUI интерфейс**  удобное управление через графический интерфейс
-  **Высокая производительность**  асинхронная архитектура и кэширование
-  **Надежность**  полное логирование действий и обработка ошибок
-  **Автоматизация**  массовые операции и пакетная обработка
-  **🆕 FreeIPA Интеграция**  управление группами в FreeIPA (без синхронизации пользователей)

##  Статистика проекта

| Метрика | Значение |
|---------|----------|
|  Строк кода | ~8500+ |
|  Тестов | 25+ (6 автоматических + 19 ручных) |
|  Документов | 20+ |
|  Скриптов | 15+ |
|  Зависимостей | 25+ |
|  Версия | **2.2.0** 🎉 |
|  Python версия | 3.8+ (рекомендуется 3.12+) |
|  Модулей | 40+ |
|  API интеграций | 6 (Directory, Drive, Calendar, Reports, Groups, **FreeIPA**) |
|  Фич | 35+ основных функций |
|  Покрытие тестами | 75%+ |
|  Методы авторизации | 2 (OAuth 2.0, Service Account) |
|  **Готовый релиз** | ✅ **Windows EXE доступен** |
|  Внешние интеграции | 1 (**FreeIPA** - управление группами) |

**Последнее обновление статистики**: Июль 2025

---

## 🆕 FreeIPA Интеграция

**Новая возможность!** Интеграция с FreeIPA для централизованного управления пользователями и группами.

### ✨ Возможности FreeIPA интеграции:

-  **Управление группами** - создание и управление группами в FreeIPA
- 🔄 **Синхронизация групп** - перенос групп из Google Workspace в FreeIPA
- 📊 **Сравнение данных** между Google Workspace и FreeIPA (только группы)
- 🛡️ **Безопасность** - поддержка Kerberos аутентификации
- ⚡ **GUI интерфейс** для удобного управления
- ⚠️ **Примечание**: Синхронизация пользователей отключена по требованию

### 🚀 Быстрый старт с FreeIPA:

1. **Откройте Admin Team Tools**
2. **Нажмите кнопку "🔗 FreeIPA"** в панели инструментов
3. **Настройте подключение** в вкладке "Подключение"
4. **Управляйте группами** в вкладке "Управление группами"
5. **Просматривайте статистику** в вкладке "Статистика"

📖 **Документация**: [FreeIPA Integration Guide](docs/FREEIPA_INTEGRATION_GUIDE.md)  
🖥️ **GUI Руководство**: [FreeIPA GUI Guide](docs/FREEIPA_GUI_GUIDE.md)  
⚡ **Быстрый старт**: [FREEIPA_QUICKSTART.md](FREEIPA_QUICKSTART.md)

---
