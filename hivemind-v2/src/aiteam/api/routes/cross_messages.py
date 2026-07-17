"""AI Team OS — Cross-project messaging routes.

Messages live in the global default DB (not per-project), enabling
different Claude Code sessions / projects to exchange notifications.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Header, HTTPException

from aiteam.api.deps import get_global_repository
from aiteam.api.project_context import compute_project_id
from aiteam.api.schemas import APIListResponse, APIResponse, CrossMessageCreate
from aiteam.storage.repository import StorageRepository
from aiteam.types import CrossMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cross-messages", tags=["cross-messages"])


def _resolve_project_id(x_project_dir: str) -> str:
    """Compute project_id from X-Project-Dir header.

    The header value may be percent-encoded (MCP client encodes non-ASCII
    path components to keep headers latin-1 safe); decode before hashing.
    Raises HTTP 400 if the header is missing.
    """
    import urllib.parse as _up
    if not x_project_dir:
        raise HTTPException(
            status_code=400,
            detail="X-Project-Dir header is required for cross-project messaging",
        )
    return compute_project_id(_up.unquote(x_project_dir))


@router.post("/", response_model=APIResponse[CrossMessage], status_code=201)
async def send_cross_message(
    payload: CrossMessageCreate,
    x_project_dir: str = Header(default=""),
    repo: StorageRepository = Depends(get_global_repository),
) -> APIResponse[CrossMessage]:
    """Send a cross-project message.

    The sender's project_id is derived from the X-Project-Dir header.
    Set to_project_id=null to broadcast to all projects.
    """
    import urllib.parse as _up
    decoded_dir = _up.unquote(x_project_dir)
    from_project_id = _resolve_project_id(x_project_dir)
    msg = await repo.create_cross_message(
        from_project_id=from_project_id,
        from_project_dir=decoded_dir,
        to_project_id=payload.to_project_id or None,
        sender_name=payload.sender_name,
        content=payload.content,
        message_type=payload.message_type,
        metadata=payload.metadata,
    )
    logger.info(
        "Cross-message sent from project %s to %s", from_project_id, payload.to_project_id or "all"
    )
    return APIResponse(data=msg, message="Message sent")


@router.get("/count", response_model=APIResponse[int])
async def count_unread_cross_messages(
    x_project_dir: str = Header(default=""),
    repo: StorageRepository = Depends(get_global_repository),
) -> APIResponse[int]:
    """Get unread message count for the current project's inbox."""
    project_id = _resolve_project_id(x_project_dir)
    count = await repo.count_unread_cross_messages(project_id)
    return APIResponse(data=count)


@router.get("/", response_model=APIListResponse[CrossMessage])
async def list_cross_messages(
    unread_only: bool = False,
    limit: int = 50,
    x_project_dir: str = Header(default=""),
    repo: StorageRepository = Depends(get_global_repository),
) -> APIListResponse[CrossMessage]:
    """List inbox messages for the current project (direct + broadcasts)."""
    project_id = _resolve_project_id(x_project_dir)
    messages = await repo.list_cross_messages(
        project_id=project_id,
        unread_only=unread_only,
        limit=limit,
    )
    return APIListResponse(data=messages, total=len(messages))


@router.put("/{message_id}/read", response_model=APIResponse[CrossMessage])
async def mark_cross_message_read(
    message_id: str,
    repo: StorageRepository = Depends(get_global_repository),
) -> APIResponse[CrossMessage]:
    """Mark a cross-project message as read."""
    msg = await repo.mark_cross_message_read(message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail=f"Message {message_id} not found")
    return APIResponse(data=msg, message="Message marked as read")
