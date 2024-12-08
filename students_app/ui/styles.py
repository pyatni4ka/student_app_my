"""Стили приложения"""

STYLES = """
* {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

QMainWindow {
    background-color: white;
}

#header {
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    min-height: 30px;
}

#year-label {
    color: #333333;
    font-size: 14px;
    font-weight: normal;
    margin: 10px 0;
    qproperty-alignment: AlignRight;
}

#left-panel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                              stop:0 #2962FF, stop:1 #1565C0);
    border-top-left-radius: 25px;
    border-bottom-left-radius: 25px;
    padding: 40px;
    min-width: 450px;
}

#logo {
    margin-bottom: 30px;
}

#title-label {
    color: white;
    font-size: 36px;
    font-weight: bold;
    margin: 30px 0 15px 0;
    qproperty-alignment: AlignCenter;
    letter-spacing: 0.5px;
}

#subtitle-label {
    color: white;
    font-size: 26px;
    margin: 15px 0;
    qproperty-alignment: AlignCenter;
    opacity: 0.95;
    letter-spacing: 0.3px;
}

#welcome-label {
    color: white;
    font-size: 16px;
    margin: 25px 0;
    qproperty-alignment: AlignCenter;
    line-height: 1.8;
    opacity: 0.9;
    letter-spacing: 0.2px;
}

#right-panel {
    background-color: white;
    border-top-right-radius: 25px;
    border-bottom-right-radius: 25px;
    padding: 60px;
}

#input-label {
    font-size: 14px;
    color: #202124;
    font-weight: 500;
    margin: 10px 0 2px 5px;
}

QLineEdit {
    border: 2px solid #E3E3E3;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 16px;
    background-color: white;
    margin: 0;
    color: #202124;
}

QLineEdit:hover {
    border-color: #2962FF;
}

QLineEdit:focus {
    border-color: #2962FF;
    background-color: #F5F5F5;
}

QPushButton {
    background-color: #2962FF;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 30px;
    font-size: 16px;
    font-weight: bold;
    margin: 25px 0 15px 0;
    min-width: 200px;
}

QPushButton:hover {
    background-color: #1565C0;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

#teacher-button {
    background-color: transparent;
    color: #2962FF;
    border: 2px solid #2962FF;
    border-radius: 12px;
    padding: 10px 25px;
    font-size: 15px;
    margin: 5px 0;
    min-width: 200px;
}

#teacher-button:hover {
    background-color: rgba(41, 98, 255, 0.1);
}

#teacher-button:pressed {
    background-color: rgba(41, 98, 255, 0.2);
}

#error-label {
    color: #D32F2F;
    font-size: 13px;
    margin: 0 0 5px 10px;
    min-height: 18px;
    letter-spacing: 0.2px;
}

QLabel[accessibleName="icon"] {
    margin-right: 8px;
}

.error {
    border-color: #D32F2F;
}

/* Стили для окна преподавателя */
#logo-small {
    margin: 0 10px;
}

#header-title {
    font-size: 20px;
    font-weight: 500;
    color: #202124;
}

#search-label {
    font-size: 14px;
    color: #202124;
    font-weight: 500;
}

#search-input {
    padding: 8px 12px;
    border: 1px solid #dadce0;
    border-radius: 4px;
    font-size: 14px;
    background: white;
}

#search-input:focus {
    border-color: #1a73e8;
    outline: none;
}

#results-table {
    border: 1px solid #dadce0;
    border-radius: 4px;
    background: white;
}

#results-table QHeaderView::section {
    background-color: #f8f9fa;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #dadce0;
    font-weight: 500;
    color: #202124;
}

#results-table::item {
    padding: 8px;
    border: none;
}

#results-table::item:selected {
    background-color: #e8f0fe;
    color: #202124;
}

#action-button {
    background-color: #1a73e8;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
}

#action-button:hover {
    background-color: #1557b0;
}

#logout-button {
    background-color: #f8f9fa;
    color: #202124;
    border: 1px solid #dadce0;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
}

#logout-button:hover {
    background-color: #f1f3f4;
}

#input-container {
    background-color: #f8f9fa;
    border: 1px solid #dadce0;
    border-radius: 4px;
    min-height: 40px;
}

#input-container:focus-within {
    border-color: #1a73e8;
    background-color: white;
}

#password-input {
    color: #202124;
}

#password-input::placeholder {
    color: #5f6368;
}

#login-button {
    background-color: #1a73e8;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.5px;
}

#login-button:hover {
    background-color: #1557b0;
}

#login-button:pressed {
    background-color: #174ea6;
}
"""
