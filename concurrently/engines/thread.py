import ctypes
import threading
import time
from functools import lru_cache
from queue import Queue
from typing import Callable, List

from . import AbstractEngine, AbstractWaiter, UnhandledExceptions


# from https://github.com/mosquito/crew/blob/master/crew/worker/thread.py
class KillableThread(threading.Thread):

    def __init__(self, *a, result_q: Queue, **kw):
        super().__init__(*a, **kw)
        self._result_q = result_q

    def kill(self, exc=SystemExit):
        if not self.isAlive():
            return False

        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self.ident), ctypes.py_object(exc))

        if res == 0:
            raise ValueError('nonexistent thread id')
        elif res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.ident, None)
            raise SystemError('PyThreadState_SetAsyncExc failed')

        while self.isAlive():
            time.sleep(0.01)

        return True

    def run(self):
        try:
            super().run()
        except Exception as e:
            self._result_q.put(e)
        except SystemExit:
            self._result_q.put(None)
        else:
            self._result_q.put(None)


class ThreadWaiter(AbstractWaiter):

    def __init__(self, fs: List[KillableThread], result_q: Queue):
        self._fs = fs
        self._result_q = result_q
        self._exceptions = []

    def __call__(self, *, suppress_exceptions=False, fail_hard=False):
        for _ in range(len(self._fs)):
            exc = self._result_q.get()
            if exc and fail_hard:
                [f.kill() for f in self._fs]
                [f.join() for f in self._fs]
                raise exc
            elif exc:
                self._exceptions.append(exc)

        if not suppress_exceptions and self.exceptions():
            raise UnhandledExceptions(self.exceptions())

    def stop(self):
        for f in self._fs:
            f.kill()
        self(suppress_exceptions=True)

    @lru_cache()
    def exceptions(self) -> List[Exception]:
        return self._exceptions


class ThreadEngine(AbstractEngine):

    def __init__(self):
        self._result_q = Queue()

    def create_task(self, fn: Callable[[], None]) -> KillableThread:
        tr = KillableThread(target=fn, result_q=self._result_q)
        tr.start()
        return tr

    def waiter_factory(self, fs):
        return ThreadWaiter(fs, result_q=self._result_q)
