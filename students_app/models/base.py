"""
Базовые классы для моделей данных
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class CustomBase:
    """Базовый класс для всех моделей"""

    @declared_attr
    def __tablename__(cls) -> str:
        """Автоматически генерирует имя таблицы из имени класса"""
        return cls.__name__.lower()

    # Общие поля для всех таблиц
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует модель в словарь"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        """Строковое представление объекта"""
        values = ", ".join(
            f"{c.name}={getattr(self, c.name)!r}" for c in self.__table__.columns
        )
        return f"{self.__class__.__name__}({values})"


# Создаем базовый класс для моделей
Base = declarative_base(cls=CustomBase)
