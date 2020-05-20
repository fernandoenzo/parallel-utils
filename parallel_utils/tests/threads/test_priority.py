# /usr/bin/env python3
# encoding:utf-8


import concurrent.futures
import time
from unittest import TestCase, main

from parallel_utils.thread import create_thread, Monitor

m = Monitor()


class TestPriority(TestCase):

    @staticmethod
    def f1():
        m.lock_priority_code('test', 1)
        time.sleep(3)
        print('I am the function number 1')
        m.unlock_code('test')

    @staticmethod
    def f2():
        m.lock_priority_code('test', 2)
        time.sleep(2)
        print('I am the function number 2')
        m.unlock_code('test')

    @staticmethod
    def f3():
        m.lock_priority_code('test', 3, 3)
        print('I am the function number 3')
        m.unlock_code('test')

    def test_priority(self):
        threads = []
        t1 = time.time_ns()
        threads.append(create_thread(self.f1))
        threads.append(create_thread(self.f2))
        threads.append(create_thread(self.f3))
        concurrent.futures.wait(threads)
        t2 = time.time_ns()
        delta = (t2 - t1) * (10 ** -9)
        self.assertGreaterEqual(delta, 5)


if __name__ == '__main__':
    main()
