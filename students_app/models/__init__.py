"""
Инициализация моделей данных
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .base import Base
from .user import User, UserRole
from .test import (Test, Question, QuestionOption, TestAttempt, UserAnswer,
                  QuestionType)

# Создаем движок базы данных
engine = create_engine('sqlite:///questions.db', echo=True)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем все таблицы
Base.metadata.create_all(bind=engine)

def get_db():
    """Получает сессию базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Экспортируем все модели
__all__ = [
    'Base',
    'User',
    'UserRole',
    'Test',
    'Question',
    'QuestionOption',
    'TestAttempt',
    'UserAnswer',
    'QuestionType',
    'get_db',
]
