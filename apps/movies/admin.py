"""
Admin configuration for movies app.
"""
from django.contrib import admin
from .models import Movie, FavoriteMovie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Admin interface for Movie model."""
    list_display = ['title', 'tmdb_id', 'release_date', 'vote_average', 'popularity', 'created_at']
    list_filter = ['release_date', 'original_language', 'created_at']
    search_fields = ['title', 'overview', 'tmdb_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-popularity', '-vote_average']


@admin.register(FavoriteMovie)
class FavoriteMovieAdmin(admin.ModelAdmin):
    """Admin interface for FavoriteMovie model."""
    list_display = ['user', 'movie', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'movie__title', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
