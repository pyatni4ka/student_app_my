"""
Базовый класс для окон приложения
"""

from typing import Optional, Type

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from models import User
from ui.window_manager import WindowManager


class BaseWindow(QMainWindow):
    """Базовый класс для всех окон приложения"""
    
    # Сигнал для обновления UI при изменении текущего пользователя
    user_changed = pyqtSignal(User)
    
    def __init__(self, parent: Optional[QMainWindow] = None):
        super().__init__(parent)
        
        # Устанавливаем иконку приложения
        self.setWindowIcon(QIcon("resources/icons/bmstu_logo.png"))
        
        # Текущий пользователь
        self._current_user: Optional[User] = None
        
        # Настройка окна
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        raise NotImplementedError
    
    def setup_connections(self):
        """Настройка сигналов и слотов"""
        pass
    
    @property
    def current_user(self) -> Optional[User]:
        """Получает текущего пользователя"""
        return self._current_user
    
    @current_user.setter
    def current_user(self, user: Optional[User]):
        """Устанавливает текущего пользователя"""
        self._current_user = user
        self.user_changed.emit(user)
    
    def show_error(self, title: str, message: str):
        """Показывает сообщение об ошибке"""
        QMessageBox.critical(self, title, message)
    
    def show_warning(self, title: str, message: str):
        """Показывает предупреждение"""
        QMessageBox.warning(self, title, message)
    
    def show_info(self, title: str, message: str):
        """Показывает информационное сообщение"""
        QMessageBox.information(self, title, message)
    
    def show_question(self, title: str, message: str) -> bool:
        """Показывает вопрос пользователю"""
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def switch_window(self, window_class: Type[QMainWindow], **kwargs):
        """Переключает текущее окно на новое"""
        WindowManager().show_window(window_class, **kwargs)
    
    def closeEvent(self, event: QCloseEvent):
        """Обработка закрытия окна"""
        if self.show_question(
            "Подтверждение",
            "Вы действительно хотите закрыть приложение?"
        ):
            event.accept()
        else:
            event.ignore()
