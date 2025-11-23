"""
Movie models for the recommendation system.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Movie(models.Model):
    """
    Movie model storing movie information from TMDb API.
    """
    tmdb_id = models.IntegerField(unique=True, db_index=True, help_text="TMDb movie ID")
    title = models.CharField(max_length=255, db_index=True)
    overview = models.TextField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True, db_index=True)
    poster_path = models.CharField(max_length=500, blank=True, null=True)
    backdrop_path = models.CharField(max_length=500, blank=True, null=True)
    vote_average = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        db_index=True
    )
    vote_count = models.IntegerField(default=0)
    popularity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    genre_ids = models.JSONField(default=list, blank=True, help_text="List of genre IDs")
    original_language = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-popularity', '-vote_average']
        indexes = [
            models.Index(fields=['tmdb_id']),
            models.Index(fields=['release_date']),
            models.Index(fields=['vote_average']),
            models.Index(fields=['-popularity']),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'N/A'})"

    @property
    def full_poster_url(self):
        """Return full poster URL from TMDb."""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None

    @property
    def full_backdrop_url(self):
        """Return full backdrop URL from TMDb."""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{self.backdrop_path}"
        return None


class FavoriteMovie(models.Model):
    """
    User's favorite movies with optional notes.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_movies',
        db_index=True
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        db_index=True
    )
    notes = models.TextField(blank=True, null=True, help_text="User's personal notes about this movie")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'movie']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'movie']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
