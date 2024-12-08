"""
Главный файл приложения
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from ui.login_window import LoginWindow
from ui.styles import STYLES
from ui.window_manager import WindowManager

def parse_arguments():
    """Обработка аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Приложение для управления студентами')
    parser.add_argument('--debug', action='store_true', help='Включить режим отладки')
    return parser.parse_args()

def check_single_instance():
    """Проверка на запуск единственного экземпляра приложения"""
    socket = QLocalSocket()
    socket.connectToServer('StudentAppInstance')
    if socket.waitForConnected(500):
        socket.close()
        return False
    
    server = QLocalServer()
    server.removeServer('StudentAppInstance')
    server.listen('StudentAppInstance')
    return True

def setup_logging(debug_mode=False):
    """Настройка системы логирования"""
    log_level = logging.DEBUG if debug_mode else logging.INFO
    log_file = Path('app.log')
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def setup_application():
    """Настройка приложения"""
    # Устанавливаем путь к плагинам Qt перед созданием QApplication
    qt_plugin_path = os.path.join(os.path.expanduser('~'), 
                                 'AppData', 'Local', 'Packages',
                                 'PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0',
                                 'LocalCache', 'local-packages', 'Python311',
                                 'site-packages', 'PyQt5', 'Qt5', 'plugins')
    
    if os.path.exists(qt_plugin_path):
        os.environ['QT_PLUGIN_PATH'] = qt_plugin_path
        logging.info(f"Установлен путь к плагинам Qt: {qt_plugin_path}")
    else:
        logging.warning(f"Путь к плагинам Qt не найден: {qt_plugin_path}")
    
    # Включаем поддержку High DPI
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLES)
    return app

def main():
    """Основная функция приложения"""
    args = parse_arguments()
    logger = setup_logging(args.debug)
    
    try:
        if not check_single_instance():
            logger.warning("Приложение уже запущено")
            sys.exit(0)
            
        app = setup_application()
        logger.info(f"Qt version: {QT_VERSION_STR}")
        logger.info(f"QT_PLUGIN_PATH: {os.environ.get('QT_PLUGIN_PATH', 'не установлен')}")
        
        WindowManager().show_window(LoginWindow)
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске приложения: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
