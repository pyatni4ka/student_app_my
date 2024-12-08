import sys
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

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

    @staticmethod
    def click_button(button):
        """Вспомогательный метод для клика по кнопке"""
        QTest.mouseClick(button, Qt.LeftButton)

    @staticmethod
    def enter_text(widget, text):
        """Вспомогательный метод для ввода текста"""
        widget.setText(text)
        QTest.keyClick(widget, Qt.Key_Return)

    @staticmethod
    def select_combo_item(combo, text):
        """Выбор элемента в комбобоксе"""
        index = combo.findText(text)
        combo.setCurrentIndex(index)

    def assertWindowVisible(self, window):
        """Проверка видимости окна"""
        self.assertTrue(window.isVisible())

    def assertWindowHidden(self, window):
        """Проверка скрытия окна"""
        self.assertTrue(window.isHidden())
