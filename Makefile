#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Makefile для автоматизации задач разработки.
"""

# === Переменные ===
PYTHON := .venv\Scripts\python.exe
PIP := .venv\Scripts\pip.exe
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
MYPY := mypy
DOCKER := docker

# Директории
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs
BUILD_DIR := build
DIST_DIR := dist

# === Основные команды ===

.PHONY: help
help:  ## Показать справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install:  ## Установить зависимости
	$(PIP) install -e .

.PHONY: install-dev
install-dev:  ## Установить зависимости для разработки
	$(PIP) install -e ".[dev]"

.PHONY: clean
clean:  ## Очистить временные файлы
	rm -rf $(BUILD_DIR) $(DIST_DIR) .coverage htmlcov .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# === Тестирование ===

.PHONY: test
test:  ## Запустить все тесты
	$(PYTEST) $(TEST_DIR) -v

.PHONY: test-unit
test-unit:  ## Запустить юнит тесты
	$(PYTEST) $(TEST_DIR)/unit -v

.PHONY: test-integration
test-integration:  ## Запустить интеграционные тесты
	$(PYTEST) $(TEST_DIR)/integration -v

.PHONY: test-coverage
test-coverage:  ## Запустить тесты с покрытием
	$(PYTEST) $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing

.PHONY: test-watch
test-watch:  ## Запустить тесты в режиме наблюдения
	$(PYTEST) $(TEST_DIR) -v --tb=short --maxfail=1 -q

# === Качество кода ===

.PHONY: lint
lint:  ## Запустить все проверки качества кода
	$(BLACK) --check $(SRC_DIR) $(TEST_DIR)
	$(FLAKE8) $(SRC_DIR) $(TEST_DIR)
	$(MYPY) $(SRC_DIR)

.PHONY: format
format:  ## Форматировать код
	$(BLACK) $(SRC_DIR) $(TEST_DIR)

.PHONY: flake8
flake8:  ## Проверить код с flake8
	$(FLAKE8) $(SRC_DIR) $(TEST_DIR)

.PHONY: mypy
mypy:  ## Проверить типы с mypy
	$(MYPY) $(SRC_DIR)

.PHONY: fix
fix:  ## Исправить проблемы с кодом автоматически
	$(BLACK) $(SRC_DIR) $(TEST_DIR)
	isort $(SRC_DIR) $(TEST_DIR)

# === Безопасность ===

.PHONY: security
security:  ## Проверить безопасность
	safety check
	bandit -r $(SRC_DIR)

.PHONY: audit
audit:  ## Аудит зависимостей
	$(PIP) audit

# === Сборка ===

.PHONY: build
build:  ## Собрать пакет
	$(PYTHON) -m build

.PHONY: build-exe
build-exe:  ## Собрать исполняемый файл
	.venv\Scripts\pyinstaller.exe --onefile --windowed --name AdminTeamTools_v2.2.0 main.py

.PHONY: build-docker
build-docker:  ## Собрать Docker образ
	$(DOCKER) build -t admin-team-tools .

.PHONY: build-all
build-all: clean build build-exe build-docker  ## Собрать все варианты

# === Развертывание ===

.PHONY: run
run:  ## Запустить приложение
	$(PYTHON) main_new.py

.PHONY: run-docker
run-docker:  ## Запустить в Docker
	$(DOCKER) run -d --name admin-tools admin-team-tools

.PHONY: run-dev
run-dev:  ## Запустить в режиме разработки
	APP_DEBUG=True $(PYTHON) main_new.py

# === Документация ===

.PHONY: docs
docs:  ## Построить документацию
	cd $(DOCS_DIR) && make html

.PHONY: docs-serve
docs-serve:  ## Запустить сервер документации
	cd $(DOCS_DIR)/_build/html && python -m http.server 8000

# === Развитие ===

.PHONY: init-dev
init-dev:  ## Инициализировать окружение разработки
	$(PIP) install -e ".[dev]"
	pre-commit install
	cp .env.example .env
	mkdir -p logs data cache temp

.PHONY: upgrade-deps
upgrade-deps:  ## Обновить зависимости
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[dev]"

.PHONY: check-deps
check-deps:  ## Проверить устаревшие зависимости
	$(PIP) list --outdated

# === Git ===

.PHONY: commit
commit:  ## Сделать коммит с проверками
	pre-commit run --all-files
	git add -A
	git commit

.PHONY: push
push:  ## Отправить изменения с проверками
	make lint
	make test
	git push

# === Разное ===

.PHONY: health-check
health-check:  ## Проверить состояние приложения
	$(PYTHON) -c "from src.utils.health_check import is_healthy; exit(0 if is_healthy() else 1)"

.PHONY: logs
logs:  ## Показать последние логи
	tail -f logs/admin_tools.log

.PHONY: stats
stats:  ## Статистика проекта
	@echo "Строки кода:"
	@find $(SRC_DIR) -name "*.py" | xargs wc -l | tail -1
	@echo "Файлы Python:"
	@find $(SRC_DIR) -name "*.py" | wc -l
	@echo "Тесты:"
	@find $(TEST_DIR) -name "*.py" | wc -l

.PHONY: version
version:  ## Показать версию
	@$(PYTHON) -c "from src.config.enhanced_config import config; print(config.settings.app_version)"

# === Профили ===

.PHONY: dev
dev: install-dev format lint test  ## Полная проверка для разработки

.PHONY: ci
ci: install-dev lint test-coverage security  ## Пайплайн CI

.PHONY: release
release: clean ci build  ## Подготовить релиз

# === Утилиты ===

.PHONY: shell
shell:  ## Открыть Python shell с загруженными модулями
	$(PYTHON) -i -c "from src.core.application import Application; app = Application()"

.PHONY: db-shell
db-shell:  ## Открыть shell базы данных
	sqlite3 data/admin_tools.db

.PHONY: env-check
env-check:  ## Проверить переменные окружения
	$(PYTHON) -c "from src.config.enhanced_config import config; print(config.export_to_dict())"

# По умолчанию показываем справку
.DEFAULT_GOAL := help
