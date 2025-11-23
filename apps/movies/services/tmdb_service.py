"""
TMDb API service for fetching movie data.
"""
import requests
from django.conf import settings
from django.core.cache import cache
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TMDbService:
    """Service for interacting with TMDb API."""

    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.timeout = 10

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Make a request to TMDb API.
        
        Args:
            endpoint: API endpoint (e.g., '/movie/popular')
            params: Query parameters
            
        Returns:
            Response data as dict or None if error
        """
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request failed: {e}")
            return None

    def _get_cached_or_fetch(self, cache_key: str, fetch_func, timeout: int = 600) -> Optional[Dict]:
        """
        Get data from cache or fetch from API.
        
        Args:
            cache_key: Cache key
            fetch_func: Function to fetch data if not cached
            timeout: Cache timeout in seconds
            
        Returns:
            Cached or fetched data
        """
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        data = fetch_func()
        if data:
            cache.set(cache_key, data, timeout)
        return data

    def get_trending_movies(self, page: int = 1, time_window: str = 'day') -> Optional[Dict]:
        """
        Get trending movies.
        
        Args:
            page: Page number
            time_window: 'day' or 'week'
            
        Returns:
            Trending movies data
        """
        cache_key = f"tmdb:trending:{time_window}:page:{page}"
        
        def fetch():
            return self._make_request('/trending/movie/day', {'page': page})
        
        return self._get_cached_or_fetch(cache_key, fetch, timeout=600)  # 10 minutes

    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """
        Get popular movies.
        
        Args:
            page: Page number
            
        Returns:
            Popular movies data
        """
        cache_key = f"tmdb:popular:page:{page}"
        
        def fetch():
            return self._make_request('/movie/popular', {'page': page})
        
        return self._get_cached_or_fetch(cache_key, fetch, timeout=600)  # 10 minutes

    def get_top_rated_movies(self, page: int = 1) -> Optional[Dict]:
        """
        Get top-rated movies.
        
        Args:
            page: Page number
            
        Returns:
            Top-rated movies data
        """
        cache_key = f"tmdb:top_rated:page:{page}"
        
        def fetch():
            return self._make_request('/movie/top_rated', {'page': page})
        
        return self._get_cached_or_fetch(cache_key, fetch, timeout=600)  # 10 minutes

    def get_upcoming_movies(self, page: int = 1) -> Optional[Dict]:
        """
        Get upcoming movies.
        
        Args:
            page: Page number
            
        Returns:
            Upcoming movies data
        """
        cache_key = f"tmdb:upcoming:page:{page}"
        
        def fetch():
            return self._make_request('/movie/upcoming', {'page': page})
        
        return self._get_cached_or_fetch(cache_key, fetch, timeout=600)  # 10 minutes

    def search_movies(self, query: str, page: int = 1) -> Optional[Dict]:
        """
        Search movies by query.
        
        Args:
            query: Search query
            page: Page number
            
        Returns:
            Search results
        """
        cache_key = f"tmdb:search:{query.lower()}:page:{page}"
        
        def fetch():
            return self._make_request('/search/movie', {'query': query, 'page': page})
        
        return self._get_cached_or_fetch(cache_key, fetch, timeout=300)  # 5 minutes

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """
        Get detailed movie information.
        
        Args:
            movie_id: TMDb movie ID
            
        Returns:
            Movie details
        """
        cache_key = f"tmdb:movie:{movie_id}"
        
        def fetch():
            return self._make_request(f'/movie/{movie_id}')
        
        return self._get_cached_or_fetch(cache_key, fetch, timeout=3600)  # 1 hour

    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """
        Get movie recommendations based on a movie.
        
        Args:
            movie_id: TMDb movie ID
            page: Page number
            
        Returns:
            Recommended movies
        """
        cache_key = f"tmdb:recommendations:{movie_id}:page:{page}"
        
        def fetch():
            return self._make_request(f'/movie/{movie_id}/recommendations', {'page': page})
        
        return self._get_cached_or_fetch(cache_key, fetch, timeout=600)  # 10 minutes

