# /usr/bin/env python3
# encoding:utf-8


from typing import Union

from private_attrs import PrivateAttrs

from parallel_utils.common import AbstractMonitor


def Monitor():
    p = PrivateAttrs(proxy=True)
    locker = p.manager.Semaphore(1)

    def lock_priority_code(self, uid: Union[str, int], order: int, total: int, max_threads: int):
        '''
        A private function that handles every use case. If total > 1, max_processes should be 1.
        :param self: A Monitor intance.
        :param uid: Unique identifier for the code protector (for the associated semaphores).
        :param order: The priority of the code locked with this function's uid.
        :param total: The total number of pieces of code implied with this function's uid.
        :param max_threads: Maximum number of processes that can access the code simultaneously.
        '''
        assert order > 0
        assert max_threads > 0
        semaphores = p.semaphores
        while True:
            locker.acquire()
            s = semaphores.get(uid)
            if s is not None:
                locker.release()
                break
            if total is None:
                setup_locker = p.setup_priority_lockers.get(uid)
                if setup_locker is None:
                    setup_locker = p.manager.Semaphore(0)
                    p.setup_priority_lockers[uid] = setup_locker
                locker.release()
                setup_locker.acquire()
            else:
                assert order <= total
                s = [p.manager.Semaphore(max_threads)]
                s.extend([p.manager.Semaphore(0) for _ in range(total - 1)])
                s = p.manager.list((tuple(s), 1))
                semaphores[uid] = s
                locker.release()
                setup_locker = p.setup_priority_lockers.get(uid)
                if setup_locker is not None:
                    [setup_locker.release() for _ in range(total)]
                    del p.setup_priority_lockers[uid]
                break
        s[0][order - 1].acquire()

    def unlock_code(self, uid: Union[str, int]):
        semaphores = p.semaphores
        s = semaphores.get(uid)
        total = len(s[0])
        order = s[1]
        s[1] = (s[1] + 1) % total
        s[0][order % total].release()

    class Monitor(AbstractMonitor):
        '''
        A class to ease the handle and synchronization of multiple processes.
        You can safely use a same 'uid' in two different instances of this class.
        However, you must never reuse an 'uid' in a same instance, even if you're calling
        'lock_code()' and 'lock_priority_code()' since they share the same namespace.
        '''

        def __init__(self):
            p.register_instance(self)

            # This attribute will store a tuple of semaphores per uid, so it'll be like:
            # semaphores = {'uid1': [(s1,), order], 'uid2': [(s2, s3, s4), order], ...}
            p.semaphores = p.manager.dict()
            p.setup_priority_lockers = p.manager.dict()

        def lock_code(self, uid: Union[str, int], max_threads: int = 1):
            lock_priority_code(self, uid=uid, order=1, total=1, max_threads=max_threads)

        def lock_priority_code(self, uid: Union[str, int], order: int = 1, total: int = None):
            lock_priority_code(self, uid=uid, order=order, total=total, max_threads=1)

        def unlock_code(self, uid: Union[str, int]):
            unlock_code(self, uid=uid)

        def __getstate__(self):
            state = dict(self.__dict__)
            state['private'] = p.getstate(self)
            return state

        def __setstate__(self, state):
            private = state.pop('private')
            p.setstate(self, private)
            self.__dict__ = state

        def __del__(self):
            p.delete(self)

    Monitor.__qualname__ = 'Monitor'

    return Monitor


StaticMonitor = Monitor()()
Monitor = Monitor()
