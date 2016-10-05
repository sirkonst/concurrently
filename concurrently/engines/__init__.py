"""
Supported engines
=================

.. automodule:: concurrently.engines.asyncio
.. automodule:: concurrently.engines.thread
.. automodule:: concurrently.engines.process
.. automodule:: concurrently.engines.gevent
"""
import abc
from typing import List


class AbstractEngine(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_task(self, fn):
        raise NotImplementedError

    @abc.abstractmethod
    def waiter_factory(self, fs) -> 'AbstractWaiter':
        raise NotImplementedError


class AbstractWaiter(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __call__(self, *,
                 suppress_exceptions: bool=False, fail_hard: bool=False):
        """
        The call blocks until the completion of all concurrent functions.

        All exceptions in concurrent functions are captured and re-raise as
        :class:`UnhandledExceptions`.

        You can customize this behavior with following options:

        :param suppress_exceptions: don't raise :class:`UnhandledExceptions`
        :param fail_hard: stop all functions and raise error if one of
            function abort with error
        """
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self):
        """
        Interrupts execution functions.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def exceptions(self) -> List[Exception]:
        """
        Returns list of all exception.

        Useful with option ``suppress_exceptions``.
        """
        raise NotImplementedError


class UnhandledExceptions(Exception):
    """
    :param exceptions: list of exception
    """
    def __init__(self, exceptions):
        self.exceptions = exceptions
