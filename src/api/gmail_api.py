#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail API модуль для отправки приветственных писем.
"""

import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    build = None
    HttpError = Exception

logger = logging.getLogger(__name__)


class GmailService:
    """Сервис для работы с Gmail API"""
    
    def __init__(self, credentials):
        """
        Инициализация Gmail сервиса
        
        Args:
            credentials: Google OAuth2 credentials
        """
        self.credentials = credentials
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Инициализация Gmail API сервиса"""
        try:
            if build is None:
                logger.error("❌ Google API библиотеки не установлены")
                return
            
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("✅ Gmail API сервис инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Gmail API: {e}")
    
    def create_welcome_message(self, to_email: str, user_name: str, 
                             temporary_password: str, admin_email: str) -> Optional[Dict]:
        """
        Создание приветственного письма для нового пользователя
        
        Args:
            to_email: Email получателя (нового пользователя)
            user_name: Имя пользователя
            temporary_password: Временный пароль
            admin_email: Email администратора (отправителя)
            
        Returns:
            Словарь с данными сообщения или None при ошибке
        """
        try:
            # Создаем многочастное сообщение
            msg = MIMEMultipart('alternative')
            msg['To'] = to_email
            msg['From'] = admin_email
            msg['Subject'] = 'Добро пожаловать в Google Workspace!'
            
            # HTML версия письма
            html_content = self._create_html_welcome_template(
                user_name, to_email, temporary_password
            )
            
            # Текстовая версия письма
            text_content = self._create_text_welcome_template(
                user_name, to_email, temporary_password
            )
            
            # Добавляем части сообщения
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Кодируем сообщение в base64
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            
            return {'raw': raw_message}
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания письма: {e}")
            return None
    
    def _create_html_welcome_template(self, user_name: str, email: str, 
                                    password: str) -> str:
        """Создание HTML шаблона приветственного письма"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; }}
                .header {{ background: #4285f4; color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; line-height: 1.6; }}
                .credentials {{ background: #f8f9fa; padding: 20px; border-left: 4px solid #4285f4; margin: 20px 0; }}
                .button {{ display: inline-block; background: #4285f4; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Добро пожаловать!</h1>
                    <p>Ваша учетная запись Google Workspace готова</p>
                </div>
                
                <div class="content">
                    <h2>Здравствуйте, {user_name}!</h2>
                    
                    <p>Для вас была создана учетная запись в Google Workspace. Теперь у вас есть доступ к:</p>
                    
                    <ul>
                        <li>📧 Gmail - корпоративная электронная почта</li>
                        <li>📁 Google Drive - облачное хранилище</li>
                        <li>📄 Google Docs, Sheets, Slides - офисные приложения</li>
                        <li>📅 Google Calendar - календарь и планирование</li>
                        <li>💬 Google Meet - видеоконференции</li>
                    </ul>
                    
                    <div class="credentials">
                        <h3>🔐 Данные для входа:</h3>
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Временный пароль:</strong> <code>{password}</code></p>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Важно:</strong> Обязательно смените пароль при первом входе в систему!
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="https://accounts.google.com/" class="button">Войти в Google</a>
                    </div>
                    
                    <h3>📱 Мобильные приложения:</h3>
                    <p>Загрузите приложения Google на свой телефон для удобного доступа:</p>
                    <ul>
                        <li>Gmail</li>
                        <li>Google Drive</li>
                        <li>Google Calendar</li>
                        <li>Google Meet</li>
                    </ul>
                    
                    <h3>🛡️ Безопасность:</h3>
                    <ul>
                        <li>Используйте надежный пароль</li>
                        <li>Настройте двухфакторную аутентификацию</li>
                        <li>Не сообщайте свои данные третьим лицам</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>Если у вас есть вопросы, обратитесь к администратору.</p>
                    <p>© Google Workspace Admin Tools</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_text_welcome_template(self, user_name: str, email: str, 
                                    password: str) -> str:
        """Создание текстового шаблона приветственного письма"""
        return f"""
Добро пожаловать в Google Workspace!

Здравствуйте, {user_name}!

Для вас была создана учетная запись в Google Workspace.

ДАННЫЕ ДЛЯ ВХОДА:
Email: {email}
Временный пароль: {password}

ВАЖНО: Обязательно смените пароль при первом входе!

Теперь у вас есть доступ к:
- Gmail - корпоративная электронная почта
- Google Drive - облачное хранилище  
- Google Docs, Sheets, Slides - офисные приложения
- Google Calendar - календарь и планирование
- Google Meet - видеоконференции

Для входа перейдите на: https://accounts.google.com/

БЕЗОПАСНОСТЬ:
- Используйте надежный пароль
- Настройте двухфакторную аутентификацию
- Не сообщайте свои данные третьим лицам

При возникновении вопросов обратитесь к администратору.

--
Google Workspace Admin Tools
        """
    
    def send_welcome_email(self, to_email: str, user_name: str, 
                          temporary_password: str, admin_email: str) -> bool:
        """
        Отправка приветственного письма новому пользователю
        
        Args:
            to_email: Email получателя
            user_name: Имя пользователя
            temporary_password: Временный пароль
            admin_email: Email администратора
            
        Returns:
            True если письмо отправлено успешно
        """
        if not self.service:
            logger.error("❌ Gmail сервис не инициализирован")
            return False
        
        try:
            # Создаем сообщение
            message = self.create_welcome_message(
                to_email, user_name, temporary_password, admin_email
            )
            
            if not message:
                logger.error("❌ Не удалось создать сообщение")
                return False
            
            # Отправляем письмо
            result = self.service.users().messages().send(
                userId='me', body=message
            ).execute()
            
            logger.info(f"✅ Приветственное письмо отправлено: {to_email}")
            logger.info(f"📧 Message ID: {result.get('id')}")
            
            return True
            
        except HttpError as e:
            logger.error(f"❌ HTTP ошибка при отправке письма: {e}")
            if hasattr(e, 'resp') and e.resp:
                logger.error(f"🔍 Статус: {e.resp.status}")
                logger.error(f"🔍 Ответ: {e.content}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки письма: {e}")
            return False
    
    def test_gmail_access(self) -> bool:
        """
        Тестирование доступа к Gmail API
        
        Returns:
            True если доступ есть
        """
        if not self.service:
            return False
        
        try:
            # Получаем профиль пользователя
            profile = self.service.users().getProfile(userId='me').execute()
            logger.info(f"✅ Gmail API доступен. Email: {profile.get('emailAddress')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка доступа к Gmail API: {e}")
            return False


def create_gmail_service(credentials) -> Optional[GmailService]:
    """
    Создание экземпляра Gmail сервиса
    
    Args:
        credentials: Google OAuth2 credentials
        
    Returns:
        Экземпляр GmailService или None при ошибке
    """
    try:
        gmail_service = GmailService(credentials)
        if gmail_service.service:
            return gmail_service
        return None
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания Gmail сервиса: {e}")
        return None
