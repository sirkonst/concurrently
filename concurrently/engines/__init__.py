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
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError

    @abc.abstractmethod
    def exceptions(self) -> List[Exception]:
        raise NotImplementedError


class UnhandledExceptions(Exception):

    def __init__(self, exceptions):
        self.exceptions = exceptions
