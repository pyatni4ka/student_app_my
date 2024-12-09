"""Окно входа для преподавателя"""
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import uic
import os
from pathlib import Path
from loguru import logger

from ui.window_manager import WindowManager
from ui.teacher_window import TeacherWindow

# Пути к ресурсам и UI файлу
RESOURCES_PATH = Path(os.path.dirname(os.path.dirname(__file__))) / "resources" / "icons"
UI_PATH = Path(os.path.dirname(__file__)) / "teacher_login_window.ui"

class TeacherLoginWindow(QMainWindow):
    """Класс окна входа для преподавателя"""

    def __init__(self):
        super().__init__()

        # Загружаем UI
        uic.loadUi(UI_PATH, self)

        # Настраиваем окно
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Подключаем обработчики событий
        self.login_button.clicked.connect(self.check_password)
        self.password_input.returnPressed.connect(self.check_password)

        # Скрываем сообщение об ошибке
        self.error_label.hide()

        # Инициализируем WindowManager
        self.window_manager = WindowManager()

        # Таймер для скрытия сообщения об ошибке
        self.error_timer = QTimer()
        self.error_timer.timeout.connect(lambda: self.error_label.hide())
        self.error_timer.setSingleShot(True)

    def check_password(self):
        """Проверяет введенный пароль"""
        password = self.password_input.text().strip()

        if not password:
            self.show_error("Введите пароль")
            return

        if password == "admin":  # TODO: заменить на безопасную проверку пароля
            self.open_teacher_window()
        else:
            self.show_error("Неверный пароль")
            self.password_input.clear()

    def show_error(self, message: str):
        """Показывает сообщение об ошибке"""
        self.error_label.setText(message)
        self.error_label.show()
        self.error_timer.start(3000)  # Скрыть через 3 секунды

    def open_teacher_window(self):
        """Открывает окно преподавателя"""
        try:
            teacher_window = TeacherWindow()
            self.window_manager.switch_to_window(teacher_window)
        except Exception as e:
            logger.error(f"Ошибка при открытии окна преподавателя: {e}")
            QMessageBox.critical(
                self,
                "Ошибка",
                "Не удалось открыть окно преподавателя. Попробуйте позже."
            )

    def mousePressEvent(self, event):
        """Обработчик нажатия кнопки мыши для перемещения окна"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Обработчик перемещения мыши для перемещения окна"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
