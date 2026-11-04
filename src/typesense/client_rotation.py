"""
Optional limit on how long a client keeps sending requests with one httpx client.

httpx closes a pooled connection only once it sits idle for its keep-alive expiry,
so under steady traffic a connection is reused for good. When several nodes sit
behind one load balancer, every connection then stays on the node it first reached.
With ``max_connection_lifetime_seconds`` set, an httpx client that reaches that age
is replaced by a new one, and later requests open new connections. Requests and
streams already sent with the old client finish on it, and it is closed once the
last of them is done.

``AsyncClientRotation`` is used by the async client and ``ClientRotation`` by the
sync client (``utils/run-unasync.py`` maps one name to the other). Both hand out the
same client for good when ``max_connection_lifetime_seconds`` is ``None``.
"""

import asyncio
import contextlib
import random
import sys
import threading
from time import monotonic

from typesense.http_backend import AsyncClientType, SyncClientType

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TClient = typing.TypeVar("TClient")


class _ClientRotation(typing.Generic[TClient]):
    """Tracks the current client and the retired clients still in use."""

    def __init__(
        self,
        build_client: typing.Callable[[], TClient],
        max_lifetime_seconds: typing.Optional[float],
    ) -> None:
        """
        Build the first client.

        Args:
            build_client (Callable[[], TClient]): Builds a client to send requests with.
            max_lifetime_seconds (Optional[float]): How long a client is used for new
                requests, or ``None`` to use the first client for good.
        """
        self._build_client = build_client
        self._max_lifetime_seconds = max_lifetime_seconds
        self._client = build_client()
        self._expires_at = self._deadline()
        self._in_flight = 0
        self._retired: typing.Dict[TClient, int] = {}

    def _deadline(self) -> typing.Optional[float]:
        """Return when a client built now expires, up to 10% late at random."""
        if self._max_lifetime_seconds is None:
            return None
        return monotonic() + self._max_lifetime_seconds * random.uniform(1.0, 1.1)

    def _checkout(self) -> typing.Tuple[TClient, typing.Optional[TClient]]:
        """
        Take the client to send a request with, replacing it first if it has expired.

        Returns:
            Tuple[TClient, Optional[TClient]]: The client, and the replaced client
                when nothing is using it any more and it should be closed.
        """
        idle_client: typing.Optional[TClient] = None
        if self._expires_at is not None and monotonic() >= self._expires_at:
            new_client = self._build_client()
            if self._in_flight:
                self._retired[self._client] = self._in_flight
            else:
                idle_client = self._client
            self._client = new_client
            self._expires_at = self._deadline()
            self._in_flight = 0
        self._in_flight += 1
        return self._client, idle_client

    def _checkin(self, client: TClient) -> typing.Optional[TClient]:
        """
        Give back a client taken with ``_checkout``.

        Returns:
            Optional[TClient]: The client, when it was retired and this was its last
                request, so it should be closed. A client that ``_take_all_clients``
                already handed over for closing is never returned again.
        """
        if client is self._client:
            self._in_flight -= 1
            return None
        if client not in self._retired:
            return None
        self._retired[client] -= 1
        if self._retired[client]:
            return None
        del self._retired[client]
        return client

    def _take_all_clients(self) -> typing.List[TClient]:
        """
        Return the current client and the retired ones, and stop tracking them.

        The current client is never replaced after this, so requests sent after
        closing fail as they would without a lifetime.
        """
        clients = [self._client, *self._retired]
        self._retired.clear()
        self._expires_at = None
        return clients


class AsyncClientRotation(_ClientRotation[AsyncClientType]):
    """
    Hands out the async client each request is sent with.

    Closes are shielded from cancellation. httpx marks a client closed before it
    closes its connections, so a close cut short would never be finished.
    """

    @contextlib.asynccontextmanager
    async def lease(self) -> typing.AsyncIterator[AsyncClientType]:
        """Hold the client to send a request with until the request is done."""
        client, idle_client = self._checkout()
        try:
            if idle_client is not None:
                await asyncio.shield(idle_client.aclose())
            yield client
        finally:
            idle_client = self._checkin(client)
            if idle_client is not None:
                await asyncio.shield(idle_client.aclose())

    async def aclose(self) -> None:
        """Close the current client and every retired client still in use."""
        clients = self._take_all_clients()
        await asyncio.shield(asyncio.gather(*(client.aclose() for client in clients)))


class ClientRotation(_ClientRotation[SyncClientType]):
    """Hands out the client each request is sent with, from any thread."""

    def __init__(
        self,
        build_client: typing.Callable[[], SyncClientType],
        max_lifetime_seconds: typing.Optional[float],
    ) -> None:
        """
        Build the first client.

        Args:
            build_client (Callable[[], SyncClientType]): Builds a client to send
                requests with.
            max_lifetime_seconds (Optional[float]): How long a client is used for new
                requests, or ``None`` to use the first client for good.
        """
        super().__init__(build_client, max_lifetime_seconds)
        # The GC can give back a dropped stream's lease on a thread holding the lock.
        self._lock = threading.RLock()

    @contextlib.contextmanager
    def lease(self) -> typing.Iterator[SyncClientType]:
        """Hold the client to send a request with until the request is done."""
        with self._lock:
            client, idle_client = self._checkout()
        try:
            if idle_client is not None:
                idle_client.close()
            yield client
        finally:
            with self._lock:
                idle_client = self._checkin(client)
            if idle_client is not None:
                idle_client.close()

    def close(self) -> None:
        """Close the current client and every retired client still in use."""
        with self._lock:
            clients = self._take_all_clients()
        with contextlib.ExitStack() as stack:
            for client in clients:
                stack.callback(client.close)
