"""
ProcessEngine
-------------

Runs code in system process::

    from concurrently import concurrently, ProcessEngine

    ...
    @concurrently(2, engine=ProcessEngine)
    def fetch_urls():
        ...

    fetch_urls()

.. autoclass::  concurrently.ProcessEngine
"""
from multiprocessing import Queue, Process as _Process
import os
import signal
from functools import lru_cache
from typing import Callable, List

from . import AbstractEngine, AbstractWaiter, UnhandledExceptions


class Process(_Process):

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


class ProcessWaiter(AbstractWaiter):

    def __init__(self, fs: List[Process], result_q: Queue):
        self._fs = fs
        self._result_q = result_q
        self._exceptions = []

    def __call__(self, *, suppress_exceptions=False, fail_hard=False):
        for _ in range(len(self._fs)):
            exc = self._result_q.get()
            if exc and fail_hard:
                [os.kill(f.pid, signal.SIGINT) for f in self._fs]
                [f.join() for f in self._fs]
                raise exc
            elif exc:
                self._exceptions.append(exc)

        if not suppress_exceptions and self.exceptions():
            raise UnhandledExceptions(self.exceptions())

    def stop(self):
        for f in self._fs:
            os.kill(f.pid, signal.SIGINT)
        self(suppress_exceptions=True)

    @lru_cache()
    def exceptions(self) -> List[Exception]:
        return self._exceptions


class ProcessEngine(AbstractEngine):

    def __init__(self):
        self._result_q = Queue()

    def create_task(self, fn: Callable[[], None]) -> Process:
        p = Process(target=fn, result_q=self._result_q)
        p.start()
        return p

    def waiter_factory(self, fs):
        return ProcessWaiter(fs, self._result_q)
