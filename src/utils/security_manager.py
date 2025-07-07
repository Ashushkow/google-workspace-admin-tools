# -*- coding: utf-8 -*-
"""
Система безопасности для защиты учетных данных и аудита действий.
"""

import os
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from pathlib import Path


class SecurityManager:
    """
    Менеджер безопасности для защиты учетных данных и аудита.
    """
    
    def __init__(self):
        self.key_file = Path(".security_key")
        self.audit_file = Path("security_audit.json")
        self.session_timeout = timedelta(hours=1)
        self.last_activity = datetime.now()
        
        # Инициализация ключа шифрования
        self._init_encryption()
    
    def _init_encryption(self):
        """Инициализирует ключ шифрования"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.encryption_key)
            # Скрываем файл ключа
            if os.name == 'nt':  # Windows
                os.system(f'attrib +h "{self.key_file}"')
        
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_data(self, data: str) -> str:
        """Шифрует данные"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Расшифровывает данные"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def validate_session(self) -> bool:
        """Проверяет активность сессии"""
        if datetime.now() - self.last_activity > self.session_timeout:
            return False
        return True
    
    def update_activity(self):
        """Обновляет время последней активности"""
        self.last_activity = datetime.now()
    
    def audit_action(self, action: str, user_email: str = "", 
                    details: Dict = None, severity: str = "INFO"):
        """
        Записывает действие в аудит лог.
        
        Args:
            action: Описание действия
            user_email: Email пользователя (если применимо)
            details: Дополнительные детали
            severity: Уровень важности (INFO, WARNING, CRITICAL)
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_email": user_email,
            "details": details or {},
            "severity": severity,
            "session_id": self._get_session_id()
        }
        
        # Загружаем существующий аудит лог
        audit_log = []
        if self.audit_file.exists():
            try:
                with open(self.audit_file, 'r', encoding='utf-8') as f:
                    audit_log = json.load(f)
            except:
                audit_log = []
        
        # Добавляем новую запись
        audit_log.append(audit_entry)
        
        # Ограничиваем размер лога (последние 1000 записей)
        if len(audit_log) > 1000:
            audit_log = audit_log[-1000:]
        
        # Сохраняем лог
        try:
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                json.dump(audit_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка записи в аудит лог: {e}")
    
    def _get_session_id(self) -> str:
        """Генерирует ID сессии"""
        return hashlib.md5(f"{os.getpid()}{self.last_activity}".encode()).hexdigest()[:8]
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Получает записи из аудит лога"""
        if not self.audit_file.exists():
            return []
        
        try:
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                audit_log = json.load(f)
            return audit_log[-limit:]
        except:
            return []
    
    def secure_delete_file(self, file_path: Path):
        """Безопасное удаление файла с перезаписью"""
        if not file_path.exists():
            return
        
        try:
            # Перезаписываем файл случайными данными
            file_size = file_path.stat().st_size
            with open(file_path, 'wb') as f:
                f.write(secrets.token_bytes(file_size))
            
            # Удаляем файл
            file_path.unlink()
            
        except Exception as e:
            print(f"Ошибка безопасного удаления файла: {e}")


# Глобальный экземпляр менеджера безопасности
security_manager = SecurityManager()
