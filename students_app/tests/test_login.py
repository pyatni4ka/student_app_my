import sys
import os
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.login_window import LoginWindow
from ui.teacher_login_window import TeacherLoginWindow
from tests.test_base import QtTestCase

class TestLogin(QtTestCase):
    def setUp(self):
        self.login_window = LoginWindow()
        self.teacher_login_window = TeacherLoginWindow()

    def test_student_login_fields(self):
        """Тест наличия всех необходимых полей в окне входа студента"""
        self.assertIsNotNone(self.login_window.group_input)
        self.assertIsNotNone(self.login_window.name_input)
        self.assertIsNotNone(self.login_window.login_button)

    def test_teacher_login_field(self):
        """Тест наличия поля пароля в окне входа преподавателя"""
        self.assertIsNotNone(self.teacher_login_window.password_input)
        self.assertIsNotNone(self.teacher_login_window.login_button)

    def test_student_login_validation(self):
        """Тест валидации полей входа студента"""
        # Проверяем пустые поля
        QTest.mouseClick(self.login_window.login_button, Qt.LeftButton)
        self.assertFalse(self.login_window.isHidden())  # Окно не должно закрыться

        # Проверяем только группу
        self.login_window.group_input.setText("ПИ-231")
        QTest.mouseClick(self.login_window.login_button, Qt.LeftButton)
        self.assertFalse(self.login_window.isHidden())

        # Проверяем полные данные
        self.login_window.name_input.setText("Иван Иванов")
        QTest.mouseClick(self.login_window.login_button, Qt.LeftButton)
        # Здесь должна быть проверка перехода к следующему окну

    def test_teacher_login_validation(self):
        """Тест валидации пароля преподавателя"""
        # Проверяем пустой пароль
        QTest.mouseClick(self.teacher_login_window.login_button, Qt.LeftButton)
        self.assertFalse(self.teacher_login_window.isHidden())

        # Проверяем неверный пароль
        self.teacher_login_window.password_input.setText("wrong_password")
        QTest.mouseClick(self.teacher_login_window.login_button, Qt.LeftButton)
        self.assertFalse(self.teacher_login_window.isHidden())

    def tearDown(self):
        self.login_window.close()
        self.teacher_login_window.close()

if __name__ == '__main__':
    unittest.main()