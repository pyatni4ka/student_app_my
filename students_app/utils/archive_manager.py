"""Модуль для работы с архивом"""
import json
import os
import gzip
import pickle
from datetime import datetime, timedelta

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

    def archive_with_compression(self, data, compress_level=6):
        """Архивация с сжатием"""
        serialized = pickle.dumps(data)
        compressed = gzip.compress(serialized, compress_level)
        
        archive_record = {
            "data": compressed,
            "timestamp": datetime.now().isoformat(),
            "compressed": True
        }
        self.archived_data.append(archive_record)
        self.save_archive()

    def get_recent_archives(self, days=30):
        """Получение архивов за последний период"""
        threshold = datetime.now() - timedelta(days=days)
        return [
            item for item in self.archived_data
            if datetime.fromisoformat(item["archive_date"]) > threshold
        ]

    def cleanup_old_archives(self, days=90):
        """Очистка старых архивов"""
        threshold = datetime.now() - timedelta(days=days)
        self.archived_data = [
            item for item in self.archived_data
            if datetime.fromisoformat(item["archive_date"]) > threshold
        ]
        self.save_archive()
