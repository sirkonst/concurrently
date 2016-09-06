import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List

from . import AbstractEngine, AbstractWaiter


class AsyncIOWaiter(AbstractWaiter):

    def __init__(self, fs: List[asyncio.Future], loop: asyncio.BaseEventLoop):
        self.fs = fs
        self.loop = loop

    async def __call__(self):
        await asyncio.wait(self.fs, loop=self.loop)

    async def stop(self):
        for f in self.fs:
            f.cancel()
        await self()

    def exceptions(self) -> List[Exception]:
        exc_list = []
        for f in self.fs:
            exc = f.exception()
            if exc:
                exc_list.append(exc)

        return exc_list


class AsyncIOEngine(AbstractEngine):

    def __init__(self, *, loop: asyncio.BaseEventLoop=None):
        super().__init__()
        self.loop = loop or asyncio.get_event_loop()

    def create_task(self, fn: asyncio.coroutine) -> asyncio.Future:
        return self.loop.create_task(fn())

    def waiter_factory(self, fs: List[asyncio.Future]):
        return AsyncIOWaiter(fs=fs, loop=self.loop)


class AsyncIOThreadEngine(AsyncIOEngine):

    def __init__(self, *, loop=None):
        super().__init__(loop=loop)
        self.pool = ThreadPoolExecutor()  # TODO: shutdown pool

    def create_task(self, fn: Callable[[], None]) -> asyncio.Future:
        return self.loop.run_in_executor(self.pool, fn)
