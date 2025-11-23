"""
Utility functions for the application.
"""
from django.core.cache import cache
from functools import wraps
import hashlib
import json


def cache_result(timeout=300, key_prefix=''):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_parts = [key_prefix, func.__name__]
            cache_key_parts.extend([str(arg) for arg in args])
            cache_key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = hashlib.md5('|'.join(cache_key_parts).encode()).hexdigest()
            full_cache_key = f"{key_prefix}:{func.__name__}:{cache_key}" if key_prefix else f"{func.__name__}:{cache_key}"
            
            # Try to get from cache
            result = cache.get(full_cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(full_cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def generate_cache_key(prefix, *args, **kwargs):
    """
    Generate a cache key from a prefix and arguments.
    
    Args:
        prefix: Key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        str: Generated cache key
    """
    key_parts = [prefix]
    key_parts.extend([str(arg) for arg in args])
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    key_string = '|'.join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern.
    Note: This requires Redis and may not work with all cache backends.
    
    Args:
        pattern: Cache key pattern to match (e.g., 'user:*')
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        keys = redis_conn.keys(pattern)
        if keys:
            redis_conn.delete(*keys)
    except Exception:
        # If Redis is not available or pattern matching fails, silently continue
        pass

