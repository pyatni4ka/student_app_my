import sys
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QGuiApplication

class QtTestCase(unittest.TestCase):
    """Базовый класс для тестов с поддержкой Qt"""
    
    @classmethod
    def setUpClass(cls):
        """Инициализация Qt приложения перед запуском тестов"""
        # Проверяем, не запущено ли уже приложение
        cls.app = QApplication.instance()
        if not cls.app:
            # Создаем новый экземпляр приложения
            cls.app = QApplication(sys.argv)
        
        # Убеждаемся, что у нас есть QGuiApplication
        cls.gui_app = QGuiApplication.instance()
        if not cls.gui_app:
            cls.gui_app = QGuiApplication(sys.argv)
    
    @classmethod
    def tearDownClass(cls):
        """Очистка после завершения тестов"""
        if cls.app:
            cls.app.quit()
