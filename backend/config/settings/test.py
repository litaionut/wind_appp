"""Test settings."""

import tempfile
from pathlib import Path

from .base import *  # noqa: F403

DEBUG = False
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="wind_test_media_"))
