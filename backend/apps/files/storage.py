"""Local filesystem storage adapter."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from django.conf import settings


def media_root() -> Path:
    return Path(settings.MEDIA_ROOT)


def build_storage_key(organization_id, project_id, original_name: str) -> str:
    safe_name = Path(original_name).name.replace("..", "_")
    return f"org/{organization_id}/project/{project_id}/{uuid.uuid4().hex}_{safe_name}"


def save_bytes(storage_key: str, content: bytes) -> tuple[int, str]:
    path = media_root() / storage_key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    return len(content), digest


def open_path(storage_key: str) -> Path:
    return media_root() / storage_key


def read_bytes(storage_key: str) -> bytes:
    return open_path(storage_key).read_bytes()
