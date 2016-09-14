from concurrent.futures import (
    ThreadPoolExecutor, Future, wait, ALL_COMPLETED, FIRST_EXCEPTION
)
from functools import lru_cache
from typing import Callable, List

from . import AbstractEngine, AbstractWaiter, UnhandledExceptions


class ThreadPoolWaiter(AbstractWaiter):

    def __init__(self, fs: List[Future]):
        self._fs = fs

    def __call__(self, *, suppress_exceptions=False, fail_hard=False):
        when = FIRST_EXCEPTION if fail_hard else ALL_COMPLETED
        done, pending = wait(self._fs, return_when=when)

        if fail_hard:
            f = next(filter(lambda x: x.exception(), done), None)
            if f:
                [p.cancel() for p in pending]
                wait(pending)
                raise f.exception()

        if not suppress_exceptions and self.exceptions():
            raise UnhandledExceptions(self.exceptions())

    def stop(self):
        for f in self._fs:
            f.cancel()
        self(suppress_exceptions=True)

    @lru_cache()
    def exceptions(self) -> List[Exception]:
        return [f.exception() for f in self._fs if f.exception()]


class ThreadPoolEngine(AbstractEngine):
    pool = ThreadPoolExecutor()

    def __init__(self, *, pool: ThreadPoolExecutor=None):
        if pool:
            self.pool = pool

    def create_task(self, fn: Callable[[], None]) -> Future:
        return self.pool.submit(fn)

    def waiter_factory(self, fs):
        return ThreadPoolWaiter(fs)
