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

urlpatterns = [
    path('', include(router.urls)),
    path('trending/', TrendingMoviesView.as_view(), name='movie-trending'),
    path('popular/', PopularMoviesView.as_view(), name='movie-popular'),
    path('search/', SearchMoviesView.as_view(), name='movie-search'),
]