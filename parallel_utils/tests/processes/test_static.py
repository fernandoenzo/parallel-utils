# /usr/bin/env python3
# encoding:utf-8


import concurrent.futures
import time
from multiprocessing import Manager
from unittest import TestCase, main

from parallel_utils.process import StaticMonitor, create_process

results = Manager().list()


class TestStatic(TestCase):

    @staticmethod
    def m1_one_second_three_processes():
        StaticMonitor.lock_code(uid='test1', max_threads=3)
        time.sleep(1)
        StaticMonitor.unlock_code(uid='test1')

    @staticmethod
    def m2_three_seconds_three_processes():
        StaticMonitor.lock_code(uid='test2', max_threads=1)
        time.sleep(1)
        StaticMonitor.unlock_code(uid='test2')

    @staticmethod
    def f1():
        StaticMonitor.lock_priority_code('test3', 1, 3)
        time.sleep(3)
        results.append(1)
        StaticMonitor.unlock_code('test3')

    @staticmethod
    def f2():
        StaticMonitor.lock_priority_code('test3', 2)
        time.sleep(2)
        results.append(2)
        StaticMonitor.unlock_code('test3')

    @staticmethod
    def f3():
        StaticMonitor.lock_priority_code('test3', 3)
        results.append(3)
        StaticMonitor.unlock_code('test3')

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
        self.assertLessEqual(delta, 3.5)

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
