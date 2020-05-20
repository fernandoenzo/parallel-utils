# /usr/bin/env python3
# encoding:utf-8


from functools import wraps
from threading import Semaphore
from typing import Union

from parallel_utils.thread import Monitor


def synchronized(max_threads: int = 1):
    '''
    This decorator will allow only up to max_threads threads to run this function simultaneously.
    :param max_threads: Maximum number of threads.
    '''

    s = Semaphore(max_threads)

    def locked(func):
        @wraps(func)
        def locked_func(*args, **kw_args):
            s.acquire()
            func(*args, **kw_args)
            s.release()

        return locked_func

    return locked


def synchronized_priority(*args, **kwargs):
    m = Monitor()

    def synchronized_priority(uid: Union[str, int], order: int = 1, total: int = None):
        '''
        This decorator will synchronize different threads to execute some functions
        in a specific order to avoid race conditions.
        :param uid: Unique identifier for the set of code snippets.
        :param order: The priority of the function protected with this function's uid.
        :param total: The total number of functions to synchronize using this function's uid.
        '''

        def locked(func):
            @wraps(func)
            def locked_func(*args, **kw_args):
                m.lock_priority_code(uid=uid, order=order, total=total)
                func(*args, **kw_args)
                m.unlock_code(uid=uid)

            return locked_func

        return locked

    return synchronized_priority


synchronized_priority = synchronized_priority()
