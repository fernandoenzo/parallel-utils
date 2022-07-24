# /usr/bin/env python3
# encoding:utf-8


from concurrent.futures._base import Future
from concurrent.futures.process import ProcessPoolExecutor
from typing import Callable, Any


def create_process(func: Callable, *args: Any, **kwargs: Any) -> Future:
    '''
    Calls a function in its own process
    :param func: The function to be called
    :param args: The function arguments
    :param kwargs: The function keyword arguments
    :return: The created Future object, from which we can call 'result()' to get the function return value.
    '''
    tp = ProcessPoolExecutor(max_workers=1)
    future = tp.submit(func, *args, **kwargs)
    tp.shutdown(wait=False)
    return future
