import sys
from types import ModuleType

from ._concurrently import concurrently, get_default_engine, set_default_engine

__all__ = ['concurrently', 'get_default_engine', 'set_default_engine']


# -- engines:
from .engines import UnhandledExceptions
from .engines.thread import ThreadEngine
from .engines.process import ProcessEngine
from .engines.asyncio import AsyncIOEngine, AsyncIOThreadEngine

__all__.extend((
    'ThreadEngine', 'ProcessEngine', 'AsyncIOEngine', 'AsyncIOThreadEngine'
))

set_default_engine(AsyncIOEngine)

try:
    from .engines.gevent import GeventEngine
    __all__.append('GeventEngine')
except ImportError as e:
    GeventEngine = e


class Module(ModuleType):

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if isinstance(attr, ImportError):
            raise attr

        return attr


module = Module(__name__)
module.__dict__.update(globals())
module.__all__ = __all__
sys.modules[__name__] = module
