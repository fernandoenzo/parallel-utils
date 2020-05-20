# /usr/bin/env python3
# encoding:utf-8


import concurrent
import time
from unittest import TestCase, main

from parallel_utils.process import synchronized, create_process


class TestSynchronized(TestCase):

    @staticmethod
    @synchronized(3)
    def one_second_three_processes():
        time.sleep(1)

    @staticmethod
    @synchronized(1)
    def three_seconds_three_processes():
        time.sleep(1)

    def test_one_second_three_processes(self):
        processes = []
        t1 = time.time_ns()
        for _ in range(3):
            processes.append(create_process(self.one_second_three_processes))
        concurrent.futures.wait(processes)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 1)
        self.assertLessEqual(delta, 1.5)

    def test_three_seconds_three_processes(self):
        processes = []
        t1 = time.time_ns()
        for _ in range(3):
            processes.append(create_process(self.three_seconds_three_processes))
        concurrent.futures.wait(processes)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 3)


if __name__ == '__main__':
    main()
