# parallel-utils

[![PyPI](https://img.shields.io/pypi/v/parallel-utils?label=latest)](https://pypi.org/project/parallel-utils/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/parallel-utils)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/parallel-utils)
![PyPI - Status](https://img.shields.io/pypi/status/parallel-utils)

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/fernandoenzo/parallel-utils)
[![GitHub last commit](https://img.shields.io/github/last-commit/fernandoenzo/parallel-utils)](https://github.com/fernandoenzo/parallel-utils)
[![Build Status](https://img.shields.io/travis/com/fernandoenzo/parallel-utils?label=tests)](https://travis-ci.com/fernandoenzo/parallel-utils)
![Maintenance](https://img.shields.io/maintenance/yes/2020)

This library implements a class [**Monitor**](https://en.wikipedia.org/wiki/Monitor_(synchronization)), as defined by [**Per
 Brinch Hansen**](https://en.wikipedia.org/wiki/Per_Brinch_Hansen) and [**C.A.R. Hoare**](https://en.wikipedia.org/wiki/Tony_Hoare),
 for **synchronization and concurrent management of threads and processes in Python**. It also provides **other
  functions to ease the creation and collection of results for both threads and processes**. 

## Table of contents

<!--ts-->
  * [Installation](#installation)
  * [Usage](#usage)
     * [Monitor class](#monitor-class)
        * [First example](#first-example)
           * [@synchronized](#synchronized)
        * [Second example](#second-example)
           * [@synchronized_priority](#synchronized_priority)
     * [StaticMonitor class](#staticmonitor-class)
     * [Launching threads and processes](#launching-threads-and-processes)
  * [Contributing](#contributing)
  * [License](#license)
<!--te-->

## Installation

Use the package manager [**pip**](https://pip.pypa.io/en/stable/) to install **parallel-utils**.

```bash
pip3 install parallel-utils
```
## Usage

### Monitor class

There are two implementations of the `Monitor` class: one is located in the `thread` module and the other in the 
`process` module of `parallel-utils`.

Although it's safe to always use the `Monitor` class located in the `process` module, even if you're working only with
 threads, you will get slightly better performance when using the one located in the `thread` module. Therefore, it is
  recommended to use each one for what it is intended for.

From now on, for ease of reading, every time we say _thread_ we will also be including _process_ unless stated otherwise.

Also, from now until the end of this section, when we say _function_, we will not only refer to "whole" functions but we
 will also include pieces of code contained within a function.

A monitor essentially does two things:
1. It controls the maximum number of threads that can simultaneously access a function.

2. It organizes a set of functions so that they follow a strict order in their execution, regardless of the thread
 from which they are called.


#### First example
> 1. It allows controlling the maximum number of threads that can simultaneously access a function.

To achieve this first goal, the Monitor class includes the following couple of functions:

```python
def lock_code(self, uid: Union[str, int], max_threads: int = 1)

def unlock_code(self, uid: Union[str, int])
```

The first one, `lock_code`, must be called at the beginning of the piece of code for which we want to control the maximum
 number of threads that can access it simultaneously.

The `unlock_code` function sets the limit of the scope of the `lock_code` function.

To do this, both functions must share a same unique identifier (`uid`), that can be either a string or
 an integer number. Let's see an example:

```python
import concurrent.futures
from time import sleep
from parallel_utils.thread import Monitor, create_thread

m = Monitor()

def print_and_sleep():
    print('Hello')
    m.lock_code('example', max_threads=1)
    sleep(2)
    m.unlock_code('example')
    print('Goodbye')

th1 = create_thread(print_and_sleep)
th2 = create_thread(print_and_sleep)
th3 = create_thread(print_and_sleep)

concurrent.futures.wait([th1, th2, th3])
```

The example shown above takes 6 seconds to finalize its execution, since we have a `lock_code` that only allows one thread
 each time to execute the `sleep` function, and we are launching three threads.

If we set the `lock_code` to allow up to three threads at the same time, then the code only needs 2 seconds to finalize
 its execution, since all the three threads can make the `sleep` blocking call at the same time.

We'll se more about the `create_thread` and `create_process` functions later.

The last line, [`concurrent.futures.wait`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.wait)
 is a blocking call that waits until all the three threads finish running.

#### @synchronized

In the previous example, we just were protecting the piece of code wrapping the `sleep` call. But, what if we want to wrap
 the entire function?
 
Of course we could call `lock_code` on the first line, and `unlock_code` on the last one, and that would work
 just fine. Like this:
 
 ```python
def print_and_sleep():
    m.lock_code('example', 1)
    print('Hello')
    sleep(2)
    print('Goodbye')
    m.unlock_code('example')
```  

But, to simplify life for the programmer and for improving readability, there's some syntactic sugar we could use. And this is
 where the `@synchronized` decorator comes in and turns the above code into this:

```python
from parallel_utils.thread import synchronized

@synchronized
def print_and_sleep():
    print('Hello')
    sleep(2)
    print('Goodbye')
```

Let's see the decorator prototype:

```python
@synchronized(max_threads: int = 1)
```

As you can see, the `@synchronized` decorator doesn't need an identifier, and by default only allows one thread to access the
 function at the same time. However, we can override that default behavior with the optional `max_threads` argument.

If we want, for example, to allow up to two threads to enter the function at the same time, we only need to write:

```python
@synchronized(2)
def print_and_sleep():
    print('Hello')
    sleep(2)
    print('Goodbye')
```

Note that **this decorator has its own namespace for uids**, which is completely independent of the namespace of the
 `lock_code` and `unlock_code` functions.

#### Second example

> &nbsp;2. It allows organizing a set of functions so that they follow a strict order in their execution, regardless of the
 thread from which they are called.

To achieve this first goal, the Monitor class includes the following couple of functions:

```python
def lock_priority_code(uid: Union[str, int], order: int = 1, total: int = 1)

def unlock_code(uid: Union[str, int], order: int)
```

Yes, the `unlock_code` function is the same as before. And these two functions work quite similarly to the previous example, 
 wrapping the code snippet that we want to control and sharing the same `uid` between them.

The main difference is that, in this case, we have to specify the `order` in which the code snippet will run and the `total`
 number of functions to sync with the supplied `uid`.
 
Let's see an example:

```python
from time import sleep
from parallel_utils.process import Monitor, create_process

m = Monitor()

def say_hello(name):
    print('Entering hello')
    m.lock_priority_code('id1', order=1, total=2)
    print(f'Hello {name}!')
    m.unlock_code('id1')

def say_goodbye(name):
    print('Entering goodbye')
    m.lock_priority_code('id1', order=2)
    print(f'Goodbye {name}!')
    m.unlock_code('id1')

create_process(say_goodbye, 'Peter')
sleep(3)
create_process(say_hello, 'Peter')
```

this example will always print:

```
Entering goodbye
. . . (3 secs after)
Entering hello
Hello Peter!
Goodbye Peter!
```

even if you start the `say_goodbye` function long before the `say_hello` function. This is because the snippet in `say_goobye` has
 not the first turn, but the second, so it will make a blocking call and wait until `say_hello` calls `unlock_code`.

The `total` argument must be supplied **at least once** in any of the calls to `lock_priority_code`.

With these two functions, you can sort the execution of as many code snippets as you need.

Note that `lock_code` and `lock_priority_code` share the same namespace for uids. 

#### @synchronized_priority

Just like before, there is a decorator that we can use to wrap a complete function and set its relative order of execution
 with respect to others.

This is its prototype:

```python
@synchronized_priority(uid: Union[str, int], order: int = 1, total: int = None)
```
 
With it, the last example would look like this:

```python
from parallel_utils.process import create_process, synchronized_priority

@synchronized_priority('id1', order=1)
def say_hello(name):
    print('Entering hello')
    print(f'Hello {name}!')

@synchronized_priority('id1', order=2, total=2)
def say_goodbye(name):
    print('Entering goodbye')
    print(f'Goodbye {name}!')

create_process(say_goodbye, 'Peter')
sleep(3)
create_process(say_hello, 'Peter')
```

Note that this time we've provided the `total` argument in the second call instead of the first one. Never mind. You
 could even supply it in both.

The above example will always print:

```
. . . (sleeps 3 secs)
Entering hello
Hello Peter!
Entering goodbye
Goodbye Peter!
```

Note that **this decorator has its own namespace for uids**, which is completely independent of the namespace of the
 `lock_priority_code` and `unlock_code` functions.

### StaticMonitor class

The `StaticMonitor` class has exactly the same methods as the `Monitor` class. And it also has two implementations: one can
 be imported from `parallel_utils.process` and the other can be imported from `parallel_utils.thread`.

This class saves you the need to instantiate a `Monitor`, store it in a variable, and then use it. Instead of that, you can
 just call its methods like this:

```python
from parallel_utils.process import StaticMonitor

def say_hello(name):
    print('Entering hello')
    StaticMonitor.lock_priority_code('id1', order=1, total=2)
    print(f'Hello {name}!')
    StaticMonitor.unlock_code('id1')
```

Note that this class, since it is static, has a unique namespace for uids that is shared among all calls to its methods. 

### Launching threads and processes

This library includes two very useful functions to quickly start processes and threads, and retrieve their results, which we
 have already seen in our examples:

```python
def create_thread(func: Callable, *args: Any, **kwargs: Any) -> Future

def create_process(func: Callable, *args: Any, **kwargs: Any) -> Future
``` 

Like the rest of classes and objects in this library, they are located in `parallel_utils.thread` and
 `parallel_utils.process` respectively.

Their first argument is a Callable that, in turn, is called with `*args` and `**kwargs`.
 
They both return a [`Future`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Future)
 object, which encapsulates the asynchronous execution of a callable.

Although the [`Future`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Future) class has
 several interesting methods that you should read in the official documentation, by far the most interesting one is probably
  **the `result()` method, which makes a blocking call until the thread finishes and returns**.

Another interesting feature of these two methods is that **you don't need to worry about zombie processes anymore** due to a
 forgotten `join()` call, since all this logic is handled automatically. Just focus on making calls and retrieving results.

In this example, we compute two factorials, each one in a different process, to bypass the Python GIL and have real
 parallelism, and then we retrieve and print their results:

```python
from parallel_utils.process import create_process

def factorial(n):
    res = 1
    for i in range(1,n+1):
        res *= i
    return res

f1 = create_process(factorial, 5)
f2 = create_process(factorial, 7)

print(f1.result(), f2.result())
``` 

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

![PyPI - License](https://img.shields.io/pypi/l/private-attrs)

This library is licensed under the
 [GNU General Public License v3 or later (GPLv3+)](https://choosealicense.com/licenses/gpl-3.0/)