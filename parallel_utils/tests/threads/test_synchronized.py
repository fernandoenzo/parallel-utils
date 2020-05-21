# /usr/bin/env python3
# encoding:utf-8


import concurrent.futures
import time
from unittest import TestCase, main

from parallel_utils.thread import create_thread, synchronized


class TestSynchronized(TestCase):

    @staticmethod
    @synchronized(3)
    def one_second_three_threads():
        time.sleep(1)

    @staticmethod
    @synchronized(1)
    def three_seconds_three_threads():
        time.sleep(1)

    def test_one_second_three_threads(self):
        threads = []
        t1 = time.time_ns()
        for _ in range(3):
            threads.append(create_thread(self.one_second_three_threads))
        concurrent.futures.wait(threads)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 1)
        self.assertLessEqual(delta, 1.5)

    def test_three_seconds_three_threads(self):
        threads = []
        t1 = time.time_ns()
        for _ in range(3):
            threads.append(create_thread(self.three_seconds_three_threads))
        concurrent.futures.wait(threads)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 3)
        self.assertLessEqual(delta, 3.5)


if __name__ == '__main__':
    main()
