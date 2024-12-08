"""
Модели для работы с тестами
"""

from enum import Enum
from typing import List

from sqlalchemy import (Column, Enum as SQLEnum, ForeignKey, Integer, String,
                       Text, Float)
from sqlalchemy.orm import relationship

from .base import Base


class QuestionType(str, Enum):
    """Типы вопросов"""
    SINGLE_CHOICE = "single_choice"  # Один правильный ответ
    MULTIPLE_CHOICE = "multiple_choice"  # Несколько правильных ответов
    TEXT = "text"  # Текстовый ответ
    NUMERIC = "numeric"  # Числовой ответ с погрешностью


class Test(Base):
    """Модель теста"""
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    passing_score = Column(Float, nullable=False, default=60.0)  # Процент для сдачи
    
    # Отношения
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    attempts = relationship("TestAttempt", back_populates="test", cascade="all, delete-orphan")


class Question(Base):
    """Модель вопроса"""
    
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('test.id'), nullable=False)
    text = Column(Text, nullable=False)
    type = Column(SQLEnum(QuestionType), nullable=False)
    points = Column(Float, nullable=False, default=1.0)
    
    # Для числовых вопросов
    correct_numeric_answer = Column(Float, nullable=True)
    numeric_tolerance = Column(Float, nullable=True)  # Допустимая погрешность
    
    # Отношения
    test = relationship("Test", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base):
    """Модель варианта ответа"""
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('question.id'), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    
    # Отношения
    question = relationship("Question", back_populates="options")


class TestAttempt(Base):
    """Модель попытки прохождения теста"""
    
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('test.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    score = Column(Float, nullable=True)  # Итоговый балл
    
    # Отношения
    test = relationship("Test", back_populates="attempts")
    user = relationship("User", backref="test_attempts")
    answers = relationship("UserAnswer", back_populates="attempt", cascade="all, delete-orphan")


class UserAnswer(Base):
    """Модель ответа пользователя"""
    
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey('testattempt.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('question.id'), nullable=False)
    
    # Для вопросов с выбором
    selected_options = Column(ARRAY(Integer), nullable=True)  # ID выбранных вариантов
    
    # Для текстовых и числовых вопросов
    text_answer = Column(Text, nullable=True)
    numeric_answer = Column(Float, nullable=True)
    
    points_earned = Column(Float, nullable=True)  # Заработанные баллы
    
    # Отношения
    attempt = relationship("TestAttempt", back_populates="answers")
    question = relationship("Question")
