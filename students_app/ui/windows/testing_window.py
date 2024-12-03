from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QRadioButton, QPushButton,
                             QButtonGroup, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime
from ..base_window import BaseWindow
from core.database.manager import DatabaseManager
from .results_window import ResultsWindow

class TestingWindow(BaseWindow):
    def __init__(self, student, lab):
        self.student = student
        self.lab = lab
        self.db = DatabaseManager()
        self.current_question = 0
        self.answers = []
        self.remaining_time = 20 * 60  # 20 минут в секундах
        self.start_time = datetime.now()
        super().__init__()

    def setup_ui(self):
        self.setWindowTitle(f'Тестирование - {self.lab.name}')
        self.setGeometry(100, 100, 800, 600)

        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Верхняя панель с информацией
        top_panel = QFrame()
        top_panel.setObjectName('topPanel')
        top_layout = QHBoxLayout(top_panel)

        # Таймер
        self.timer_label = QLabel('20:00')
        self.timer_label.setObjectName('timer')
        top_layout.addWidget(self.timer_label)

        # Прогресс
        self.progress = QProgressBar()
        self.progress.setRange(0, 5)
        self.progress.setValue(0)
        self.progress.setFormat('Вопрос %v из %m')
        self.progress.setObjectName('progress')
        top_layout.addWidget(self.progress)

        layout.addWidget(top_panel)

        # Область вопроса
        question_frame = QFrame()
        question_frame.setObjectName('questionFrame')
        question_layout = QVBoxLayout(question_frame)

        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setObjectName('questionText')
        question_layout.addWidget(self.question_label)

        # Область для вариантов ответа
        self.answers_frame = QFrame()
        self.answers_frame.setObjectName('answersFrame')
        self.answers_layout = QVBoxLayout(self.answers_frame)
        question_layout.addWidget(self.answers_frame)

        layout.addWidget(question_frame)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.next_btn = QPushButton('Следующий вопрос')
        self.next_btn.setObjectName('primaryButton')
        self.next_btn.clicked.connect(self.next_question)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.next_btn)

        layout.addLayout(buttons_layout)

        # Инициализация
        self.load_questions()
        self.start_timer()

    def load_questions(self):
        try:
            # Получаем случайные вопросы
            theory = self.db.get_random_questions(self.lab.id, 'theory', 2)
            practice = self.db.get_random_questions(self.lab.id, 'practice', 2)
            graphic = self.db.get_random_questions(self.lab.id, 'graphic', 1)
            
            self.questions = theory + practice + graphic
            self.show_question(0)
            
        except Exception as e:
            self.show_error('Ошибка', f'Ошибка при загрузке вопросов: {str(e)}')
            self.close()

    def show_question(self, index):
        # Очищаем предыдущие варианты ответов
        for i in reversed(range(self.answers_layout.count())): 
            self.answers_layout.itemAt(i).widget().setParent(None)
        
        question = self.questions[index]
        self.question_label.setText(f'Вопрос {index + 1}:\n{question.text}')
        
        # Создаем группу для радиокнопок
        self.answer_group = QButtonGroup()
        
        # Создаем варианты ответов
        options = json.loads(question.options)
        for i, option in enumerate(options):
            radio = QRadioButton(option)
            radio.setObjectName('answerOption')
            self.answers_layout.addWidget(radio)
            self.answer_group.addButton(radio, i)
        
        # Обновляем прогресс
        self.progress.setValue(index + 1)

    def next_question(self):
        if not self.answer_group.checkedButton():
            self.show_warning('Предупреждение', 'Выберите вариант ответа!')
            return

        # Сохраняем ответ
        current_question = self.questions[self.current_question]
        answer = {
            'question_id': current_question.id,
            'given_answer': self.answer_group.checkedId(),
            'is_correct': self.answer_group.checkedId() == current_question.correct_answer
        }
        self.answers.append(answer)

        if self.current_question < 4:
            self.current_question += 1
            self.show_question(self.current_question)
            if self.current_question == 4:
                self.next_btn.setText('Завершить тест')
        else:
            self.finish_test()

    def finish_test(self):
        end_time = datetime.now()
        
        try:
            # Подсчет результатов
            correct_answers = sum(1 for a in self.answers if a['is_correct'])
            score = (correct_answers / 5) * 100

            # Сохраняем результат
            test_result = self.db.save_test_result(
                student_id=self.student.id,
                lab_id=self.lab.id,
                score=score,
                start_time=self.start_time,
                end_time=end_time,
                answers=self.answers
            )

            # Открываем окно результатов
            self.results_window = ResultsWindow(self.student, test_result)
            self.results_window.show()
            self.close()
            
        except Exception as e:
            self.show_error('Ошибка', f'Ошибка при сохранении результатов: {str(e)}')

    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def update_timer(self):
        self.remaining_time -= 1
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        
        self.timer_label.setText(f'{minutes:02d}:{seconds:02d}')
        
        if minutes <= 5:
            self.timer_label.setStyleSheet('color: red;')
        
        if self.remaining_time <= 0:
            self.timer.stop()
            self.show_warning('Время вышло', 'Время тестирования закончилось!')
            self.finish_test()

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)
