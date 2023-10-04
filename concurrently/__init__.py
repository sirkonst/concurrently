import sys
from types import ModuleType
from typing import Sequence

from ._concurrently import concurrently, get_default_engine, set_default_engine
from .engines import UnhandledExceptions
from .engines.asyncio import AsyncIOEngine, AsyncIOThreadEngine
from .engines.process import ProcessEngine
from .engines.thread import ThreadEngine

__all__ = [
    'concurrently',
    'get_default_engine',
    'set_default_engine',
    'UnhandledExceptions',
    'ThreadEngine',
    'ProcessEngine',
    'AsyncIOEngine',
    'AsyncIOThreadEngine',
]

set_default_engine(AsyncIOEngine)

try:
    from .engines.gevent import GeventEngine  # noqa:W0611

    __all__.append('GeventEngine')
except ImportError:
    pass


class Module(ModuleType):
    __all__: Sequence[str]

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if isinstance(attr, ImportError):
            raise attr

        return attr


module = Module(__name__)
module.__dict__.update(globals())
module.__all__ = __all__
sys.modules[__name__] = module
