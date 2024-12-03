from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt

class BaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_styles()
        
    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.Window |
                          Qt.WindowType.CustomizeWindowHint |
                          Qt.WindowType.WindowCloseButtonHint |
                          Qt.WindowType.WindowMinimizeButtonHint |
                          Qt.WindowType.WindowMaximizeButtonHint)
        
    def load_styles(self):
        try:
            with open('styles/main.qss', 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading styles: {e}")
            
    def show_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)
        
    def show_warning(self, title: str, message: str):
        QMessageBox.warning(self, title, message)
        
    def show_info(self, title: str, message: str):
        QMessageBox.information(self, title, message)
