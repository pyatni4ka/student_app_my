import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent

# Путь к основной базе данных
MAIN_DATABASE_PATH = os.path.join(os.path.dirname(BASE_DIR), 'data', 'database.db')
DATABASE_URL = f'sqlite:///{MAIN_DATABASE_PATH}'

# Настройки приложения
APP_NAME = "Система тестирования студентов"
APP_VERSION = "1.0.0"
TEACHER_PASSWORD = os.getenv('TEACHER_PASSWORD', 'admin123')  # Измените на реальный пароль

# Настройки тестирования
TEST_DURATION_MINUTES = 20
QUESTIONS_PER_TEST = 5
THEORY_QUESTIONS_COUNT = 2
PRACTICE_QUESTIONS_COUNT = 2
GRAPHIC_QUESTIONS_COUNT = 1

# Пути к ресурсам
STYLES_DIR = BASE_DIR / 'styles'
MAIN_STYLE = STYLES_DIR / 'main.qss'
DARK_THEME_PATH = STYLES_DIR / 'dark_theme.qss'

# Логирование
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'students_app.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Убедимся, что директории существуют
LOG_DIR.mkdir(parents=True, exist_ok=True)
STYLES_DIR.mkdir(parents=True, exist_ok=True)
