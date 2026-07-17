"""AI Team OS — Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

import aiteam

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health_check() -> dict:
    """Simple health check — returns status and version."""
    return {"status": "ok", "version": aiteam.__version__}
