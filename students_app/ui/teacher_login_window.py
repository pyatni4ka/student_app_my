"""Окно входа для преподавателя"""
import os
import sys
import logging
from functools import lru_cache
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPainterPath
from ui.window_manager import WindowManager
from ui.teacher_window import TeacherWindow

logger = logging.getLogger(__name__)

# Предварительно загружаем и кэшируем изображения при импорте модуля
RESOURCES_PATH = Path(os.path.dirname(os.path.dirname(__file__))) / "resources" / "icons"
LOGO_PATH = str(RESOURCES_PATH / "bmstu_logo.svg")
LOCK_PATH = str(RESOURCES_PATH / "lock.svg")

@lru_cache(maxsize=2)
def load_pixmap(path: str, size: int) -> QPixmap:
    """Загружает и кэширует изображение"""
    pixmap = QPixmap(path)
    if not pixmap.isNull():
        return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return QPixmap()

# Предварительно загружаем изображения
LOGO_PIXMAP = load_pixmap(LOGO_PATH, 50)
LOCK_PIXMAP = load_pixmap(LOCK_PATH, 20)

class RoundedWidget(QWidget):
    """Виджет с закругленными углами для поля ввода"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            RoundedWidget {
                background-color: #f8f9fa;
                border-radius: 6px;
            }
        """)

class ModernButton(QPushButton):
    """Современная кнопка в стиле Material Design"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(40)
        self.setMinimumWidth(280)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 24px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1E88E5;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)

class TeacherLoginWindow(QMainWindow):
    """Класс окна входа для преподавателя"""
    
    # Определяем стили как константу класса
    WINDOW_STYLE = """
        QMainWindow {
            background-color: white;
        }
        #password-input {
            border: none;
            background: transparent;
            font-size: 15px;
            padding: 8px 0;
            color: #333;
        }
        #password-input::placeholder {
            color: #999;
        }
        #header-title {
            color: #2196F3;
            font-size: 24px;
            font-weight: 500;
            margin: 16px 0;
        }
        #input-label {
            font-size: 14px;
            color: #666;
            margin-bottom: 6px;
        }
        QLabel {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
        }
    """
    
    def __init__(self):
        super().__init__()
        # Устанавливаем базовые параметры окна
        self.setWindowTitle("Вход для преподавателя")
        self.setFixedSize(480, 400)
        self.setStyleSheet(self.WINDOW_STYLE)
        
        # Создаем основной виджет и компоновщик
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 30, 50, 50)
        main_layout.setSpacing(20)
        
        # Добавляем логотип
        logo_label = QLabel()
        logo_label.setObjectName("logo-small")
        if not LOGO_PIXMAP.isNull():
            scaled_logo = LOGO_PIXMAP.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("МГТУ")
            logo_label.setStyleSheet("font-weight: bold; font-size: 24px;")
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)
        
        # Добавляем заголовок
        title_label = QLabel("Вход для преподавателя")
        title_label.setObjectName("header-title")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        main_layout.addSpacing(20)
        
        # Добавляем поле для пароля
        password_label = QLabel("Пароль")
        password_label.setObjectName("input-label")
        main_layout.addWidget(password_label)
        
        # Контейнер для поля пароля с иконкой
        password_container = RoundedWidget()
        password_container.setFixedHeight(44)
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(12, 0, 12, 0)
        password_layout.setSpacing(8)
        
        # Добавляем иконку замка
        lock_icon = QLabel()
        lock_icon.setFixedSize(20, 20)
        if not LOCK_PIXMAP.isNull():
            scaled_lock = LOCK_PIXMAP.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lock_icon.setPixmap(scaled_lock)
        else:
            lock_icon.setText("🔒")
            lock_icon.setStyleSheet("font-size: 16px;")
        password_layout.addWidget(lock_icon)
        
        # Поле ввода пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("password-input")
        self.password_input.returnPressed.connect(self.handle_login)
        password_layout.addWidget(self.password_input)
        
        main_layout.addWidget(password_container)
        main_layout.addSpacing(30)
        
        # Добавляем кнопку входа с центрированием
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.login_button = ModernButton("Войти")
        button_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        self.login_button.clicked.connect(self.handle_login)
        
        main_layout.addWidget(button_container)
        main_layout.addStretch()
        
        # Устанавливаем фокус на поле ввода пароля
        self.password_input.setFocus()
    
    def handle_login(self):
        """Обработка входа преподавателя"""
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пожалуйста, введите пароль.",
                QMessageBox.Ok
            )
            return
            
        if password == "admin":
            try:
                # Очищаем поле пароля перед открытием нового окна
                self.password_input.clear()
                WindowManager().show_window(TeacherWindow)
            except Exception as e:
                error_msg = f"Ошибка при открытии окна преподавателя: {str(e)}"
                logger.error(error_msg, exc_info=True)
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    error_msg,
                    QMessageBox.Ok
                )
        else:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Неверный пароль. Пожалуйста, попробуйте снова.",
                QMessageBox.Ok
            )
            self.password_input.clear()
            self.password_input.setFocus()
