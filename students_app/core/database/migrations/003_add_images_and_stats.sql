-- Добавление поддержки изображений в вопросах
ALTER TABLE questions ADD COLUMN image_path TEXT;

-- Добавление таблицы для статистики времени
CREATE TABLE IF NOT EXISTS time_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    lab_work_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    time_spent INTEGER NOT NULL, -- время в секундах
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (lab_work_id) REFERENCES lab_works(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Добавление таблицы для отслеживания пропущенных вопросов
CREATE TABLE IF NOT EXISTS skipped_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_result_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    is_answered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_result_id) REFERENCES test_results(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);
