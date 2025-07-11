#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Заглушка для CLI приложения.
"""

import logging


class CLIApplication:
    """CLI приложение (заглушка)"""
    
    def __init__(self, user_service=None, group_service=None):
        self.user_service = user_service
        self.group_service = group_service
        self.logger = logging.getLogger(__name__)
    
    async def run(self) -> int:
        """Запуск CLI приложения"""
        self.logger.info("CLI режим (заглушка)")
        print("🖥️ CLI режим пока не реализован")
        print("ℹ️ Используйте GUI режим или подождите реализации CLI")
        return 0
