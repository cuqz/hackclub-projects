"""AI Team OS — WebSocket connection manager.

Manages WebSocket connection lifecycle, channel subscriptions, and event broadcasting.
"""

from __future__ import annotations

from fnmatch import fnmatch

from fastapi import WebSocket

from aiteam.api.ws.protocol import WSEvent


class ConnectionManager:
    """WebSocket connection manager."""

    def __init__(self) -> None:
        # Connection ID -> WebSocket instance
        self._connections: dict[str, WebSocket] = {}
        # Connection ID -> subscribed channel set
        self._subscriptions: dict[str, set[str]] = {}
        # Channel -> set of connection IDs subscribed to it (accelerated lookup)
        self._channel_index: dict[str, set[str]] = {}

    @property
    def active_count(self) -> int:
        """Current active connection count."""
        return len(self._connections)

    async def connect(self, conn_id: str, websocket: WebSocket) -> None:
        """Register a new WebSocket connection."""
        await websocket.accept()
        self._connections[conn_id] = websocket
        self._subscriptions[conn_id] = set()

    def disconnect(self, conn_id: str) -> None:
        """Unregister a WebSocket connection."""
        # Clean up channel index
        channels = self._subscriptions.pop(conn_id, set())
        for channel in channels:
            if channel in self._channel_index:
                self._channel_index[channel].discard(conn_id)
                if not self._channel_index[channel]:
                    del self._channel_index[channel]
        # Remove connection
        self._connections.pop(conn_id, None)

    def subscribe(self, conn_id: str, channel: str) -> None:
        """Subscribe to a channel."""
        if conn_id not in self._subscriptions:
            return
        self._subscriptions[conn_id].add(channel)
        if channel not in self._channel_index:
            self._channel_index[channel] = set()
        self._channel_index[channel].add(conn_id)

    def unsubscribe(self, conn_id: str, channel: str) -> None:
        """Unsubscribe from a channel."""
        if conn_id in self._subscriptions:
            self._subscriptions[conn_id].discard(channel)
        if channel in self._channel_index:
            self._channel_index[channel].discard(conn_id)
            if not self._channel_index[channel]:
                del self._channel_index[channel]

    async def broadcast_event(self, event: WSEvent) -> None:
        """Broadcast events by channel pattern matching.

        Uses fnmatch wildcard matching, e.g. "team.*" matches "team.created" channel.
        """
        target_conn_ids: set[str] = set()

        for channel, conn_ids in self._channel_index.items():
            # Wildcard matching: subscription channel pattern matches event channel
            if fnmatch(event.channel, channel):
                target_conn_ids.update(conn_ids)

        if not target_conn_ids:
            return

        message = event.model_dump_json()
        disconnected: list[str] = []

        for conn_id in target_conn_ids:
            ws = self._connections.get(conn_id)
            if ws is None:
                continue
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(conn_id)

        # Clean up disconnected connections
        for conn_id in disconnected:
            self.disconnect(conn_id)


# Global singleton
ws_manager = ConnectionManager()
