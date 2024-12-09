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

#form-container {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
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
}

#error-message {
    color: #dc3545;
    font-size: 14px;
    margin-top: 5px;
}

QLabel {
    color: #333333;
    font-size: 16px;
    margin-bottom: 5px;
}

QLineEdit {
    padding: 12px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background-color: white;
    font-size: 16px;
    color: #333333;
    min-height: 25px;
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
    margin: 5px;
}

#primary-button {
    background-color: #2196F3;
    color: white;
}

#primary-button:hover {
    background-color: #1976D2;
}

#primary-button:pressed {
    background-color: #0D47A1;
}

#secondary-button {
    background-color: #f8f9fa;
    color: #2196F3;
    border: 2px solid #2196F3;
}

#secondary-button:hover {
    background-color: #e9ecef;
}

#secondary-button:pressed {
    background-color: #dee2e6;
}

QListWidget {
    border: 1px solid #ccc;
    border-radius: 8px;
    background-color: #ffffff;
    padding: 15px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 14px;
    color: #333;
}

QListWidget::item {
    margin: 10px 0;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    background-color: #f9f9f9;
    transition: background-color 0.3s, box-shadow 0.3s;
}

QListWidget::item:hover {
    background-color: #e0f7fa;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

QListWidget::item:selected {
    background-color: #00acc1;
    border-color: #00838f;
    color: #fff;
}

QLabel {
    color: #2c3e50;
    font-family: Arial;
    font-size: 12pt;
}
QLabel.lab_title {
    font-weight: bold;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 12pt;
    font-family: Arial;
}
QPushButton:hover {
    background-color: #2980b9;
}
"""

LIST_WIDGET_STYLE = """
QListWidget {
    border: 1px solid #ccc;
    border-radius: 8px;
    background-color: #ffffff;
    padding: 15px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 14px;
    color: #333;
}

QListWidget::item {
    margin: 10px 0;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    background-color: #f9f9f9;
    transition: background-color 0.3s, box-shadow 0.3s;
}

QListWidget::item:hover {
    background-color: #e0f7fa;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

QListWidget::item:selected {
    background-color: #00acc1;
    border-color: #00838f;
    color: #fff;
}
"""

ITEM_LABEL_STYLE = """
QLabel {
    color: #2c3e50;
    font-family: Arial;
    font-size: 12pt;
}
QLabel.lab_title {
    font-weight: bold;
}
"""

BUTTON_STYLE = """
QPushButton {
    background-color: #3498db;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 12pt;
    font-family: Arial;
}
QPushButton:hover {
    background-color: #2980b9;
}
"""
