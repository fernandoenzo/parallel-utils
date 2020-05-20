# /usr/bin/env python3
# encoding:utf-8


from concurrent.futures._base import Future
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, Callable


def create_thread(func: Callable, *args: Any, **kwargs: Any) -> Future:
    '''
    Calls a function in its own thread
    :param func: The function to be called
    :param args: The function arguments
    :param kwargs: The function keyword arguments
    :return: The created Future object, from which we can call 'result()' as if it were a 'join()'
    '''
    tp = ThreadPoolExecutor(max_workers=1)
    future = tp.submit(func, *args, **kwargs)
    tp.shutdown(wait=False)
    return future
