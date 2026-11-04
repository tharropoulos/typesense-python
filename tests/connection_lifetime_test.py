"""Tests for replacing the httpx client once it reaches its lifetime."""

import asyncio
import gc
import pathlib
import shutil
import sys
import threading
import types
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

import certifi
import httpx
import pytest
from pytest_mock import MockerFixture

from tests.utils.streaming import CHUNKS, FINAL_RESPONSE, sse_body
from typesense import AsyncClient, Client
from typesense.async_.api_call import AsyncApiCall
from typesense.client_rotation import AsyncClientRotation, ClientRotation
from typesense.configuration import Configuration
from typesense.exceptions import ConfigError
from typesense.sync.api_call import ApiCall

LIFETIME_SECONDS: typing.Final = 60.0

_WAIT_SECONDS: typing.Final = 5


class _Clock:
    """A monotonic clock that only moves when told to."""

    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance_past_lifetime(self) -> None:
        """Move past the latest deadline a jittered lifetime can have."""
        self.now += LIFETIME_SECONDS * 1.1 + 1


class _Server(ThreadingHTTPServer):
    """
    Answers every request on a real socket and records its client port.

    ``/slow`` answers once ``release_slow_request`` is set. ``/stream`` sends the
    first answer piece, then the rest once ``resume_stream`` is set.
    """

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), _Handler)
        self.ports: typing.List[int] = []
        self.slow_request_started = threading.Event()
        self.release_slow_request = threading.Event()
        self.resume_stream = threading.Event()


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server: _Server

    def do_GET(self) -> None:
        self.server.ports.append(self.client_address[1])
        if self.path == "/stream":
            self._send_stream()
            return
        if self.path == "/slow":
            self.server.slow_request_started.set()
            self.server.release_slow_request.wait(_WAIT_SECONDS)
        body = b'{"ok": true}'
        self._send_headers("application/json", len(body))
        self.wfile.write(body)

    def _send_stream(self) -> None:
        first_chunk = sse_body(CHUNKS[:1])
        rest = sse_body(CHUNKS[1:], FINAL_RESPONSE)
        self._send_headers("text/event-stream", len(first_chunk) + len(rest))
        self.wfile.write(first_chunk)
        self.server.resume_stream.wait(_WAIT_SECONDS)
        self.wfile.write(rest)

    def _send_headers(self, content_type: str, content_length: int) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass


@pytest.fixture(name="server")
def server_fixture() -> typing.Iterator[_Server]:
    """Run a keep-alive HTTP server on a free local port."""
    server = _Server()
    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.05},
        daemon=True,
    )
    thread.start()
    yield server
    server.release_slow_request.set()
    server.resume_stream.set()
    server.shutdown()
    server.server_close()


@pytest.fixture(name="clock")
def clock_fixture(mocker: MockerFixture) -> _Clock:
    """Replace the clock that client lifetimes are measured with."""
    clock = _Clock()
    mocker.patch("typesense.client_rotation.monotonic", new=clock)
    return clock


def _config(
    server: _Server,
    max_connection_lifetime_seconds: typing.Optional[float],
    **overrides: object,
) -> Configuration:
    return Configuration(
        {
            "api_key": "xyz",
            "nodes": [
                {"host": "127.0.0.1", "port": server.server_port, "protocol": "http"},
            ],
            "num_retries": 0,
            "connection_timeout_seconds": _WAIT_SECONDS,
            "max_connection_lifetime_seconds": max_connection_lifetime_seconds,
            **overrides,
        },
    )


def _assert_new_port_per_lifetime(ports: typing.List[int], lifetimes: int) -> None:
    """Assert requests were sent two per lifetime, each pair on its own connection."""
    pairs = [ports[index : index + 2] for index in range(0, len(ports), 2)]
    assert [len(set(pair)) for pair in pairs] == [1] * lifetimes
    assert len(set(ports)) == lifetimes


def test_reuses_one_connection_without_a_lifetime(server: _Server) -> None:
    """Test that sequential requests share one kept-alive connection by default."""
    with ApiCall(_config(server, None)) as api_call:
        for _ in range(10):
            api_call.get("/", entity_type=typing.Dict[str, bool])

    assert len(server.ports) == 10
    assert len(set(server.ports)) == 1


