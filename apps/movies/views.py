"""
Views for the movies app.
"""
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, FavoriteMovie
from .serializers import MovieSerializer, FavoriteMovieSerializer, MovieSearchSerializer
from .services.tmdb_service import TMDbService
from .utils.cache import cache_page_on_auth


class MovieViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    """ViewSet for movie-related operations."""
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]
    lookup_field = 'tmdb_id'
    lookup_url_kwarg = 'tmdb_id'
    
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
            
        return Response(status=status.HTTP_204_NO_CONTENT


class MovieListMixin:
    """Mixin for list views that use TMDb API."""
    permission_classes = [AllowAny]
    serializer_class = MovieSearchSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        return {'request': self.request}
    
    def get_queryset(self):
        """Return an empty queryset since we're using TMDb API."""
        return Movie.objects.none()
    
    def get_serializer(self, *args, **kwargs):
        """Return the serializer instance."""
        if 'data' in kwargs:
            return super().get_serializer(*args, **kwargs)
        return self.serializer_class(data=self.get_data(), context=self.get_serializer_context())
    
    def get_data(self):
        """Get data from TMDb API."""
        raise NotImplementedError("Subclasses must implement get_data()")
    
    def list(self, request, *args, **kwargs):
        """Handle GET request."""
        page = request.query_params.get('page', 1)
        try:
            page = int(page)
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
            
        data = self.get_data()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class TrendingMoviesView(MovieListMixin, viewsets.GenericViewSet):
    """View for trending movies."""
    
    @cache_page_on_auth(60 * 15)  # 15 minutes cache for anonymous users, 5 minutes for authenticated
    def get_data(self):
        """Get trending movies from TMDb API."""
        page = int(self.request.query_params.get('page', 1))
        time_window = self.request.query_params.get('time_window', 'day')
        
        if time_window not in ['day', 'week']:
            time_window = 'day'
            
        tmdb_service = TMDbService()
        return tmdb_service.get_trending_movies(page=page, time_window=time_window)


class PopularMoviesView(MovieListMixin, viewsets.GenericViewSet):
    """View for popular movies."""
    
    @cache_page_on_auth(60 * 60)  # 1 hour cache for anonymous users, 30 minutes for authenticated
    def get_data(self):
        """Get popular movies from TMDb API."""
        page = int(self.request.query_params.get('page', 1))
        tmdb_service = TMDbService()
        return tmdb_service.get_popular_movies(page=page)


class SearchMoviesView(MovieListMixin, viewsets.GenericViewSet):
    """View for searching movies."""
    
    @cache_page_on_auth(60 * 60 * 2)  # 2 hours cache for anonymous users, 1 hour for authenticated
    def get_data(self):
        """Search movies from TMDb API."""
        query = self.request.query_params.get('query', '').strip()
        page = int(self.request.query_params.get('page', 1))
        
        if not query:
            return {
                'results': [],
                'page': 1,
                'total_pages': 0,
                'total_results': 0
            }
            
        tmdb_service = TMDbService()
        return tmdb_service.search_movies(query=query, page=page)


class FavoriteMovieViewSet(viewsets.ModelViewSet):
    """ViewSet for user's favorite movies."""
    serializer_class = FavoriteMovieSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's favorite movies."""
        return FavoriteMovie.objects.filter(user=self.request.user).select_related('movie')
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a favorite."""
        movie_id = serializer.validated_data.get('movie_id')
        movie = get_object_or_404(Movie, pk=movie_id)
        serializer.save(user=self.request.user, movie=movie)
