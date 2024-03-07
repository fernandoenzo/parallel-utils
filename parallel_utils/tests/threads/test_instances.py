# /usr/bin/env python3
# encoding:utf-8


import concurrent.futures
import time
from unittest import TestCase, main

from parallel_utils.thread import create_thread, Monitor


class TestInstances(TestCase):
    m1 = Monitor()
    m2 = Monitor()

    @classmethod
    def m1_two_seconds_three_threads(cls):
        cls.m1.lock_code(uid='test1', max_threads=2)
        time.sleep(1)
        cls.m1.unlock_code(uid='test1')

    @classmethod
    def m2_three_seconds_three_threads(cls):
        cls.m2.lock_code(uid='test1', max_threads=1)
        time.sleep(1)
        cls.m2.unlock_code(uid='test1')

    def test_m1_two_seconds_three_threads(self):
        threads = []
        t1 = time.time_ns()
        for _ in range(3):
            threads.append(create_thread(self.m1_two_seconds_three_threads))
        concurrent.futures.wait(threads)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 2)
        self.assertLessEqual(delta, 2.5)

    def test_m2_three_seconds_three_threads(self):
        threads = []
        t1 = time.time_ns()
        for _ in range(3):
            threads.append(create_thread(self.m2_three_seconds_three_threads))
        concurrent.futures.wait(threads)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 3)
        self.assertLessEqual(delta, 3.5)


if __name__ == '__main__':
    main()
