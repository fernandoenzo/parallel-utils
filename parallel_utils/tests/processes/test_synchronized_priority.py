# /usr/bin/env python3
# encoding:utf-8


import concurrent
import time
from multiprocessing import Manager
from unittest import TestCase, main

from parallel_utils.process import synchronized_priority, create_process

results = Manager().list()


class TestPriority(TestCase):

    @staticmethod
    @synchronized_priority('test1', 1)
    def f1():
        time.sleep(3)
        results.append(1)

    @staticmethod
    @synchronized_priority('test1', 2)
    def f2():
        time.sleep(2)
        results.append(2)

    @staticmethod
    @synchronized_priority('test1', 3, 3)
    def f3():
        results.append(3)

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
