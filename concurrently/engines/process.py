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
import os
import signal
from functools import lru_cache
from multiprocessing import Process as _Process
from multiprocessing import Queue
from typing import Callable, List, Sequence

from . import AbstractEngine, AbstractWaiter, UnhandledExceptions


class Process(_Process):
    def __init__(self, *a, result_q: Queue, **kw) -> None:
        super().__init__(*a, **kw)
        self._result_q = result_q

    def run(self) -> None:
        try:
            super().run()
        except Exception as e:
            self._result_q.put(e)
        except KeyboardInterrupt:
            self._result_q.put(None)
        else:
            self._result_q.put(None)


class ProcessWaiter(AbstractWaiter):
    def __init__(self, fs: List[Process], result_q: Queue) -> None:
        self._fs = fs
        self._result_q = result_q
        self._exceptions: List[Exception] = []

    def __call__(
        self, *, suppress_exceptions: bool = False, fail_hard: bool = False
    ) -> None:
        for _ in range(len(self._fs)):
            exc = self._result_q.get()
            if exc and fail_hard:
                for f in self._fs:
                    if f.pid:
                        os.kill(f.pid, signal.SIGINT)
                for f in self._fs:
                    f.join()
                raise exc
            if exc:
                self._exceptions.append(exc)

        if not suppress_exceptions and self.exceptions():
            raise UnhandledExceptions(self.exceptions())

    def stop(self) -> None:
        for f in self._fs:
            if f.pid:
                os.kill(f.pid, signal.SIGINT)
        self(suppress_exceptions=True)

    @lru_cache()
    def exceptions(self) -> Sequence[Exception]:
        return tuple(self._exceptions)


class ProcessEngine(AbstractEngine):
    def __init__(self) -> None:
        self._result_q: Queue = Queue()

    def create_task(self, fn: Callable[[], None]) -> Process:
        p = Process(target=fn, result_q=self._result_q)
        p.start()
        return p

    def waiter_factory(self, fs) -> ProcessWaiter:
        return ProcessWaiter(fs, self._result_q)
