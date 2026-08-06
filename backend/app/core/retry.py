from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, TypeVar

import httpx

F = TypeVar("F", bound=Callable[..., Any])


def retry_on_disconnect(func: F) -> F:
    """Retries a Supabase call up to 3 times on a transient connection
    failure (e.g. httpx.RemoteProtocolError: Server disconnected, from a
    stale/idle pooled connection). Each attempt gets a fresh client (see
    app.core.supabase_client.get_service_client), so a retry almost always
    succeeds.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except (httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadTimeout) as exc:
                last_exc = exc
                if attempt < 2:
                    time.sleep(0.5 * (attempt + 1))
        assert last_exc is not None
        raise last_exc

    return wrapper  # type: ignore[return-value]