async def test_async_reuses_one_connection_without_a_lifetime(
    server: _Server,
) -> None:
    """Test that sequential async requests share one kept-alive connection by default."""
    async with AsyncApiCall(_config(server, None)) as api_call:
        for _ in range(10):
            await api_call.get("/", entity_type=typing.Dict[str, bool])

    assert len(server.ports) == 10
    assert len(set(server.ports)) == 1


def test_opens_a_new_connection_after_each_lifetime(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that every expiry replaces the client, and with it the connection."""
    with ApiCall(_config(server, LIFETIME_SECONDS)) as api_call:
        for _ in range(3):
            api_call.get("/", entity_type=typing.Dict[str, bool])
            api_call.get("/", entity_type=typing.Dict[str, bool])
            clock.advance_past_lifetime()

    _assert_new_port_per_lifetime(server.ports, lifetimes=3)


async def test_async_opens_a_new_connection_after_each_lifetime(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that every expiry replaces the async client, and with it the connection."""
    async with AsyncApiCall(_config(server, LIFETIME_SECONDS)) as api_call:
        for _ in range(3):
            await api_call.get("/", entity_type=typing.Dict[str, bool])
            await api_call.get("/", entity_type=typing.Dict[str, bool])
            clock.advance_past_lifetime()

    _assert_new_port_per_lifetime(server.ports, lifetimes=3)


def test_request_in_flight_finishes_on_the_replaced_client(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that a request sent before the client is replaced still succeeds."""
    with ApiCall(_config(server, LIFETIME_SECONDS)) as api_call:
        retired_client = api_call._clients._client
        with ThreadPoolExecutor(max_workers=1) as executor:
            slow_request = executor.submit(
                api_call.get,
                "/slow",
                entity_type=typing.Dict[str, bool],
            )
            assert server.slow_request_started.wait(_WAIT_SECONDS)

            clock.advance_past_lifetime()
            api_call.get("/", entity_type=typing.Dict[str, bool])
            assert api_call._clients._client is not retired_client
            assert retired_client.is_closed is False

            server.release_slow_request.set()
            assert slow_request.result(timeout=_WAIT_SECONDS) == {"ok": True}

        assert retired_client.is_closed is True

    assert len(set(server.ports)) == 2


async def test_async_request_in_flight_finishes_on_the_replaced_client(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that an async request sent before the client is replaced still succeeds."""
    async with AsyncApiCall(_config(server, LIFETIME_SECONDS)) as api_call:
        retired_client = api_call._clients._client
        slow_request = asyncio.ensure_future(
            api_call.get("/slow", entity_type=typing.Dict[str, bool]),
        )
        assert await asyncio.to_thread(server.slow_request_started.wait, _WAIT_SECONDS)

        clock.advance_past_lifetime()
        await api_call.get("/", entity_type=typing.Dict[str, bool])
        assert api_call._clients._client is not retired_client
        assert retired_client.is_closed is False

        server.release_slow_request.set()
        assert await slow_request == {"ok": True}
        assert retired_client.is_closed is True

    assert len(set(server.ports)) == 2


class _FakeAsyncClient:
    """An async client that closes once ``allow_close`` is set."""

    def __init__(self, close_error: typing.Optional[Exception] = None) -> None:
        self.is_closed = False
        self.close_started = asyncio.Event()
        self.allow_close = asyncio.Event()
        self._close_error = close_error

    async def aclose(self) -> None:
        self.close_started.set()
        await self.allow_close.wait()
        if self._close_error is not None:
            raise self._close_error
        self.is_closed = True


async def test_async_cancelled_request_still_gives_its_client_back(
    clock: _Clock,
) -> None:
    """Test that a request cancelled while the old client closes releases its client."""
    slow_closing_client = _FakeAsyncClient()
    replacement_client = _FakeAsyncClient()
    built_clients = iter([slow_closing_client, replacement_client, _FakeAsyncClient()])
    clients = AsyncClientRotation(built_clients.__next__, LIFETIME_SECONDS)

    async def send_request() -> None:
        async with clients.lease():
            pass

    clock.advance_past_lifetime()
    cancelled_request = asyncio.ensure_future(send_request())
    await asyncio.sleep(0)
    cancelled_request.cancel()
    with pytest.raises(asyncio.CancelledError):
        await cancelled_request

    slow_closing_client.allow_close.set()
    await asyncio.sleep(0)
    assert slow_closing_client.is_closed is True

    replacement_client.allow_close.set()
    clock.advance_past_lifetime()
    await send_request()
    assert replacement_client.is_closed is True


def test_open_stream_keeps_reading_after_the_client_is_replaced(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that a stream outlives its client's lifetime, which closes after it."""
    with ApiCall(_config(server, LIFETIME_SECONDS)) as api_call:
        retired_client = api_call._clients._client
        with api_call.stream("GET", "/stream", typing.Dict[str, object]) as stream:
            assert next(stream) == CHUNKS[0]

            clock.advance_past_lifetime()
            api_call.get("/", entity_type=typing.Dict[str, bool])
            server.resume_stream.set()

            assert [next(stream), next(stream)] == CHUNKS[1:]
            assert retired_client.is_closed is False
            assert stream.get_final_response() == FINAL_RESPONSE
            assert retired_client.is_closed is True

        assert api_call._clients._client.is_closed is False

    assert len(set(server.ports)) == 2


async def test_async_open_stream_keeps_reading_after_the_client_is_replaced(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that an async stream outlives its client's lifetime, which closes after it."""
    async with AsyncApiCall(_config(server, LIFETIME_SECONDS)) as api_call:
        retired_client = api_call._clients._client
        stream = await api_call.stream("GET", "/stream", typing.Dict[str, object])
        async with stream:
            assert await stream.__anext__() == CHUNKS[0]

            clock.advance_past_lifetime()
            await api_call.get("/", entity_type=typing.Dict[str, bool])
            server.resume_stream.set()

            assert [await stream.__anext__(), await stream.__anext__()] == CHUNKS[1:]
            assert retired_client.is_closed is False
            assert await stream.get_final_response() == FINAL_RESPONSE
            assert retired_client.is_closed is True

        assert api_call._clients._client.is_closed is False

    assert len(set(server.ports)) == 2


def test_never_replaces_or_closes_a_user_supplied_client(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that the lifetime does not apply to a client passed in by the caller."""
    http_client = httpx.Client()
    with ApiCall(_config(server, LIFETIME_SECONDS), http_client) as api_call:
        for _ in range(3):
            api_call.get("/", entity_type=typing.Dict[str, bool])
            clock.advance_past_lifetime()

        assert api_call._clients._client is http_client

    assert http_client.is_closed is False
    assert len(server.ports) == 3
    assert len(set(server.ports)) == 1
    http_client.close()


async def test_async_never_replaces_or_closes_a_user_supplied_client(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that the lifetime does not apply to an async client passed in by the caller."""
    http_client = httpx.AsyncClient()
    async with AsyncApiCall(
        _config(server, LIFETIME_SECONDS),
        http_client,
    ) as api_call:
        for _ in range(3):
            await api_call.get("/", entity_type=typing.Dict[str, bool])
            clock.advance_past_lifetime()

        assert api_call._clients._client is http_client

    assert http_client.is_closed is False
    assert len(server.ports) == 3
    assert len(set(server.ports)) == 1
    await http_client.aclose()


@pytest.mark.parametrize("client_class", [Client, AsyncClient])
@pytest.mark.parametrize("lifetime", [0, -1, "60", True, float("nan"), float("inf")])
def test_rejects_an_invalid_lifetime(
    client_class: typing.Union[typing.Type[Client], typing.Type[AsyncClient]],
    lifetime: object,
) -> None:
    """Test that the lifetime must be a finite number greater than 0."""
    with pytest.raises(
        ConfigError,
        match="`max_connection_lifetime_seconds` must be a finite number greater than 0.",
    ):
        client_class(
            {
                "api_key": "xyz",
                "nodes": ["http://localhost:8108"],
                "max_connection_lifetime_seconds": lifetime,
            },
        )


@pytest.mark.parametrize("client_class", [Client, AsyncClient])
@pytest.mark.parametrize("lifetime", [None, 0.5, 300])
def test_accepts_a_valid_lifetime(
    client_class: typing.Union[typing.Type[Client], typing.Type[AsyncClient]],
    lifetime: typing.Optional[float],
) -> None:
    """Test that the lifetime can be unset or any number greater than 0."""
    client = client_class(
        {
            "api_key": "xyz",
            "nodes": ["http://localhost:8108"],
            "max_connection_lifetime_seconds": lifetime,
        },
    )

    assert client.config.max_connection_lifetime_seconds == lifetime


def test_close_closes_the_current_and_the_draining_client(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that closing closes a replaced client that a stream is still reading."""
    api_call = ApiCall(_config(server, LIFETIME_SECONDS))
    retired_client = api_call._clients._client
    stream = api_call.stream("GET", "/stream", typing.Dict[str, object])
    clock.advance_past_lifetime()
    api_call.get("/", entity_type=typing.Dict[str, bool])
    current_client = api_call._clients._client

    api_call.close()

    assert retired_client.is_closed is True
    assert current_client.is_closed is True
    stream.close()


async def test_async_close_closes_the_current_and_the_draining_client(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that closing closes a replaced async client that a stream is still reading."""
    api_call = AsyncApiCall(_config(server, LIFETIME_SECONDS))
    retired_client = api_call._clients._client
    stream = await api_call.stream("GET", "/stream", typing.Dict[str, object])
    clock.advance_past_lifetime()
    await api_call.get("/", entity_type=typing.Dict[str, bool])
    current_client = api_call._clients._client

    await api_call.aclose()

    assert retired_client.is_closed is True
    assert current_client.is_closed is True
    await stream.aclose()


class _FakeClient:
    """A sync client that records whether it was closed."""

    def __init__(self, close_error: typing.Optional[Exception] = None) -> None:
        self.is_closed = False
        self._close_error = close_error

    def close(self) -> None:
        if self._close_error is not None:
            raise self._close_error
        self.is_closed = True


def test_lease_freed_by_the_garbage_collector_during_rotation_does_not_deadlock(
    clock: _Clock,
) -> None:
    """Test that a lease freed by the garbage collector mid-rotation does not hang."""
    collect_while_building = threading.Event()

    def build_client() -> _FakeClient:
        if collect_while_building.is_set():
            gc.collect()
        return _FakeClient()

    clients = ClientRotation(build_client, LIFETIME_SECONDS)
    first_client = clients._client

    def abandon_lease() -> None:
        stream = types.SimpleNamespace()
        stream.lease = clients.lease()
        stream.lease.__enter__()
        stream.cycle = stream

    def send_request() -> None:
        with clients.lease():
            pass

    request = threading.Thread(target=send_request, daemon=True)
    gc.disable()
    try:
        abandon_lease()
        collect_while_building.set()
        clock.advance_past_lifetime()
        request.start()
        request.join(_WAIT_SECONDS)
    finally:
        gc.enable()

    assert request.is_alive() is False
    assert first_client.is_closed is True


def test_closed_client_is_not_replaced_once_its_lifetime_passes(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that a request after closing still fails once the lifetime has passed."""
    api_call = ApiCall(_config(server, LIFETIME_SECONDS))
    api_call.get("/", entity_type=typing.Dict[str, bool])
    closed_client = api_call._clients._client
    api_call.close()
    clock.advance_past_lifetime()

    with pytest.raises(RuntimeError, match="client has been closed"):
        api_call.get("/", entity_type=typing.Dict[str, bool])

    assert api_call._clients._client is closed_client


async def test_async_closed_client_is_not_replaced_once_its_lifetime_passes(
    server: _Server,
    clock: _Clock,
) -> None:
    """Test that an async request after closing still fails after the lifetime."""
    api_call = AsyncApiCall(_config(server, LIFETIME_SECONDS))
    await api_call.get("/", entity_type=typing.Dict[str, bool])
    closed_client = api_call._clients._client
    await api_call.aclose()
    clock.advance_past_lifetime()

    with pytest.raises(RuntimeError, match="client has been closed"):
        await api_call.get("/", entity_type=typing.Dict[str, bool])

    assert api_call._clients._client is closed_client


async def test_async_cancelled_request_still_closes_its_retired_client(
    clock: _Clock,
) -> None:
    """Test that cancelling the last request on a retired client still closes it."""
    retired_client = _FakeAsyncClient()
    built_clients = iter([retired_client, _FakeAsyncClient()])
    clients = AsyncClientRotation(built_clients.__next__, LIFETIME_SECONDS)
    finish_request = asyncio.Event()

    async def send_slow_request() -> None:
        async with clients.lease():
            await finish_request.wait()

    slow_request = asyncio.ensure_future(send_slow_request())
    await asyncio.sleep(0)
    clock.advance_past_lifetime()
    async with clients.lease():
        pass

    finish_request.set()
    await asyncio.wait_for(retired_client.close_started.wait(), _WAIT_SECONDS)
    slow_request.cancel()
    with pytest.raises(asyncio.CancelledError):
        await slow_request

    retired_client.allow_close.set()
    await asyncio.sleep(0)
    assert retired_client.is_closed is True


async def test_async_close_closes_every_client_when_one_fails(clock: _Clock) -> None:
    """Test that closing closes every async client, even when one fails to close."""
    retired_client = _FakeAsyncClient()
    current_client = _FakeAsyncClient(close_error=OSError("close failed"))
    built_clients = iter([retired_client, current_client])
    clients = AsyncClientRotation(built_clients.__next__, LIFETIME_SECONDS)
    retired_client.allow_close.set()
    current_client.allow_close.set()

    async with clients.lease():
        clock.advance_past_lifetime()
        async with clients.lease():
            pass

        with pytest.raises(OSError, match="close failed"):
            await clients.aclose()

    assert retired_client.is_closed is True


async def test_async_cancelled_close_still_closes_every_client(clock: _Clock) -> None:
    """Test that cancelling closing partway still closes every async client."""
    retired_client = _FakeAsyncClient()
    current_client = _FakeAsyncClient()
    built_clients = iter([retired_client, current_client])
    clients = AsyncClientRotation(built_clients.__next__, LIFETIME_SECONDS)

    async with clients.lease():
        clock.advance_past_lifetime()
        async with clients.lease():
            pass

        closing = asyncio.ensure_future(clients.aclose())
        await asyncio.wait_for(current_client.close_started.wait(), _WAIT_SECONDS)
        closing.cancel()
        with pytest.raises(asyncio.CancelledError):
            await closing

    retired_client.allow_close.set()
    current_client.allow_close.set()
    await asyncio.sleep(0)
    assert retired_client.is_closed is True
    assert current_client.is_closed is True


def test_close_closes_every_client_when_one_fails(clock: _Clock) -> None:
    """Test that closing closes every client, even when one fails to close."""
    retired_client = _FakeClient()
    current_client = _FakeClient(close_error=OSError("close failed"))
    built_clients = iter([retired_client, current_client])
    clients = ClientRotation(built_clients.__next__, LIFETIME_SECONDS)

    with clients.lease():
        clock.advance_past_lifetime()
        with clients.lease():
            pass

        with pytest.raises(OSError, match="close failed"):
            clients.close()

    assert retired_client.is_closed is True


def test_new_client_reuses_the_ca_bundle_loaded_at_start_up(
    server: _Server,
    clock: _Clock,
    tmp_path: pathlib.Path,
) -> None:
    """Test that replacing the client still works once the CA bundle file is gone."""
    ca_bundle = tmp_path / "ca.pem"
    shutil.copy(certifi.where(), ca_bundle)
    with ApiCall(_config(server, LIFETIME_SECONDS, verify=str(ca_bundle))) as api_call:
        api_call.get("/", entity_type=typing.Dict[str, bool])
        first_client = api_call._clients._client
        ca_bundle.unlink()
        clock.advance_past_lifetime()

        assert api_call.get("/", entity_type=typing.Dict[str, bool]) == {"ok": True}
        assert api_call._clients._client is not first_client


async def test_async_new_client_reuses_the_ca_bundle_loaded_at_start_up(
    server: _Server,
    clock: _Clock,
    tmp_path: pathlib.Path,
) -> None:
    """Test that replacing the async client still works once the CA bundle is gone."""
    ca_bundle = tmp_path / "ca.pem"
    shutil.copy(certifi.where(), ca_bundle)
    async with AsyncApiCall(
        _config(server, LIFETIME_SECONDS, verify=str(ca_bundle)),
    ) as api_call:
        await api_call.get("/", entity_type=typing.Dict[str, bool])
        first_client = api_call._clients._client
        ca_bundle.unlink()
        clock.advance_past_lifetime()

        response = await api_call.get("/", entity_type=typing.Dict[str, bool])
        assert response == {"ok": True}
        assert api_call._clients._client is not first_client
