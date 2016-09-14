from concurrent.futures import ThreadPoolExecutor, Future, wait
from functools import lru_cache
from typing import Callable, List

from . import AbstractEngine, AbstractWaiter, UnhandledExceptions


class ThreadPoolWaiter(AbstractWaiter):

    def __init__(self, fs: List[Future], pool: ThreadPoolExecutor):
        self.fs = fs
        self.pool = pool

    def __call__(self, *, suppress_exceptions=False):
        wait(self.fs)

        if not suppress_exceptions and self.exceptions():
            raise UnhandledExceptions(self.exceptions())

    def stop(self):
        for f in self.fs:
            f.cancel()
        self(suppress_exceptions=True)

    @lru_cache()
    def exceptions(self) -> List[Exception]:
        return [f.exception() for f in self.fs if f.exception()]


class ThreadPoolEngine(AbstractEngine):
    pool = ThreadPoolExecutor()

    def __init__(self, *, pool: ThreadPoolExecutor=None):
        super().__init__()
        if pool:
            self.pool = pool

    def create_task(self, fn: Callable[[], None]) -> Future:
        return self.pool.submit(fn)

    def waiter_factory(self, fs):
        return ThreadPoolWaiter(fs, pool=self.pool)
