"""Authentication middleware and dependencies for SpaceEye API.

Provides consistent API key authentication across all endpoints.
Public routes are registered via register_no_auth_route() in main.py.
"""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from backend.config import get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """Verify API key if configured. Skipped when API_KEY env var is empty."""
    settings = get_settings()
    if not settings.api_key:
        return  # Auth disabled
    if not api_key or api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# Routes that don't require authentication
_NO_AUTH_ROUTES: set[str] = set()


def register_no_auth_route(route_path: str) -> None:
    """Register a route path as not requiring authentication."""
    _NO_AUTH_ROUTES.add(route_path)


class AuthenticationMiddleware:
    """ASGI middleware for API key authentication.

    This middleware provides consistent authentication across all API endpoints.
    Public routes are registered via register_no_auth_route().

    Usage:
        # In main.py:
        register_no_auth_route("/api/health")
        register_no_auth_route("/api/public")
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Only apply to API routes
        path = scope.get("path", "")
        if not path.startswith("/api/"):
            await self.app(scope, receive, send)
            return

        # Skip auth for docs and health endpoints
        if path in ("/api/docs", "/api/redoc", "/api/openapi.json", "/api/health"):
            await self.app(scope, receive, send)
            return

        # Check if auth is enabled
        settings = get_settings()
        if not settings.api_key:
            await self.app(scope, receive, send)
            return

        # Check if route is marked as no-auth
        if path in _NO_AUTH_ROUTES:
            await self.app(scope, receive, send)
            return

        # Extract API key from headers
        headers = dict(scope.get("headers", []))
        api_key = None
        for header_name, header_value in headers.items():
            if header_name == b"x-api-key":
                api_key = header_value.decode("utf-8")
                break

        # Verify API key
        if not api_key or api_key != settings.api_key:
            # Return 401 error
            response_body = b'{"detail":"Invalid or missing API key"}'
            await send(
                {
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        [b"content-type", b"application/json"],
                        [b"content-length", str(len(response_body)).encode()],
                    ],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": response_body,
                }
            )
            return

        # API key is valid, proceed
        await self.app(scope, receive, send)
