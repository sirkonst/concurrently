"""
AsyncIOEngine
-------------

Runs code as asyncio coroutines::

    from concurrently import concurrently, AsyncIOEngine

    ...
    @concurrently(2, engine=AsyncIOEngine)
    async def fetch_urls():
        ...

    await fetch_urls()

.. autoclass:: concurrently.AsyncIOEngine


AsyncIOThreadEngine
-------------------

Runs code in threads with asyncio::

    from concurrently import concurrently, AsyncIOThreadEngine

    ...
    @concurrently(2, engine=AsyncIOThreadEngine)
    def fetch_urls():  # not async def
        ...

    await fetch_urls()

.. autoclass:: concurrently.AsyncIOThreadEngine
"""
import asyncio
import sys
from collections.abc import Coroutine
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Callable, List, Sequence

from . import AbstractEngine, AbstractWaiter, UnhandledExceptions

_PY_VERSION = float(sys.version_info[0]) + sys.version_info[1] / 10


class AsyncIOWaiter(AbstractWaiter):
    def __init__(self, fs: List[asyncio.Future]) -> None:
        self._fs = fs

    async def __call__(  # type: ignore[override]
        self, *, suppress_exceptions: bool = False, fail_hard: bool = False
    ) -> None:
        when = asyncio.FIRST_EXCEPTION if fail_hard else asyncio.ALL_COMPLETED
        done, pending = await asyncio.wait(self._fs, return_when=when)

        if fail_hard:
            for f in done:
                e = f.exception()
                if not e:
                    continue

                for p in pending:
                    p.cancel()

                await asyncio.wait(pending)

                raise e

        if not suppress_exceptions and self.exceptions():
            raise UnhandledExceptions(self.exceptions())

    async def stop(self) -> None:  # type: ignore[override]
        for f in self._fs:
            f.cancel()
        await self(suppress_exceptions=True)

    @lru_cache()
    def exceptions(self) -> Sequence[Exception]:
        return tuple(
            f.exception()  # type: ignore[misc]
            for f in self._fs
            if not f.cancelled()
            if f.exception()
        )


class AsyncIOEngine(AbstractEngine):
    def __init__(self) -> None:
        super().__init__()
        self.loop = _get_running_loop()

    def create_task(self, fn: Coroutine) -> asyncio.Future:
        assert asyncio.iscoroutinefunction(
            fn
        ), 'Decorated function `{}` must be coroutine'.format(fn.__name__)

        return _create_task(fn())

    def waiter_factory(self, fs: List[asyncio.Future]) -> AsyncIOWaiter:
        return AsyncIOWaiter(fs=fs)


class AsyncIOThreadEngine(AsyncIOEngine):
    _pool = ThreadPoolExecutor()

    def create_task(self, fn: Callable[[], None]) -> asyncio.Future:  # type: ignore[override]
        assert not asyncio.iscoroutinefunction(
            fn
        ), 'Decorated function `{}` must be regular not a coroutine'.format(
            fn.__name__
        )

        return self.loop.run_in_executor(self._pool, fn)


def _create_task(coro: Coroutine) -> asyncio.Task:
    if _PY_VERSION >= 3.7:
        return asyncio.create_task(coro)

    return _get_running_loop().create_task(coro)


def _get_running_loop() -> asyncio.AbstractEventLoop:
    if _PY_VERSION >= 3.7:
        return asyncio.get_running_loop()

    return asyncio.get_event_loop()
