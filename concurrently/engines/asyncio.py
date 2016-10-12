"""
AsyncIOEngine
-------------

Runs code as asyncio coroutines::

    from concurrently import concurrently, AsyncIOEngine

    ...
    @concurrently(2, engine=AsyncIOEngine, loop=loop)  # loop is option
    async def fetch_urls():
        ...

    await fetch_urls()

.. autoclass:: concurrently.AsyncIOEngine


AsyncIOThreadEngine
-------------------

Runs code in threads with asyncio::

    from concurrently import concurrently, AsyncIOThreadEngine

    ...
    @concurrently(2, engine=AsyncIOThreadEngine, loop=loop)
    def fetch_urls():  # not async def
        ...

    await fetch_urls()

.. autoclass:: concurrently.AsyncIOThreadEngine
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Callable, List

from . import AbstractEngine, AbstractWaiter, UnhandledExceptions


class AsyncIOWaiter(AbstractWaiter):

    def __init__(self, fs: List[asyncio.Future], loop: asyncio.BaseEventLoop):
        self._fs = fs
        self._loop = loop

    async def __call__(self, *, suppress_exceptions=False, fail_hard=False):
        when = asyncio.FIRST_EXCEPTION if fail_hard else asyncio.ALL_COMPLETED
        done, pending = await asyncio.wait(
            self._fs, loop=self._loop, return_when=when
        )

        if fail_hard:
            f = next(filter(lambda x: x.exception(), done), None)
            if f:
                [p.cancel() for p in pending]
                await asyncio.wait(pending, loop=self._loop)
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
    """
    :param loop: specific asyncio loop or use default if `None`
    """
    def __init__(self, *, loop: asyncio.BaseEventLoop=None):
        super().__init__()
        self.loop = loop or asyncio.get_event_loop()

    def create_task(self, fn: asyncio.coroutine) -> asyncio.Future:
        assert asyncio.iscoroutinefunction(fn), \
            'Decorated function `{}` must be coroutine'.format(fn.__name__)

        return self.loop.create_task(fn())

    def waiter_factory(self, fs: List[asyncio.Future]):
        return AsyncIOWaiter(fs=fs, loop=self.loop)


class AsyncIOThreadEngine(AsyncIOEngine):
    """
    :param loop: specific asyncio loop or use default if `None`
    """
    _pool = ThreadPoolExecutor()

    def create_task(self, fn: Callable[[], None]) -> asyncio.Future:
        assert not asyncio.iscoroutinefunction(fn), \
            'Decorated function `{}` must be regular not a coroutine'.format(
                fn.__name__
            )

        return self.loop.run_in_executor(self._pool, fn)
