"""
Cache utilities for movies app.
"""
from django.core.cache import cache
from typing import Optional, Callable
import hashlib
import json


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from prefix and arguments.
    
    Args:
        prefix: Key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Generated cache key
    """
    key_parts = [prefix]
    key_parts.extend([str(arg) for arg in args])
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    key_string = '|'.join(key_parts)
    return f"movies:{hashlib.md5(key_string.encode()).hexdigest()}"


def cache_movie_data(key: str, data: dict, timeout: int = 3600):
    """
    Cache movie data.
    
    Args:
        key: Cache key
        data: Data to cache
        timeout: Cache timeout in seconds
    """
    cache.set(key, data, timeout)


def get_cached_movie_data(key: str) -> Optional[dict]:
    """
    Get cached movie data.
    
    Args:
        key: Cache key
        
    Returns:
        Cached data or None
    """
    return cache.get(key)


def invalidate_user_cache(user_id: int):
    """
    Invalidate all cache entries for a user.
    
    Args:
        user_id: User ID
    """
    patterns = [
        f"movies:user:{user_id}:*",
        f"movies:recommendations:{user_id}:*",
        f"movies:favorites:{user_id}:*",
    ]
    
    for pattern in patterns:
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            keys = redis_conn.keys(pattern)
            if keys:
                redis_conn.delete(*keys)
        except Exception:
            # If Redis pattern matching fails, silently continue
            pass


def cached_result(timeout: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = get_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

