from functools import lru_cache
from typing import Callable, List

import gevent

from . import AbstractEngine, AbstractWaiter, UnhandledExceptions


class GeventEngine(AbstractEngine):

    def create_task(self, fn: Callable) -> gevent.Greenlet:
        return gevent.spawn(fn)

    def waiter_factory(self, fs):
        return GeventWaiter(fs)


class GeventWaiter(AbstractWaiter):

    def __init__(self, fs: List[gevent.Greenlet]):
        self._fs = fs

    def __call__(self, *, suppress_exceptions: bool=False,
                 fail_hard: bool=False):
        if not fail_hard:
            gevent.joinall(self._fs)
            if not suppress_exceptions:
                excs = self.exceptions()
                if excs:
                    raise UnhandledExceptions(excs)
        else:
            gevent.joinall(self._fs, raise_error=True)

    def stop(self):
        gevent.killall(self._fs)

    @lru_cache()
    def exceptions(self) -> List[Exception]:
        return [f.exception for f in self._fs if f.exception]
