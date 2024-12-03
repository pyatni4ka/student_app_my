from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Student, LabWork, Question, TestResult, StudentAnswer
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, connection_string="sqlite:///students_app.db"):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_student(self, full_name: str, group: str, admission_year: int) -> Student:
        try:
            student = Student(
                full_name=full_name,
                group=group,
                admission_year=admission_year
            )
            self.session.add(student)
            self.session.commit()
            return student
        except SQLAlchemyError as e:
            logger.error(f"Error adding student: {e}")
            self.session.rollback()
            raise

    def get_available_labs(self) -> list[LabWork]:
        try:
            return self.session.query(LabWork).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting labs: {e}")
            raise

    def get_random_questions(self, lab_id: int, question_type: str, count: int) -> list[Question]:
        try:
            return (self.session.query(Question)
                   .filter(Question.lab_work_id == lab_id,
                          Question.question_type == question_type)
                   .order_by(func.random())
                   .limit(count)
                   .all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting questions: {e}")
            raise

    def save_test_result(self, student_id: int, lab_id: int, 
                        score: float, start_time, end_time,
                        answers: list[dict]) -> TestResult:
        try:
            test_result = TestResult(
                student_id=student_id,
                lab_work_id=lab_id,
                score=score,
                start_time=start_time,
                end_time=end_time
            )
            self.session.add(test_result)
            
            for answer in answers:
                student_answer = StudentAnswer(
                    test_result=test_result,
                    question_id=answer['question_id'],
                    given_answer=answer['given_answer'],
                    is_correct=answer['is_correct']
                )
                self.session.add(student_answer)
            
            self.session.commit()
            return test_result
        except SQLAlchemyError as e:
            logger.error(f"Error saving test result: {e}")
            self.session.rollback()
            raise

    def get_student_results(self, student_id: int) -> list[TestResult]:
        try:
            return (self.session.query(TestResult)
                   .filter(TestResult.student_id == student_id)
                   .order_by(TestResult.created_at.desc())
                   .all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting student results: {e}")
            raise

    def get_all_results(self, group: str = None, lab_id: int = None) -> list[TestResult]:
        try:
            query = self.session.query(TestResult)
            if group:
                query = query.join(Student).filter(Student.group == group)
            if lab_id:
                query = query.filter(TestResult.lab_work_id == lab_id)
            return query.order_by(TestResult.created_at.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all results: {e}")
            raise
