import sys
import logging
from PyQt6.QtWidgets import QApplication
from ui.windows.registration_window import RegistrationWindow
from core.database.manager import DatabaseManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('students_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        # Инициализация базы данных
        db = DatabaseManager()
        
        # Создание приложения
        app = QApplication(sys.argv)
        
        # Загрузка стилей
        with open('styles/main.qss', 'r') as f:
            app.setStyleSheet(f.read())
        
        # Запуск главного окна
        window = RegistrationWindow()
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
