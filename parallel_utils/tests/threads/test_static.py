# /usr/bin/env python3
# encoding:utf-8


import concurrent.futures
import time
from unittest import TestCase, main

from parallel_utils.thread import StaticMonitor, create_thread

results = []


class TestStatic(TestCase):

    @staticmethod
    def m1_one_second_three_threads():
        StaticMonitor.lock_code(uid='test1', max_threads=3)
        time.sleep(1)
        StaticMonitor.unlock_code(uid='test1')

    @staticmethod
    def m2_three_seconds_three_threads():
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
        threads = []
        t1 = time.time_ns()
        for _ in range(3):
            threads.append(create_thread(self.m1_one_second_three_threads))
        concurrent.futures.wait(threads)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 1)
        self.assertLessEqual(delta, 1.5)

    def test_m2_three_seconds_three_processes(self):
        threads = []
        t1 = time.time_ns()
        for _ in range(3):
            threads.append(create_thread(self.m2_three_seconds_three_threads))
        concurrent.futures.wait(threads)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 3)
        self.assertLessEqual(delta, 3.5)

    def test_priority(self):
        threads = []
        t1 = time.time_ns()
        threads.append(create_thread(self.f3))
        threads.append(create_thread(self.f2))
        threads.append(create_thread(self.f1))
        concurrent.futures.wait(threads)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 5)
        self.assertLessEqual(delta, 5.5)
        self.assertEqual((1, 2, 3), tuple(results))


if __name__ == '__main__':
    main()
