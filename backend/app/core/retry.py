from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar

import httpx

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

MAX_ATTEMPTS = 5


def retry_on_disconnect(func: F) -> F:
    """Retries a Supabase call on a transient connection failure (e.g.
    httpx.RemoteProtocolError: Server disconnected, from a stale/idle
    pooled connection, or a longer-lived network blip). Each attempt gets
    a fresh client (see app.core.supabase_client.get_service_client).
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        last_exc: Exception | None = None
        for attempt in range(MAX_ATTEMPTS):
            try:
                if attempt > 0:
                    logger.warning(
                        "Retrying %s after connection error (attempt %d/%d)",
                        func.__name__,
                        attempt + 1,
                        MAX_ATTEMPTS,
                    )
                return func(*args, **kwargs)
            except (httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadTimeout) as exc:
                last_exc = exc
                logger.warning("%s failed on attempt %d/%d: %s", func.__name__, attempt + 1, MAX_ATTEMPTS, exc)
                if attempt < MAX_ATTEMPTS - 1:
                    time.sleep(min(1.0 * (2**attempt), 8.0))
        assert last_exc is not None
        logger.error("%s exhausted all %d retries", func.__name__, MAX_ATTEMPTS)
        raise last_exc

    return wrapper  # type: ignore[return-value]
