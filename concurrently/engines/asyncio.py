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
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Callable, List

from . import AbstractEngine, AbstractWaiter, UnhandledExceptions

_PY_VERSION = float(sys.version_info[0]) + sys.version_info[1] / 10


class AsyncIOWaiter(AbstractWaiter):

    def __init__(self, fs: List[asyncio.Future]):
        self._fs = fs

    async def __call__(self, *, suppress_exceptions=False, fail_hard=False):
        when = asyncio.FIRST_EXCEPTION if fail_hard else asyncio.ALL_COMPLETED
        done, pending = await asyncio.wait(self._fs, return_when=when)

        if fail_hard:
            f = next(filter(lambda x: x.exception(), done), None)
            if f:
                [p.cancel() for p in pending]
                await asyncio.wait(pending)
                raise f.exception()

        if not suppress_exceptions and self.exceptions():
            raise UnhandledExceptions(self.exceptions())

    async def stop(self):
        for f in self._fs:
            f.cancel()
        await self(suppress_exceptions=True)

    @lru_cache()
    def exceptions(self) -> List[Exception]:
        exc_list = []
        for f in self._fs:
            if f.cancelled():
                continue

            exc = f.exception()
            if exc:
                exc_list.append(exc)

        return exc_list


class AsyncIOEngine(AbstractEngine):

    def __init__(self):
        super().__init__()
        self.loop = _get_running_loop()

    def create_task(self, fn: asyncio.coroutine) -> asyncio.Future:
        assert asyncio.iscoroutinefunction(fn), \
            'Decorated function `{}` must be coroutine'.format(fn.__name__)

        return _create_task(fn())

    def waiter_factory(self, fs: List[asyncio.Future]):
        return AsyncIOWaiter(fs=fs)


class AsyncIOThreadEngine(AsyncIOEngine):
    _pool = ThreadPoolExecutor()

    def create_task(self, fn: Callable[[], None]) -> asyncio.Future:
        assert not asyncio.iscoroutinefunction(fn), \
            'Decorated function `{}` must be regular not a coroutine'.format(
                fn.__name__
            )

        return self.loop.run_in_executor(self._pool, fn)


def _create_task(coro: asyncio.coroutine) -> asyncio.Task:
    if _PY_VERSION >= 3.7:
        return asyncio.create_task(coro)

    return _get_running_loop().create_task(coro)


def _get_running_loop() -> asyncio.AbstractEventLoop:
    if _PY_VERSION >= 3.7:
        return asyncio.get_running_loop()

    return asyncio.get_event_loop()
