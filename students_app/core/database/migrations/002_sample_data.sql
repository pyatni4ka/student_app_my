-- Добавление примера лабораторной работы
INSERT INTO lab_works (name, description) VALUES 
('Лабораторная работа №1', 'Основы программирования на Python'),
('Лабораторная работа №2', 'Алгоритмы и структуры данных');

-- Добавление примеров вопросов для первой лабораторной работы
INSERT INTO questions (lab_work_id, question_type, text, options, correct_answer) VALUES 
-- Теоретические вопросы
(1, 'theory', 'Что такое Python?', 
 '["Компилируемый язык программирования", "Интерпретируемый язык программирования", "Операционная система", "База данных"]', 
 1),
(1, 'theory', 'Какой оператор используется для определения функции в Python?', 
 '["function", "def", "define", "func"]', 
 1),

-- Практические вопросы
(1, 'practice', 'Какой результат выполнения кода: print(2 + 2 * 2)?', 
 '["8", "6", "4", "10"]', 
 1),
(1, 'practice', 'Как получить длину списка my_list в Python?', 
 '["my_list.length()", "my_list.size()", "len(my_list)", "size(my_list)"]', 
 2),

-- Графический вопрос
(1, 'graphic', 'Какой график отображает линейную зависимость?', 
 '["График A", "График B", "График C", "График D"]', 
 0);

-- Добавление примеров вопросов для второй лабораторной работы
INSERT INTO questions (lab_work_id, question_type, text, options, correct_answer) VALUES 
-- Теоретические вопросы
(2, 'theory', 'Что такое алгоритм?', 
 '["Набор данных", "Последовательность действий", "Компьютерная программа", "База данных"]', 
 1),
(2, 'theory', 'Какая сложность алгоритма быстрой сортировки в среднем случае?', 
 '["O(n)", "O(n^2)", "O(n log n)", "O(log n)"]', 
 2),

-- Практические вопросы
(2, 'practice', 'Какой результат работы алгоритма бинарного поиска?', 
 '["Индекс элемента", "Сумма элементов", "Количество элементов", "Среднее значение"]', 
 0),
(2, 'practice', 'Какая структура данных работает по принципу LIFO?', 
 '["Очередь", "Стек", "Список", "Массив"]', 
 1),

-- Графический вопрос
(2, 'graphic', 'Какая диаграмма отображает дерево поиска?', 
 '["Диаграмма A", "Диаграмма B", "Диаграмма C", "Диаграмма D"]', 
 2);
