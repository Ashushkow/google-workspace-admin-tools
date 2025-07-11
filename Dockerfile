# Используем Python 3.11 slim для меньшего размера
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя для запуска приложения
RUN useradd --create-home --shell /bin/bash app

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY --chown=app:app . .

# Создаем необходимые директории
RUN mkdir -p logs data config && \
    chown -R app:app logs data config

# Переключаемся на пользователя app
USER app

# Экспортируем порт (если будет веб-интерфейс)
EXPOSE 8000

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import src.utils.health_check; exit(0 if src.utils.health_check.is_healthy() else 1)"

# Команда запуска
CMD ["python", "main.py"]
