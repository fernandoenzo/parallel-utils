# /usr/bin/env python3
# encoding:utf-8


from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Union


class AbstractMonitor(ABC):
    '''
    An abstract class to ease the handle and synchronization of multiple threads or processes.
    '''

    @abstractmethod
    def lock_code(self, uid: Union[str, int], max_threads: int):
        '''
        Only allow up to max_threads threads to enter the code included between this function and
        the 'unlock_code()' function.
        :param uid: Unique identifier for the code snippet.
        :param max_threads: Maximum number of threads that can access the code simultaneously.
        '''
        raise NotImplementedError

    @abstractmethod
    def lock_priority_code(self, uid: Union[str, int], order: int, total: int):
        '''
        Synchronizes different threads to execute some pieces of code in a specific order to avoid
        race conditions.
        :param uid: Unique identifier for the set of code snippets.
        :param order: The priority of the code protected with this function's uid.
        :param total: The total number of pieces of code to synchronize with this function's uid.
        '''
        raise NotImplementedError

    @abstractmethod
    def unlock_code(self, uid: Union[str, int]):
        '''
        Sets the limit to where a piece of code is locked with 'lock_code' or 'lock_priority_code' methods.
        :param uid: Unique identifier of the 'lock_code' or 'lock_priority_code' function.
        '''
        raise NotImplementedError

    @contextmanager
    def synchronized(self, uid: Union[str, int], max_threads: int = 1):
        '''
        Context manager for 'lock_code' function
        :param uid: Unique identifier for the code snippet.
        :param max_threads: Maximum number of threads that can access the code simultaneously.
        '''
        self.lock_code(uid, max_threads)
        try:
            yield
        finally:
            self.unlock_code(uid)

    @contextmanager
    def synchronized_priority(self, uid: Union[str, int], order: int, total: int = None):
        '''
        Context manager for 'lock_priority_code' function
        :param uid: Unique identifier for the set of code snippets.
        :param order: The priority of the code protected with this function's uid.
        :param total: The total number of pieces of code to synchronize with this function's uid.
        '''
        self.lock_priority_code(uid, order, total)
        try:
            yield
        finally:
            self.unlock_code(uid)
