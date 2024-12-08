"""
Главный файл приложения
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging
from PyQt5.QtWidgets import (
    QApplication, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QCoreApplication
from ui.login_window import LoginWindow
from ui.styles import STYLES
from ui.window_manager import WindowManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Основная функция приложения"""
    try:
        # Устанавливаем высокое DPI до создания QApplication
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        app = QApplication(sys.argv)
        app.setStyleSheet(STYLES)
        
        # Создаем и показываем окно входа через менеджер окон
        WindowManager().show_window(LoginWindow)
        
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
