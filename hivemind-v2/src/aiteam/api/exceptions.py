"""AI Team OS — Custom exceptions."""

from __future__ import annotations


class NotFoundError(ValueError):
    """Resource not found exception — maps to HTTP 404."""
