"""Local development settings."""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True
