"""
URLs for the movies app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    MovieViewSet,
    TrendingMoviesView,
    PopularMoviesView,
    SearchMoviesView,
    FavoriteMovieViewSet
)

router = DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'favorites', FavoriteMovieViewSet, basename='favorite')

# Additional URL patterns for list views
urlpatterns = [
    path('', include(router.urls)),
    path('movies/trending/', 
         TrendingMoviesView.as_view({'get': 'list'}), 
         name='movie-trending'),
    path('movies/popular/', 
         PopularMoviesView.as_view({'get': 'list'}), 
         name='movie-popular'),
    path('movies/search/', 
         SearchMoviesView.as_view({'get': 'list'}), 
         name='movie-search'),
]