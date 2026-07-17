"""AI Team OS — WebSocket message protocol.

Defines message formats between server and client.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ============================================================
# Server -> Client
# ============================================================


class WSEvent(BaseModel):
    """Server-pushed event message."""

    type: str = "event"
    channel: str
    event_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class WSPong(BaseModel):
    """Heartbeat response."""

    type: str = "pong"


class WSAck(BaseModel):
    """Operation acknowledgment."""

    type: str = "ack"
    action: str
    detail: str = ""


class WSError(BaseModel):
    """Error message."""

    type: str = "error"
    message: str


# ============================================================
# Client -> Server
# ============================================================


class WSSubscribe(BaseModel):
    """Subscribe to a channel."""

    type: str = "subscribe"
    channel: str


class WSUnsubscribe(BaseModel):
    """Unsubscribe from a channel."""

    type: str = "unsubscribe"
    channel: str


class WSPing(BaseModel):
    """Heartbeat request."""

    type: str = "ping"
