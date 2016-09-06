import abc
from typing import List


class AbstractEngine(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def waiter_factory(self, fs) -> 'AbstractWaiter':
        raise NotImplementedError


class AbstractWaiter(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __call__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError

    @abc.abstractmethod
    def exceptions(self) -> List[Exception]:
        raise NotImplementedError
