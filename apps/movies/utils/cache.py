from functools import wraps
from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework.request import Request
from rest_framework.response import Response

def cache_page_on_auth(anon_timeout: int, auth_timeout: int = None):
    """
    Decorator that caches a view with different timeouts for authenticated and anonymous users.
    Works with both class-based and function-based views.
    """
    if auth_timeout is None:
        auth_timeout = max(60, anon_timeout // 3)  # At least 1 minute for auth users

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_or_request, *args, **kwargs):
            # Handle class-based views (self is first argument)
            if hasattr(view_or_request, 'request'):
                view = view_or_request
                request = view.request
                is_class_based = True
            else:
                # Handle function-based views (request is first argument)
                request = view_or_request
                view = None
                is_class_based = False

            # Generate cache key
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 'anon'
            path = request.get_full_path()
            cache_key = f'view_cache:{user_id}:{path}'

            # Check cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)

            # Call the view
            if is_class_based:
                response = view_func(view, *args, **kwargs)
            else:
                response = view_func(request, *args, **kwargs)

            # Cache the response data
            if hasattr(response, 'data') and response.status_code == 200:
                timeout = auth_timeout if hasattr(request, 'user') and request.user.is_authenticated else anon_timeout
                cache.set(cache_key, response.data, timeout)

            return response

        return _wrapped_view
    return decorator

def method_cache_page_on_auth(anon_timeout: int, auth_timeout: int = None):
    """
    Method decorator version of cache_page_on_auth for class-based views.
    """
    def decorator(method):
        return method_decorator(cache_page_on_auth(anon_timeout, auth_timeout))(method)
    return decorator

def get_cache_key(prefix: str, *args) -> str:
    """
    Generate a cache key from a prefix and arguments.
    
    Args:
        prefix: Cache key prefix
        *args: Additional parts to include in the key
        
    Returns:
        str: Generated cache key
    """
    key_parts = [str(prefix)] + [str(arg) for arg in args]
    return ":".join(key_parts)

def cache_movie_data(movie_id: int, data: dict, timeout: int = None):
    """
    Cache movie data.
    
    Args:
        movie_id: Movie ID
        data: Data to cache
        timeout: Cache timeout in seconds (default: None, use default timeout)
    """
    cache_key = get_cache_key("movie", movie_id)
    cache.set(cache_key, data, timeout)

def get_cached_movie_data(movie_id: int) -> dict:
    """
    Get cached movie data.
    
    Args:
        movie_id: Movie ID
        
    Returns:
        dict: Cached movie data or None if not found
    """
    cache_key = get_cache_key("movie", movie_id)
    return cache.get(cache_key)

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
        except ImportError:
            # Fallback to simple cache if redis is not available
            pass

def cached_result(timeout: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = get_cache_key(func.__name__, *args, *[f"{k}={v}" for k, v in kwargs.items()])
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator