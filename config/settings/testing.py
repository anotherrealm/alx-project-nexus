from .base import *

DEBUG = False

# Use an in-memory SQLite DB for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
