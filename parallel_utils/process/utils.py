# /usr/bin/env python3
# encoding:utf-8


from concurrent.futures._base import Future
from concurrent.futures.process import ProcessPoolExecutor
from typing import Callable, Any

from parallel_utils.thread import create_thread


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
    shutdown = lambda fut: create_thread(tp.shutdown, wait=True)  # Necessary since wait=False is broken
    future.add_done_callback(shutdown)
    return future
