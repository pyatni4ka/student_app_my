from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    group = Column(String, nullable=False)
    admission_year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    test_results = relationship("TestResult", back_populates="student")
    time_statistics = relationship("TimeStatistic", back_populates="student")

class LabWork(Base):
    __tablename__ = 'lab_works'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    questions = relationship("Question", back_populates="lab_work")
    test_results = relationship("TestResult", back_populates="lab_work")

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    lab_work_id = Column(Integer, ForeignKey('lab_works.id'))
    question_type = Column(String, nullable=False)  # theory, practice, graphic
    text = Column(String, nullable=False)
    options = Column(String, nullable=False)  # JSON string of options
    correct_answer = Column(Integer, nullable=False)
    image_path = Column(String)  # Путь к изображению
    created_at = Column(DateTime, default=datetime.utcnow)
    
    lab_work = relationship("LabWork", back_populates="questions")
    time_statistics = relationship("TimeStatistic", back_populates="question")
    skipped_questions = relationship("SkippedQuestion", back_populates="question")

class TestResult(Base):
    __tablename__ = 'test_results'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    lab_work_id = Column(Integer, ForeignKey('lab_works.id'))
    score = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="test_results")
    lab_work = relationship("LabWork", back_populates="test_results")
    answers = relationship("StudentAnswer", back_populates="test_result")
    skipped_questions = relationship("SkippedQuestion", back_populates="test_result")

class StudentAnswer(Base):
    __tablename__ = 'student_answers'

    id = Column(Integer, primary_key=True)
    test_result_id = Column(Integer, ForeignKey('test_results.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    given_answer = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    test_result = relationship("TestResult", back_populates="answers")
    question = relationship("Question")

class TimeStatistic(Base):
    __tablename__ = 'time_statistics'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    lab_work_id = Column(Integer, ForeignKey('lab_works.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    time_spent = Column(Integer, nullable=False)  # время в секундах
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="time_statistics")
    question = relationship("Question", back_populates="time_statistics")

class SkippedQuestion(Base):
    __tablename__ = 'skipped_questions'

    id = Column(Integer, primary_key=True)
    test_result_id = Column(Integer, ForeignKey('test_results.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    is_answered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_result = relationship("TestResult", back_populates="skipped_questions")
    question = relationship("Question", back_populates="skipped_questions")
