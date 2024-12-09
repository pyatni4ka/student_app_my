"""
Модели для работы с пользователями
"""

from enum import Enum
from typing import Optional

from sqlalchemy import Column, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.orm import validates

from .base import Base


class UserRole(str, Enum):
    """Роли пользователей"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    """Модель пользователя"""

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    group = Column(String(10), nullable=True)  # Только для студентов
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    email = Column(String(120), unique=True, nullable=True)
    avatar = Column(Text, nullable=True)  # URL или путь к файлу аватара

    @validates('email')
    def validate_email(self, key: str, email: Optional[str]) -> Optional[str]:
        """Проверяет корректность email"""
        if email is None:
            return None
        if '@' not in email:
            raise ValueError("Некорректный email адрес")
        return email.lower()

    @validates('username')
    def validate_username(self, key: str, username: str) -> str:
        """Проверяет корректность имени пользователя"""
        if len(username) < 3:
            raise ValueError("Имя пользователя должно содержать минимум 3 символа")
        return username.lower()

    @validates('group')
    def validate_group(self, key: str, group: Optional[str]) -> Optional[str]:
        """Проверяет корректность номера группы"""
        if self.role == UserRole.STUDENT and not group:
            raise ValueError("Для студента обязательно нужно указать группу")
        if group and len(group) > 10:
            raise ValueError("Слишком длинный номер группы")
        return group
