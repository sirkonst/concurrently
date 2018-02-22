"""
ThreadEngine
------------

Runs code in system threads::

    from concurrently import concurrently, ThreadEngine

    ...
    @concurrently(2, engine=ThreadEngine)
    def fetch_urls():  # not async def
        ...

    fetch_urls()  # not await

.. autoclass:: concurrently.ThreadEngine
"""
import threading
from functools import lru_cache
from queue import Queue
from typing import Callable, List

from concurrently.aux import kill_thread
from . import AbstractEngine, AbstractWaiter, UnhandledExceptions


class Thread(threading.Thread):

    def __init__(self, *a, result_q: Queue, **kw):
        super().__init__(*a, **kw)
        self._result_q = result_q

    def run(self):
        try:
            super().run()
        except Exception as e:
            self._result_q.put(e)
        except KeyboardInterrupt:
            self._result_q.put(None)
        else:
            self._result_q.put(None)


class ThreadWaiter(AbstractWaiter):

    def __init__(self, fs: List[Thread], result_q: Queue):
        self._fs = fs
        self._result_q = result_q
        self._exceptions = []

    def __call__(self, *, suppress_exceptions=False, fail_hard=False):
        for _ in range(len(self._fs)):
            exc = self._result_q.get()
            if exc and fail_hard:
                [kill_thread(f) for f in self._fs]
                [f.join() for f in self._fs]
                raise exc
            elif exc:
                self._exceptions.append(exc)

        if not suppress_exceptions and self.exceptions():
            raise UnhandledExceptions(self.exceptions())

    def stop(self):
        for f in self._fs:
            kill_thread(f)
        self(suppress_exceptions=True)

    @lru_cache()
    def exceptions(self) -> List[Exception]:
        return self._exceptions


class ThreadEngine(AbstractEngine):

    def __init__(self):
        self._result_q = Queue()

    def create_task(self, fn: Callable[[], None]) -> Thread:
        tr = Thread(target=fn, result_q=self._result_q)
        tr.start()
        return tr

    def waiter_factory(self, fs):
        return ThreadWaiter(fs, result_q=self._result_q)
