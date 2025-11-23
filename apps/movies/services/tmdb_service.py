"""
TMDb API service for fetching movie data.
"""
import os
import requests
from django.conf import settings
from django.core.cache import cache
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TMDbService:
    """Service for interacting with TMDb API."""

    def __init__(self):
        self.api_key = os.environ.get('TMDB_API_KEY') or settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL.rstrip('/')  # Ensure no trailing slash
        
        # Debug log to verify API key is loaded (masking part of the key for security)
        if self.api_key:
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if len(self.api_key) > 8 else "[invalid]"
            logger.debug(f"TMDb API key loaded: {masked_key}")
            logger.debug(f"TMDb Base URL: {self.base_url}")
        else:
            logger.error("TMDb API key is not set!")
        self.timeout = 10

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to TMDb API.
        
        Args:
            endpoint: API endpoint (e.g., 'movie/popular')
            params: Query parameters
            
        Returns:
            Response data as dict
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if params is None:
            params = {}
        
        # Always include the API key
        params['api_key'] = self.api_key
        
        # Construct the URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making request to {url} with params: {params}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            raise  # Re-raise the exception to be handled by the view

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

    def get_trending_movies(self, page: int = 1, time_window: str = 'day') -> Dict:
        """
        Get trending movies.
        
        Args:
            page: Page number
            time_window: 'day' or 'week'
            
        Returns:
            Trending movies data
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if time_window not in ['day', 'week']:
            time_window = 'day'
            
        return self._make_request(f'trending/movie/{time_window}', {'page': page})

    def get_popular_movies(self, page: int = 1) -> Dict:
        """
        Get popular movies.
        
        Args:
            page: Page number
            
        Returns:
            Popular movies data
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        return self._make_request('movie/popular', {'page': page})

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

    def search_movies(self, query: str, page: int = 1) -> Dict:
        """
        Search movies by query.
        
        Args:
            query: Search query
            page: Page number
            
        Returns:
            Search results
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if not query or not query.strip():
            return {
                'page': 1,
                'results': [],
                'total_pages': 0,
                'total_results': 0
            }
            
        return self._make_request('search/movie', {'query': query, 'page': page})

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

