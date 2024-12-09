from setuptools import setup, find_packages

setup(
    name="students_app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # UI компоненты
        "PyQt5>=5.15.9,<5.16",
        "PyQt5-Qt5>=5.15.2,<5.16",
        "PyQt5-sip>=12.12.2,<13.0",
        "PyQt5-tools>=5.15.9.3.3,<5.16",

        # База данных
        "SQLAlchemy>=2.0.23,<2.1",
        "alembic>=1.13.0,<1.14",
        "aiosqlite>=0.19.0",  # Для асинхронной работы с SQLite

        # Криптография и безопасность
        "bcrypt>=4.1.1,<4.2",
        "python-jose>=3.3.0,<3.4",
        "passlib>=1.7.4",  # Для хеширования паролей

        # Обработка данных
        "pandas>=2.1.3,<2.2",
        "numpy>=1.26.2,<1.27",
        "matplotlib>=3.8.2,<3.9",

        # Генерация отчетов
        "openpyxl>=3.1.2,<3.2",
        "reportlab>=4.0.7,<4.1",
        "jinja2>=3.1.2",  # Для шаблонов отчетов

        # Логирование и отладка
        "loguru>=0.7.2,<0.8",

        # Кэширование
        "cachetools>=5.3.2",

        # Типизация
        "typing_extensions>=4.8.0",
        "mypy>=1.7.1",
    ],
    python_requires=">=3.11",
)
