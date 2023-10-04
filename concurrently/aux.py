import ctypes
import threading
import time
from typing import Type


# inspired by
# https://github.com/mosquito/crew/blob/master/crew/worker/thread.py
def kill_thread(
    thread: threading.Thread,
    exception: Type[BaseException] = KeyboardInterrupt,
) -> None:
    if not thread.ident:
        return None

    if not thread.is_alive():
        return None

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), ctypes.py_object(exception)
    )

    if res == 0:
        raise ValueError('nonexistent thread id')
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError('PyThreadState_SetAsyncExc failed')

    while thread.is_alive():
        time.sleep(0.01)
