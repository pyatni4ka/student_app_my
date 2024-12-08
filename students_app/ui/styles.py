"""Стили для приложения"""

STYLES = """
QMainWindow {
    background-color: #f5f5f5;
}

#left-panel {
    background-color: #003366;
    min-width: 500px;
    padding: 20px;
    border-right: 1px solid #e0e0e0;
}

#right-panel {
    background-color: white;
    min-width: 500px;
    padding: 20px;
}

#logo {
    margin-bottom: 30px;
}

#title-label {
    color: white;
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 10px;
}

#subtitle-label {
    color: #b3d9ff;
    font-size: 24px;
    margin-bottom: 20px;
}

#welcome-label {
    color: #e6f2ff;
    font-size: 18px;
    line-height: 1.5;
}

#input-label {
    color: #333333;
    font-size: 18px;
    font-weight: 500;
    margin-top: 15px;
    margin-bottom: 8px;
}

QLineEdit {
    padding: 15px 15px 15px 45px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background-color: white;
    font-size: 16px;
    color: #333333;
    min-height: 25px;
}

QLineEdit::placeholder {
    color: #6c757d;
    font-size: 16px;
    font-weight: 400;
}

QLineEdit:focus {
    border-color: #2196F3;
    background-color: white;
}

QLineEdit:hover {
    border-color: #90CAF9;
    background-color: white;
}

QPushButton {
    padding: 15px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
    min-width: 150px;
    margin-top: 20px;
}

#login-button {
    background-color: #2196F3;
    color: white;
}

#login-button:hover {
    background-color: #1976D2;
}

#login-button:pressed {
    background-color: #0D47A1;
}

#teacher-button {
    background-color: #f8f9fa;
    color: #333333;
    border: 2px solid #e0e0e0;
}

#teacher-button:hover {
    background-color: #e9ecef;
}

#teacher-button:pressed {
    background-color: #dee2e6;
}

#error-label {
    color: #dc3545;
    font-size: 13px;
    min-height: 20px;
    padding: 4px 0;
}

#year-label {
    color: #6c757d;
    font-size: 14px;
    margin-top: 30px;
}

#form-widget {
    background-color: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

#icon {
    margin: 0 8px;
    min-width: 32px;
}

.input-container {
    position: relative;
    margin-bottom: 20px;
}
"""
