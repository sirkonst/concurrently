from threading import local
from typing import Callable

from concurrently.engines import AbstractEngine, AbstractWaiter


__default_engine = local()
__default_engine.cls = None


def set_default_engine(engine_cls: AbstractEngine):
    __default_engine.cls = engine_cls


def get_default_engine() -> AbstractEngine:
    return __default_engine.cls


class Concurrently:
    def __init__(self, concurrency: int=1, *,
                 engine: AbstractEngine=None, **engine_kw):
        self.concurrency = concurrency
        if not engine:
            engine = get_default_engine()
        self.engine = engine(**engine_kw)

    def __call__(self, fn: Callable[[], None]) -> 'AbstractWaiter':
        fs = []
        for _ in range(self.concurrency):
            fs.append(self.engine.create_task(fn))

        return self.engine.waiter_factory(fs)


concurrently = Concurrently
