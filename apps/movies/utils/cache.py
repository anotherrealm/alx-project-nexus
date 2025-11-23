"""
Cache utilities for movies app.
"""
from functools import wraps
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from typing import Optional, Callable, Union, Any
import hashlib
import json
from rest_framework.request import Request


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


def cache_page_on_auth(anon_timeout: int, auth_timeout: int = None):
    """
    Decorator that caches a view with different timeouts for authenticated and anonymous users.
    
    Args:
        anon_timeout: Cache timeout in seconds for anonymous users
        auth_timeout: Cache timeout in seconds for authenticated users (defaults to anon_timeout / 3)
        
    Returns:
        Decorated view function
    """
    if auth_timeout is None:
        auth_timeout = max(60, anon_timeout // 3)  # At least 1 minute for auth users
        
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request: Request, *args, **kwargs):
            # Choose timeout based on authentication status
            timeout = auth_timeout if request.user.is_authenticated else anon_timeout
            
            # Generate a cache key based on the request
            path = request.get_full_path()
            user_id = request.user.id if request.user.is_authenticated else 'anon'
            cache_key = f'view_cache::{user_id}:{path}'
            
            # Use Django's cache_page with our calculated timeout and key
            return cache_page(timeout, key_prefix=cache_key)(view_func)(request, *args, **kwargs)
            
        return _wrapped_view
    return decorator


def method_cache_page_on_auth(anon_timeout: int, auth_timeout: int = None):
    """
    Method decorator version of cache_page_on_auth for class-based views.
    """
    def decorator(method):
        return method_decorator(cache_page_on_auth(anon_timeout, auth_timeout), name='dispatch')(method)
    return decorator


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

