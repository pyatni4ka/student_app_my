"""
This module contains style definitions for the application's UI elements.
"""

STYLES = """
QMainWindow {
    background-color: #FFFFFF;
}

#left-panel {
    background-color: #003153;
    min-width: 400px;
}

#right-panel {
    background-color: #FFFFFF;
    min-width: 400px;
}

#form-container {
    background-color: #FFFFFF;
    border: 2px solid #2196F3;
    border-radius: 8px;
    padding: 20px;
}

QLabel {
    color: #333333;
    font-family: 'Segoe UI';
    font-size: 14px;
    padding: 5px;
}

#app-title {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: bold;
    padding: 10px;
}

#app-subtitle {
    color: #FFFFFF;
    font-size: 22px;
    padding: 5px;
}

#description {
    color: #FFFFFF;
    font-size: 18px;
    padding: 5px;
}

QLineEdit {
    border: 2px solid #CCCCCC;
    border-radius: 4px;
    padding: 8px;
    margin: 5px;
    font-size: 14px;
    background-color: #FFFFFF;
}

QLineEdit:focus {
    border: 2px solid #2196F3;
    background-color: #E3F2FD;
}

QPushButton {
    padding: 10px 20px;
    border-radius: 4px;
    font-size: 16px;
    margin: 5px;
    min-height: 40px;
}

#primary-button {
    background-color: #2196F3;
    color: white;
    border: none;
}

#primary-button:hover {
    background-color: #1976D2;
}

#secondary-button {
    background-color: white;
    color: #2196F3;
    border: 2px solid #2196F3;
}

#secondary-button:hover {
    background-color: #E3F2FD;
}

#error-message {
    color: #F44336;
    font-size: 12px;
    padding: 2px 5px;
}

#year-label {
    color: #666666;
    font-size: 12px;
    padding: 5px;
    margin-top: 10px;
}
"""

def apply_global_styles():
    """Применение глобальных стилей к приложению"""
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        app.setStyleSheet(STYLES)
