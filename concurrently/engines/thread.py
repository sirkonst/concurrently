import ctypes
import threading
import time
from queue import Queue
from typing import Callable, List

from . import AbstractEngine, AbstractWaiter


# from https://github.com/mosquito/crew/blob/master/crew/worker/thread.py
class KillableThread(threading.Thread):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._exception = Queue(1)

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
            self._exception.put(e)

    def exception(self):
        if self._exception.empty():
            return
        else:
            return self._exception.get()


class ThreadWaiter(AbstractWaiter):

    def __init__(self, fs: List[KillableThread]):
        self.fs = fs

    def __call__(self):
        for f in self.fs:
            f.join()

    def stop(self):
        for f in self.fs:
            f.kill()
        self()

    def exceptions(self) -> List[Exception]:
        excs = []
        for f in self.fs:
            e = f.exception()
            if e:
                excs.append(e)
        return excs


class ThreadEngine(AbstractEngine):

    def create_task(self, fn: Callable[[], None]) -> KillableThread:
        tr = KillableThread(target=fn)
        tr.start()
        return tr

    def waiter_factory(self, fs):
        return ThreadWaiter(fs)
