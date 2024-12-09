from typing import Optional, Type, Dict, Any
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal, QSettings, QTimer
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QStatusBar, QProgressBar
from models import User
from ui.window_manager import WindowManager
from utils.cache import cache_method
from loguru import logger


class BaseWindow(QMainWindow):
    """Базовый класс для всех окон приложения"""

    # Сигналы
    user_changed = pyqtSignal(User)  # Сигнал для обновления UI при изменении текущего пользователя
    status_message = pyqtSignal(str, int)  # Сигнал для показа сообщения в статусбаре

    def __init__(self, parent: Optional[QMainWindow] = None):
        super().__init__(parent)

        # Инициализация настроек
        self.settings = QSettings('BMSTU', 'StudentApp')

        # Устанавливаем иконку приложения
        icon_path = Path("resources/icons/bmstu_logo.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            logger.warning(f"Icon not found at {icon_path}")

        # Текущий пользователь
        self._current_user: Optional[User] = None

        # Статус бар
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Настройка окна
        self.restore_window_state()
        self.setup_ui()
        self.setup_connections()

        # Таймер для автоматического скрытия сообщений статусбара
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self.clear_status)

    def setup_ui(self):
        """Настройка интерфейса"""
        raise NotImplementedError

    def setup_connections(self):
        """Настройка сигналов и слотов"""
        self.status_message.connect(self.show_status_message)

    def restore_window_state(self):
        """Восстанавливает состояние окна из настроек"""
        geometry = self.settings.value(f"{self.__class__.__name__}/geometry")
        if geometry:
            self.restoreGeometry(geometry)

        state = self.settings.value(f"{self.__class__.__name__}/windowState")
        if state:
            self.restoreState(state)

    def save_window_state(self):
        """Сохраняет состояние окна в настройки"""
        self.settings.setValue(f"{self.__class__.__name__}/geometry", self.saveGeometry())
        self.settings.setValue(f"{self.__class__.__name__}/windowState", self.saveState())

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
        logger.error(f"{title}: {message}")
        QMessageBox.critical(self, title, message)

    def show_warning(self, title: str, message: str):
        """Показывает предупреждение"""
        logger.warning(f"{title}: {message}")
        QMessageBox.warning(self, title, message)

    def show_info(self, title: str, message: str):
        """Показывает информационное сообщение"""
        logger.info(f"{title}: {message}")
        QMessageBox.information(self, title, message)

    def show_question(self, title: str, message: str) -> bool:
        """Показывает вопрос пользователю"""
        logger.info(f"Question {title}: {message}")
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes

    @cache_method(ttl=300)  # Кэширование на 5 минут
    def get_window_settings(self) -> Dict[str, Any]:
        """Получает настройки окна"""
        return {
            key: self.settings.value(key)
            for key in self.settings.allKeys()
            if key.startswith(f"{self.__class__.__name__}/")
        }

    def show_status_message(self, message: str, timeout: int = 5000):
        """Показывает сообщение в статусбаре"""
        self.status_bar.showMessage(message)
        self._status_timer.start(timeout)

    def clear_status(self):
        """Очищает сообщение в статусбаре"""
        self.status_bar.clearMessage()
        self._status_timer.stop()

    def show_progress(self, value: int, maximum: int = 100):
        """Показывает прогресс в статусбаре"""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        self.progress_bar.show()

    def hide_progress(self):
        """Скрывает прогресс в статусбаре"""
        self.progress_bar.hide()

    def switch_window(self, window_class: Type[QMainWindow], **kwargs):
        """Переключает текущее окно на новое"""
        logger.info(f"Switching to window {window_class.__name__}")
        WindowManager().show_window(window_class, **kwargs)

    def apply_theme(self, dark_mode: bool = False):
        """Применяет тему оформления"""
        if dark_mode:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            self.setPalette(palette)
        else:
            self.setPalette(self.style().standardPalette())

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.show_question(
            "Подтверждение",
            "Вы действительно хотите закрыть приложение?"
        ):
            self.save_window_state()
            event.accept()
        else:
            event.ignore()
