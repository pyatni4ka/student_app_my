"""
Главный файл приложения
"""

import sys
import platform
import argparse
from contextlib import contextmanager
from typing import Generator, Any
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QtMsgType, QT_VERSION_STR, PYQT_VERSION_STR, Qt
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

from ui.login_window import LoginWindow
from ui.window_manager import WindowManager
from utils.styles import STYLES
from utils.logger import setup_logger
from loguru import logger
from database.db_manager import DatabaseManager


def parse_arguments() -> argparse.Namespace:
    """Обработка аргументов командной строки"""
    parser = argparse.ArgumentParser(description="Student Application")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()


def cleanup(app: QApplication) -> None:
    """Очистка ресурсов перед выходом"""
    app.quit()


def setup_application() -> QApplication:
    """Настройка приложения"""
    # Устанавливаем атрибуты до создания приложения
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # Создаем приложение
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    app.setStyleSheet(STYLES)

    return app


@contextmanager
def single_instance() -> Generator[QLocalServer, None, None]:
    """Контекстный менеджер для проверки единственного экземпляра приложения"""
    socket = QLocalSocket()
    socket.connectToServer("StudentAppInstance")

    if socket.waitForConnected(500):
        socket.close()
        logger.warning("Application is already running")
        sys.exit(1)

    server = QLocalServer()
    server.removeServer("StudentAppInstance")
    server.listen("StudentAppInstance")

    try:
        yield server
    finally:
        server.close()


def qt_message_handler(mode: QtMsgType,
                         context: Any,
                         message: str) -> None:
    """Обработчик сообщений Qt"""
    if mode == QtMsgType.QtDebugMsg:
        logger.debug(message)
    elif mode == QtMsgType.QtInfoMsg:
        logger.info(message)
    elif mode == QtMsgType.QtWarningMsg:
        logger.warning(message)
    elif mode == QtMsgType.QtCriticalMsg:
        logger.critical(message)
    elif mode == QtMsgType.QtFatalMsg:
        logger.error(message)


def main() -> None:
    """Главная функция приложения"""
    try:
        # Создаем приложение
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Инициализация логгера
        setup_logger()

        # Информация о версиях
        logger.info(f"Qt version: {QT_VERSION_STR}")
        logger.info(f"PyQt version: {PYQT_VERSION_STR}")
        logger.info(f"Python version: {platform.python_version()}")

        # Создаем менеджер базы данных
        db_path = os.path.join(os.path.dirname(__file__), "database", "student_app.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db_manager = DatabaseManager(db_path)

        # Создаем менеджер окон
        window_manager = WindowManager()

        # Создаем и показываем окно входа
        login_window = LoginWindow(db_manager)
        window_manager.show_window(login_window)

        logger.info("Окно входа создано и отображено")

        # Устанавливаем стили
        app.setStyleSheet(STYLES)

        logger.info("Запускаем главный цикл приложения")
        sys.exit(app.exec_())

    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception:
        logger.exception("Неожиданная ошибка при запуске приложения")
        sys.exit(1)
