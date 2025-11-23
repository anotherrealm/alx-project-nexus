"""
Recommendation service for generating personalized movie recommendations.
"""
from typing import List, Dict
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg
from apps.movies.models import Movie, FavoriteMovie
from apps.movies.services.tmdb_service import TMDbService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating personalized movie recommendations."""

    def __init__(self):
        self.tmdb_service = TMDbService()

    def get_user_recommendations(self, user: User, limit: int = 20) -> List[Dict]:
        """
        Get personalized recommendations for a user.
        
        Strategy:
        1. Get user's favorite movies
        2. Extract genres from favorites
        3. Find similar movies based on genres
        4. Exclude already favorited movies
        5. Rank by popularity and rating
        
        Args:
            user: User instance
            limit: Number of recommendations to return
            
        Returns:
            List of recommended movies
        """
        try:
            # Get user's favorite movies
            favorites = FavoriteMovie.objects.filter(user=user).select_related('movie')
            
            if not favorites.exists():
                # If no favorites, return popular movies
                return self._get_popular_fallback(limit)
            
            # Extract genre IDs from favorites
            genre_ids = set()
            favorite_movie_ids = []
            
            for favorite in favorites:
                favorite_movie_ids.append(favorite.movie.tmdb_id)
                genre_ids.update(favorite.movie.genre_ids or [])
            
            if not genre_ids:
                return self._get_popular_fallback(limit)
            
            # Find movies with similar genres, excluding favorites
            recommendations = Movie.objects.filter(
                genre_ids__overlap=list(genre_ids)
            ).exclude(
                tmdb_id__in=favorite_movie_ids
            ).order_by(
                '-popularity',
                '-vote_average'
            )[:limit]
            
            # Convert to dict format
            return [self._movie_to_dict(movie) for movie in recommendations]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._get_popular_fallback(limit)

    def _get_popular_fallback(self, limit: int) -> List[Dict]:
        """
        Get popular movies as fallback recommendations.
        
        Args:
            limit: Number of movies to return
            
        Returns:
            List of popular movies
        """
        movies = Movie.objects.order_by('-popularity', '-vote_average')[:limit]
        return [self._movie_to_dict(movie) for movie in movies]

    def _movie_to_dict(self, movie: Movie) -> Dict:
        """
        Convert Movie instance to dictionary.
        
        Args:
            movie: Movie instance
            
        Returns:
            Movie data as dictionary
        """
        return {
            'id': movie.id,
            'tmdb_id': movie.tmdb_id,
            'title': movie.title,
            'overview': movie.overview,
            'release_date': movie.release_date.isoformat() if movie.release_date else None,
            'poster_path': movie.poster_path,
            'backdrop_path': movie.backdrop_path,
            'vote_average': float(movie.vote_average) if movie.vote_average else None,
            'vote_count': movie.vote_count,
            'popularity': float(movie.popularity) if movie.popularity else None,
            'genre_ids': movie.genre_ids,
            'original_language': movie.original_language,
            'poster_url': movie.full_poster_url,
            'backdrop_url': movie.full_backdrop_url,
        }

    def get_similar_movies(self, movie_id: int, limit: int = 10) -> List[Dict]:
        """
        Get movies similar to a given movie.
        
        Args:
            movie_id: TMDb movie ID
            limit: Number of similar movies to return
            
        Returns:
            List of similar movies
        """
        try:
            # Try to get from TMDb API
            recommendations = self.tmdb_service.get_movie_recommendations(movie_id)
            
            if recommendations and 'results' in recommendations:
                # Convert TMDb results to our format
                return [
                    self._tmdb_result_to_dict(result)
                    for result in recommendations['results'][:limit]
                ]
            
            # Fallback: find movies with similar genres
            try:
                movie = Movie.objects.get(tmdb_id=movie_id)
                similar = Movie.objects.filter(
                    genre_ids__overlap=movie.genre_ids or []
                ).exclude(
                    tmdb_id=movie_id
                ).order_by(
                    '-popularity',
                    '-vote_average'
                )[:limit]
                
                return [self._movie_to_dict(m) for m in similar]
            except Movie.DoesNotExist:
                return []
                
        except Exception as e:
            logger.error(f"Error getting similar movies: {e}")
            return []

    def _tmdb_result_to_dict(self, result: Dict) -> Dict:
        """
        Convert TMDb API result to our format.
        
        Args:
            result: TMDb API result dictionary
            
        Returns:
            Formatted movie dictionary
        """
        return {
            'tmdb_id': result.get('id'),
            'title': result.get('title'),
            'overview': result.get('overview'),
            'release_date': result.get('release_date'),
            'poster_path': result.get('poster_path'),
            'backdrop_path': result.get('backdrop_path'),
            'vote_average': result.get('vote_average'),
            'vote_count': result.get('vote_count'),
            'popularity': result.get('popularity'),
            'genre_ids': result.get('genre_ids', []),
            'original_language': result.get('original_language'),
            'poster_url': f"https://image.tmdb.org/t/p/w500{result.get('poster_path')}" if result.get('poster_path') else None,
            'backdrop_url': f"https://image.tmdb.org/t/p/w1280{result.get('backdrop_path')}" if result.get('backdrop_path') else None,
        }

