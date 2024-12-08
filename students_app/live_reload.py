"""Live reload для разработки с улучшенной обработкой ошибок"""

import os
import sys
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from main import LoginWindow

class AppReloader(FileSystemEventHandler):
    """Перезагрузчик приложения с сохранением состояния"""
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        self.window = None
        self.last_reload = 0
        self.reload_cooldown = 1.0  # Минимальный интервал между перезагрузками в секундах
        self.create_window()

    def create_window(self):
        """Создание окна с сохранением состояния"""
        try:
            old_state = None
            if self.window:
                # Сохраняем текущее состояние
                old_state = {
                    'surname': self.window.surname_input.text(),
                    'name': self.window.name_input.text(),
                    'group': self.window.group_input.text()
                }
                self.window.close()

            self.window = LoginWindow()
            
            # Восстанавливаем состояние
            if old_state:
                self.window.surname_input.setText(old_state['surname'])
                self.window.name_input.setText(old_state['name'])
                self.window.group_input.setText(old_state['group'])
            
            self.window.show()
            
        except Exception as e:
            self.show_error(f"Ошибка при создании окна: {str(e)}")

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        QMessageBox.critical(None, "Ошибка", message)

    def show_reload_notification(self):
        """Показать уведомление о перезагрузке"""
        if self.window:
            self.window.setStyleSheet("background-color: rgba(200, 200, 200, 0.3);")
            QTimer.singleShot(500, lambda: self.window.setStyleSheet(""))

    def on_modified(self, event):
        """Обработчик изменения файлов с защитой от частых перезагрузок"""
        current_time = time.time()
        if current_time - self.last_reload < self.reload_cooldown:
            return

        if event.src_path.endswith('.py'):
            # Игнорируем временные файлы Python
            filename = Path(event.src_path).name
            if filename.startswith('.') or filename.endswith('.pyc'):
                return

            print(f"\nИзменен файл: {event.src_path}")
            print("Перезагрузка приложения...")
            
            try:
                self.show_reload_notification()
                self.create_window()
                self.last_reload = current_time
            except Exception as e:
                self.show_error(f"Ошибка при перезагрузке: {str(e)}")

def main():
    """Точка входа"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    path = os.path.dirname(os.path.abspath(__file__))
    
    # Создаем перезагрузчик
    reloader = AppReloader()
    
    # Настраиваем наблюдателя
    observer = Observer()
    observer.schedule(reloader, path, recursive=True)
    observer.start()
    
    try:
        print("Запущен режим разработки с автоматической перезагрузкой...")
        print(f"Отслеживаются изменения в директории: {path}")
        reloader.app.exec_()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
