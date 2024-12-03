"""
Модуль для обеспечения совместимости с преподавательской версией.
"""
import os
import sys
from pathlib import Path

# Добавляем путь к основному проекту в PYTHONPATH
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Импортируем общий модуль совместимости
from src.core.compatibility import (
    get_shared_database_path,
    get_shared_resources_path,
    ensure_student_access,
    get_version_info
)

def check_compatibility():
    """Проверяет совместимость версий."""
    version_info = get_version_info()
    if not version_info['compatibility']:
        raise RuntimeError("Несовместимая версия приложения")
    
    database_path = get_shared_database_path()
    if not ensure_student_access(f'sqlite:///{database_path}'):
        raise RuntimeError("Нет доступа к базе данных")
