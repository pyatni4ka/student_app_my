"""Модуль для работы с архивом"""
import json
import os
from datetime import datetime

class ArchiveManager:
    """Менеджер архива"""
    def __init__(self, archive_file="archive.json"):
        self.archive_file = archive_file
        self.archived_data = self.load_archive()
    
    def load_archive(self):
        """Загрузка архива из файла"""
        if os.path.exists(self.archive_file):
            try:
                with open(self.archive_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def save_archive(self):
        """Сохранение архива в файл"""
        with open(self.archive_file, 'w', encoding='utf-8') as f:
            json.dump(self.archived_data, f, ensure_ascii=False, indent=2)
    
    def archive_items(self, items):
        """Архивация элементов"""
        archive_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for item in items:
            archived_item = {
                "data": item,
                "archive_date": archive_date
            }
            self.archived_data.append(archived_item)
        self.save_archive()
    
    def get_archived_items(self):
        """Получение архивированных элементов"""
        return self.archived_data
