#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реализация репозитория аудита.
"""

from typing import List, Dict, Any, Optional
from .interfaces import IAuditRepository
from ..core.di_container import service
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import asyncio


@service(singleton=True)
class SQLiteAuditRepository(IAuditRepository):
    """SQLite репозиторий аудита"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_path = Path("data/audit.db")
        self.db_path.parent.mkdir(exist_ok=True)
        asyncio.create_task(self._init_db())
    
    async def _init_db(self):
        """Инициализация базы данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT
                )
            ''')
            
            # Создаем индексы
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user ON audit_logs(user)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_action ON audit_logs(action)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)')
            
            conn.commit()
            conn.close()
            
            self.logger.info("База данных аудита инициализирована")
        
        except Exception as e:
            self.logger.error(f"Ошибка инициализации БД аудита: {e}")
    
    async def log_action(self, user: str, action: str, resource: str, details: Dict[str, Any] = None) -> bool:
        """Записать действие в аудит"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            details_json = json.dumps(details, ensure_ascii=False) if details else None
            
            cursor.execute('''
                INSERT INTO audit_logs (user, action, resource, details)
                VALUES (?, ?, ?, ?)
            ''', (user, action, resource, details_json))
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Аудит: {user} -> {action} -> {resource}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка записи аудита: {e}")
            return False
    
    async def get_logs(self, user: str = None, action: str = None, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Получить записи аудита"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            
            if user:
                query += " AND user = ?"
                params.append(user)
            
            if action:
                query += " AND action = ?"
                params.append(action)
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC LIMIT 1000"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                log_entry = {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'user': row['user'],
                    'action': row['action'],
                    'resource': row['resource'],
                    'details': json.loads(row['details']) if row['details'] else {},
                    'ip_address': row['ip_address'],
                    'user_agent': row['user_agent']
                }
                logs.append(log_entry)
            
            conn.close()
            
            self.logger.debug(f"Получено {len(logs)} записей аудита")
            return logs
        
        except Exception as e:
            self.logger.error(f"Ошибка получения логов аудита: {e}")
            return []
    
    async def cleanup_old_logs(self, days: int = 90) -> int:
        """Очистить старые записи аудита"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                DELETE FROM audit_logs 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            self.logger.info(f"Удалено {deleted_count} старых записей аудита")
            return deleted_count
        
        except Exception as e:
            self.logger.error(f"Ошибка очистки логов аудита: {e}")
            return 0


@service(singleton=True)
class FileAuditRepository(IAuditRepository):
    """Файловый репозиторий аудита"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        self.audit_file = self.logs_dir / "audit.jsonl"
    
    async def log_action(self, user: str, action: str, resource: str, details: Dict[str, Any] = None) -> bool:
        """Записать действие в аудит"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'user': user,
                'action': action,
                'resource': resource,
                'details': details or {}
            }
            
            with open(self.audit_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            self.logger.debug(f"Аудит: {user} -> {action} -> {resource}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка записи аудита: {e}")
            return False
    
    async def get_logs(self, user: str = None, action: str = None, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Получить записи аудита"""
        try:
            if not self.audit_file.exists():
                return []
            
            logs = []
            
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        
                        # Фильтрация
                        if user and log_entry.get('user') != user:
                            continue
                        
                        if action and log_entry.get('action') != action:
                            continue
                        
                        if start_date and log_entry.get('timestamp', '') < start_date:
                            continue
                        
                        if end_date and log_entry.get('timestamp', '') > end_date:
                            continue
                        
                        logs.append(log_entry)
                    
                    except json.JSONDecodeError:
                        continue
            
            # Сортируем по времени (новые первые)
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Ограничиваем результат
            logs = logs[:1000]
            
            self.logger.debug(f"Получено {len(logs)} записей аудита")
            return logs
        
        except Exception as e:
            self.logger.error(f"Ошибка получения логов аудита: {e}")
            return []
    
    async def cleanup_old_logs(self, days: int = 90) -> int:
        """Очистить старые записи аудита"""
        try:
            if not self.audit_file.exists():
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            # Читаем все записи
            logs = []
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        if log_entry.get('timestamp', '') >= cutoff_str:
                            logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
            
            # Перезаписываем файл
            deleted_count = 0
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                for log_entry in logs:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                    deleted_count += 1
            
            self.logger.info(f"Удалено {deleted_count} старых записей аудита")
            return deleted_count
        
        except Exception as e:
            self.logger.error(f"Ошибка очистки логов аудита: {e}")
            return 0
