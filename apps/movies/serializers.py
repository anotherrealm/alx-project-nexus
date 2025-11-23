"""
Serializers for the movies app.
"""
from rest_framework import serializers
from .models import Movie, FavoriteMovie


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for the Movie model."""
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'title', 'overview', 'release_date',
            'poster_path', 'backdrop_path', 'poster_url', 'backdrop_url',
            'vote_average', 'vote_count', 'popularity', 'genre_ids',
            'original_language', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_poster_url(self, obj):
        return obj.full_poster_url
    
    def get_backdrop_url(self, obj):
        return obj.full_backdrop_url


class FavoriteMovieSerializer(serializers.ModelSerializer):
    """Serializer for the FavoriteMovie model."""
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FavoriteMovie
        fields = ['id', 'user', 'movie', 'movie_id', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class MovieSearchSerializer(serializers.Serializer):
    """Serializer for movie search results."""
    results = MovieSerializer(many=True)
    page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_results = serializers.IntegerField()