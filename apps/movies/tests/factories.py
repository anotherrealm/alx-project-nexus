"""
Test factories for movies app.
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from ..models import Movie, FavoriteMovie

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True


class MovieFactory(DjangoModelFactory):
    """Factory for creating test movies."""
    class Meta:
        model = Movie
        django_get_or_create = ('tmdb_id',)
    
    tmdb_id = factory.Sequence(lambda n: 1000 + n)
    title = factory.Faker('sentence', nb_words=3)
    overview = factory.Faker('paragraph', nb_sentences=3)
    release_date = factory.Faker('date_this_decade')
    poster_path = factory.Faker('file_path', extension='jpg')
    backdrop_path = factory.Faker('file_path', extension='jpg')
    vote_average = factory.Faker('pydecimal', left_digits=1, right_digits=1, positive=True, min_value=1, max_value=10)
    vote_count = factory.Faker('random_int', min=10, max=10000)
    popularity = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    genre_ids = factory.LazyFunction(lambda: [1, 2, 3])  # Example genre IDs
    original_language = 'en'


class FavoriteMovieFactory(DjangoModelFactory):
    """Factory for creating test favorite movies."""
    class Meta:
        model = FavoriteMovie
        django_get_or_create = ('user', 'movie')
    
    user = factory.SubFactory(UserFactory)
    movie = factory.SubFactory(MovieFactory)
    notes = factory.Faker('sentence', nb_words=6)
