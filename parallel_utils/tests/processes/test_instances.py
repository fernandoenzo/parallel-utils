# /usr/bin/env python3
# encoding:utf-8


import concurrent
import time
from unittest import TestCase, main

from parallel_utils.process import Monitor, create_process

m1 = Monitor()
m2 = Monitor()


class TestInstances(TestCase):

    @staticmethod
    def m1_one_second_three_processes():
        m1.lock_code(uid='test1', max_threads=3)
        time.sleep(1)
        m1.unlock_code(uid='test1')

    @staticmethod
    def m2_three_seconds_three_processes():
        m2.lock_code(uid='test1', max_threads=1)
        time.sleep(1)
        m2.unlock_code(uid='test1')

    def test_m1_one_second_three_processes(self):
        processes = []
        t1 = time.time_ns()
        for _ in range(3):
            processes.append(create_process(self.m1_one_second_three_processes))
        concurrent.futures.wait(processes)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 1)
        self.assertLessEqual(delta, 1.5)

    def test_m2_three_seconds_three_processes(self):
        processes = []
        t1 = time.time_ns()
        for _ in range(3):
            processes.append(create_process(self.m2_three_seconds_three_processes))
        concurrent.futures.wait(processes)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 3)


if __name__ == '__main__':
    main()
