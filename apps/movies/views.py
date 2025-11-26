import logging
from functools import wraps
from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .models import Movie, FavoriteMovie
from .serializers import MovieSerializer, FavoriteMovieSerializer, MovieSearchSerializer
from .services.tmdb_service import TMDbService

logger = logging.getLogger(__name__)

def cache_page_on_auth(anon_timeout, auth_timeout=None):
    """Cache API responses with different timeouts for auth and anon users."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            user_key = f"user_{request.user.id}" if request.user.is_authenticated else "anon"
            cache_key = f"view_cache:{user_key}:{request.get_full_path()}"
            
            if cached_response := cache.get(cache_key):
                return Response(cached_response)
            
            response = view_func(self, request, *args, **kwargs)
            
            if response.status_code == 200:
                timeout = auth_timeout if request.user.is_authenticated else anon_timeout
                cache.set(cache_key, response.data, timeout)
            
            return response
        return _wrapped_view
    return decorator


class MovieViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    """ViewSet for movie-related operations."""
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]
    lookup_field = 'tmdb_id'
    lookup_url_kwarg = 'tmdb_id'
    
    @method_decorator(cache_page_on_auth(60 * 15, 60 * 5))  # 15m for anon, 5m for auth
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def get_queryset(self):
        """Return the queryset with select_related and prefetch_related for optimization."""
        return super().get_queryset().select_related()
    
    @cache_page_on_auth(60 * 15)  # 15 minutes cache for anonymous users, 5 minutes for authenticated
    def retrieve(self, request, *args, **kwargs):
        """Get movie details by TMDb ID."""
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, tmdb_id=None):
        """Add a movie to user's favorites."""
        movie = self.get_object()
        favorite, created = FavoriteMovie.objects.get_or_create(
            user=request.user,
            movie=movie,
            defaults={'notes': request.data.get('notes', '')}
        )
        
        if not created:
            return Response(
                {'detail': 'Movie is already in your favorites.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = FavoriteMovieSerializer(favorite, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @favorite.mapping.delete
    def remove_favorite(self, request, tmdb_id=None):
        """Remove a movie from user's favorites."""
        movie = self.get_object()
        deleted = FavoriteMovie.objects.filter(
            user=request.user,
            movie=movie
        ).delete()
        
        if deleted[0] == 0:
            return Response(
                {'detail': 'Movie was not in your favorites.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response(status=status.HTTP_204_NO_CONTENT)


class TrendingMoviesView(APIView):
    """API View for trending movies."""
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Handle GET request for trending movies."""
        try:
            page = int(request.query_params.get('page', 1))
            time_window = request.query_params.get('time_window', 'day')
            
            if time_window not in ['day', 'week']:
                time_window = 'day'
                
            tmdb_service = TMDbService()
            data = tmdb_service.get_trending_movies(page=page, time_window=time_window)
            return Response(data)
            
        except ValueError as e:
            return Response(
                {'error': 'Invalid request parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error fetching trending movies: {str(e)}")
            return Response(
                {'error': 'Failed to fetch trending movies'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PopularMoviesView(APIView):
    """API View for popular movies."""
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Handle GET request for popular movies."""
        try:
            page = int(request.query_params.get('page', 1))
            tmdb_service = TMDbService()
            data = tmdb_service.get_popular_movies(page=page)
            return Response(data)
            
        except ValueError as e:
            return Response(
                {'error': 'Invalid page number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error fetching popular movies: {str(e)}")
            return Response(
                {'error': 'Failed to fetch popular movies'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchMoviesView(APIView):
    """API View for searching movies."""
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """Handle GET request for movie search."""
        try:
            query = request.query_params.get('query', '').strip()
            page = int(request.query_params.get('page', 1))
            
            tmdb_service = TMDbService()
            data = tmdb_service.search_movies(query=query, page=page)
            return Response(data)
            
        except ValueError as e:
            return Response(
                {'error': 'Invalid request parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error searching movies: {str(e)}")
            return Response(
                {'error': 'Failed to search movies'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class FavoriteMovieViewSet(viewsets.ModelViewSet):
    """ViewSet for user's favorite movies."""
    serializer_class = FavoriteMovieSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination  # Add pagination
    
    def get_queryset(self):
        """Return only the current user's favorite movies."""
        return FavoriteMovie.objects.filter(user=self.request.user).select_related('movie')
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a favorite."""
        movie_id = serializer.validated_data.get('movie_id')
        movie = get_object_or_404(Movie, pk=movie_id)
        serializer.save(user=self.request.user, movie=movie)
        
    def list(self, request, *args, **kwargs):
        """Override list to ensure pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
