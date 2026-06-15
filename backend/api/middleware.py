"""ASGI middleware for request correlation IDs."""

import uuid
from typing import Any

from backend.logging_config import correlation_id_var


class CorrelationMiddleware:
    """ASGI middleware that generates and tracks correlation IDs for requests.

    This middleware:
    1. Generates a unique correlation ID for each request
    2. Sets it in the context variable for logging
    3. Adds it to response headers for client-side tracking
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Generate correlation ID
        correlation_id = uuid.uuid4().hex[:12]

        # Set in context variable
        token = correlation_id_var.set(correlation_id)

        # Store in scope for access in handlers
        scope["correlation_id"] = correlation_id

        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                # Add correlation ID to response headers
                headers = list(message.get("headers", []))
                headers.append([b"x-correlation-id", correlation_id.encode()])
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Reset context variable
            correlation_id_var.reset(token)
