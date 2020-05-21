# /usr/bin/env python3
# encoding:utf-8


import concurrent
import time
from multiprocessing import Manager
from unittest import TestCase, main

from parallel_utils.process import Monitor, create_process

m = Monitor()
results = Manager().list()


class TestPriority(TestCase):

    @staticmethod
    def f1():
        m.lock_priority_code('test', 1, 3)
        time.sleep(3)
        results.append(1)
        m.unlock_code('test')

    @staticmethod
    def f2():
        m.lock_priority_code('test', 2)
        time.sleep(2)
        results.append(2)
        m.unlock_code('test')

    @staticmethod
    def f3():
        m.lock_priority_code('test', 3)
        results.append(3)
        m.unlock_code('test')

    def test_priority(self):
        processes = []
        t1 = time.time_ns()
        processes.append(create_process(self.f3))
        processes.append(create_process(self.f2))
        processes.append(create_process(self.f1))
        concurrent.futures.wait(processes)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 5)
        self.assertLessEqual(delta, 5.5)
        self.assertEqual((1, 2, 3), tuple(results))


if __name__ == '__main__':
    main()
