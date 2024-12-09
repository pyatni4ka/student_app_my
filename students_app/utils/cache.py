"""
Утилиты для кэширования
"""
from typing import Callable, TypeVar
from functools import wraps
from cachetools import TTLCache, LRUCache

T = TypeVar('T')

# Глобальные кэши
method_cache = TTLCache(maxsize=100, ttl=300)  # TTL = 5 минут
lru_cache = LRUCache(maxsize=1000)

def cache_method(ttl: int = 300) -> Callable:
    """
    Декоратор для кэширования методов класса

    Args:
        ttl: Время жизни кэша в секундах
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            # Создаем ключ кэша из имени класса, метода и аргументов
            cache_key = (
                self.__class__.__name__,
                func.__name__,
                args,
                frozenset(kwargs.items())
            )

            # Проверяем кэш
            cached_value = method_cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Вычисляем значение и кэшируем
            result = func(self, *args, **kwargs)
            method_cache[cache_key] = result
            return result
        return wrapper
    return decorator

def lru_cache_method(maxsize: int = 128) -> Callable:
    """
    Декоратор для LRU кэширования методов класса

    Args:
        maxsize: Максимальный размер кэша
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            cache_key = (
                self.__class__.__name__,
                func.__name__,
                args,
                frozenset(kwargs.items())
            )

            cached_value = lru_cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            result = func(self, *args, **kwargs)
            lru_cache[cache_key] = result
            return result
        return wrapper
    return decorator

def clear_cache():
    """Очищает все кэши"""
    method_cache.clear()
    lru_cache.clear()

def get_cache_stats() -> dict:
    """Возвращает статистику кэша"""
    return {
        'method_cache': {
            'size': len(method_cache),
            'maxsize': method_cache.maxsize,
            'ttl': method_cache.ttl,
        },
        'lru_cache': {
            'size': len(lru_cache),
            'maxsize': lru_cache.maxsize,
        }
    }
