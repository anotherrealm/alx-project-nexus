"""
Tests for movie views.
"""
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Movie, FavoriteMovie
from .factories import MovieFactory, UserFactory

User = get_user_model()


class MovieViewSetTestCase(APITestCase):
    """Test cases for MovieViewSet."""
    
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.movie = MovieFactory()
        
        # Generate JWT token for the test user
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_retrieve_movie(self):
        """Test retrieving a movie by TMDb ID."""
        url = reverse('movie-detail', kwargs={'tmdb_id': self.movie.tmdb_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tmdb_id'], self.movie.tmdb_id)
    
    def test_add_to_favorites(self):
        """Test adding a movie to favorites."""
        url = reverse('movie-favorite', kwargs={'tmdb_id': self.movie.tmdb_id})
        response = self.client.post(
            url, 
            {'notes': 'Test note'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FavoriteMovie.objects.filter(
            user=self.user, 
            movie=self.movie
        ).exists())
    
    def test_remove_from_favorites(self):
        """Test removing a movie from favorites."""
        # First add to favorites
        FavoriteMovie.objects.create(user=self.user, movie=self.movie)
        
        url = reverse('movie-favorite', kwargs={'tmdb_id': self.movie.tmdb_id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FavoriteMovie.objects.filter(
            user=self.user, 
            movie=self.movie
        ).exists())


class TrendingMoviesViewTestCase(APITestCase):
    """Test cases for TrendingMoviesView."""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_get_trending_movies(self):
        """Test getting trending movies."""
        url = reverse('movie-trending')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
        self.assertIn('total_results', response.data)
    
    def test_get_trending_movies_with_time_window(self):
        """Test getting trending movies with time window parameter."""
        url = reverse('movie-trending')
        response = self.client.get(url, {'time_window': 'week'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PopularMoviesViewTestCase(APITestCase):
    """Test cases for PopularMoviesView."""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_get_popular_movies(self):
        """Test getting popular movies."""
        url = reverse('movie-popular')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
        self.assertIn('total_results', response.data)


class SearchMoviesViewTestCase(APITestCase):
    """Test cases for SearchMoviesView."""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_search_movies(self):
        """Test searching for movies."""
        url = reverse('movie-search')
        response = self.client.get(url, {'query': 'avengers'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
        self.assertIn('total_results', response.data)
    
    def test_search_movies_empty_query(self):
        """Test searching with an empty query."""
        url = reverse('movie-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results', [])), 0)


class FavoriteMovieViewSetTestCase(APITestCase):
    """Test cases for FavoriteMovieViewSet."""
    
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.movie = MovieFactory()
        self.favorite = FavoriteMovie.objects.create(
            user=self.user,
            movie=self.movie,
            notes='Test note'
        )
        self.url = reverse('favorite-detail', kwargs={'pk': self.favorite.pk})
    
    def test_list_favorites(self):
        """Test listing user's favorite movies."""
        url = reverse('favorite-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)  # Check pagination structure
        favorite_ids = [fav['id'] for fav in response.data['results']]  # Access results from pagination
        self.assertIn(self.favorite.id, favorite_ids)
    
    def test_retrieve_favorite(self):
        """Test retrieving a favorite movie."""
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.favorite.id)
    
    def test_update_favorite_notes(self):
        """Test updating favorite movie notes."""
        new_notes = 'Updated test note'
        response = self.client.patch(
            self.url, 
            {'notes': new_notes},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.favorite.refresh_from_db()
        self.assertEqual(self.favorite.notes, new_notes)
    
    def test_delete_favorite(self):
        """Test deleting a favorite movie."""
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FavoriteMovie.objects.filter(id=self.favorite.id).exists())