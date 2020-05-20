# /usr/bin/env python3
# encoding:utf-8


from typing import Union

from private_attrs import PrivateAttrs

from parallel_utils.common import AbstractMonitor
from parallel_utils.thread import Monitor


def StaticMonitor():
    p = PrivateAttrs()
    p.monitor_static = Monitor()

    class StaticMonitor(AbstractMonitor):
        '''
        A static class to ease the handle and synchronization of multiple processes.
        You shall not instantiate this class, as it'd be meaningless.
        Even if you do, the 'uids' used in this class are shared among all instances,
        so you shall never repeat them.
        '''

        @staticmethod
        def lock_code(uid: Union[str, int], max_threads: int = 1):
            return p.monitor_static.lock_code(uid=uid, max_threads=max_threads)

        @staticmethod
        def lock_priority_code(uid: Union[str, int], order: int = 1, total: int = 1):
            p.monitor_static.lock_priority_code(uid=uid, order=order, total=total)

        @staticmethod
        def unlock_code(uid: Union[str, int]):
            return p.monitor_static.unlock_code(uid=uid)

    StaticMonitor.__qualname__ = 'StaticMonitor'

    return StaticMonitor


StaticMonitor = StaticMonitor()
