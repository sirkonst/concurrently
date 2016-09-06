import multiprocessing
import os
import signal
from typing import Callable, List

from . import AbstractEngine, AbstractWaiter


class Process(multiprocessing.Process):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._exception = multiprocessing.Queue(1)

    def run(self):
        try:
            super().run()
        except Exception as e:
            self._exception.put(e)

    def exception(self):
        if self._exception.empty():
            return
        else:
            return self._exception.get()


class ProcessWaiter(AbstractWaiter):

    def __init__(self, fs: List[Process]):
        self.fs = fs

    def __call__(self):
        for f in self.fs:
            f.join()

    def stop(self):
        for f in self.fs:
            os.kill(f.pid, signal.SIGINT)
        self()

    def exceptions(self) -> List[Exception]:
        excs = []
        for f in self.fs:
            e = f.exception()
            if e:
                excs.append(e)
        return excs


class ProcessEngine(AbstractEngine):

    def create_task(self, fn: Callable[[], None]) -> Process:
        p = Process(target=fn)
        p.start()
        return p

    def waiter_factory(self, fs):
        return ProcessWaiter(fs)
