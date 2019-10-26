import ctypes
import sys
import threading
import time

_PY_VERSION = float(sys.version_info[0]) + sys.version_info[1] / 10


# inspired by https://github.com/mosquito/crew/blob/master/crew/worker/thread.py
def kill_thread(
    thread: threading.Thread, exception: BaseException=KeyboardInterrupt
) -> None:
    is_alive = thread.is_alive if _PY_VERSION >= 3.7 else thread.isAlive

    if not is_alive():
        return

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), ctypes.py_object(exception)
    )

    if res == 0:
        raise ValueError('nonexistent thread id')
    elif res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError('PyThreadState_SetAsyncExc failed')

    while is_alive():
        time.sleep(0.01)
