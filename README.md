# parallel-utils

[![PyPI](https://img.shields.io/pypi/v/parallel-utils?label=latest)](https://pypi.org/project/parallel-utils/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/parallel-utils)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/parallel-utils)
![PyPI - Status](https://img.shields.io/pypi/status/parallel-utils)

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/fernandoenzo/parallel-utils)
[![GitHub last commit](https://img.shields.io/github/last-commit/fernandoenzo/parallel-utils)](https://github.com/fernandoenzo/parallel-utils)
[![Build Status](https://img.shields.io/travis/com/fernandoenzo/parallel-utils?label=tests)](https://travis-ci.com/fernandoenzo/parallel-utils)

This library implements a [**Monitor**](https://en.wikipedia.org/wiki/Monitor_(synchronization)) class, as defined by [**Per
 Brinch Hansen**](https://en.wikipedia.org/wiki/Per_Brinch_Hansen) and [**C.A.R. Hoare**](https://en.wikipedia.org/wiki/Tony_Hoare),
 for **synchronization and concurrent management of threads and processes in Python**. It also provides **additional
  functions to facilitate the creation and collection of results for both threads and processes**. 

## Table of contents

<!--ts-->
  * [Installation](#installation)
  * [Usage](#usage)
     * [Monitor class](#monitor-class)
        * [First example](#first-example)
           * [@synchronized](#synchronized)
        * [Second example](#second-example)
           * [@synchronized_priority](#synchronized_priority)
     * [StaticMonitor](#staticmonitor)
     * [Launching threads and processes](#launching-threads-and-processes)
  * [Contributing](#contributing)
  * [License](#license)
<!--te-->

## Installation

Use the package manager [**pip**](https://pip.pypa.io/en/stable/) to install **parallel-utils**.

```bash
pip install parallel-utils
```
## Usage

### Monitor class

There are two implementations of the `Monitor` class: one is located in the `thread` module and the other in the 
`process` module of `parallel-utils`.

Although it's safe to always use the `Monitor` class located in the `process` module, even if you're only working with
 threads, you will achieve slightly better performance when using the one located in the `thread` module. Therefore, it is 
 recommended to use each one for its intended purpose.

For ease of reading, every time we mention a _thread_, we will also be including a _process_ unless stated otherwise..

Also, from now until the end of this section, when we mention a _function_, we will be referring not only to “whole” 
 functions but also to pieces of code contained within a function.

A monitor essentially does two things:
1. It controls the maximum number of threads that can simultaneously access a function.

2. It organizes a set of functions so that they follow a strict order in their execution, regardless of the thread
 from which they are called.


#### First example
> 1. It allows controlling the maximum number of threads that can simultaneously access a function.

To achieve this first goal, the `Monitor` class includes the following pair of functions:

```python
def lock_code(self, uid: str | int, max_threads: int = 1)

def unlock_code(self, uid: str | int)
```

The first one, `lock_code`, must be called at the beginning of the piece of code for which we want to control the maximum 
 number of threads that can access it simultaneously.

The `unlock_code` function sets the limit of the scope of the `lock_code` function.

To do this, both functions must share the same unique identifier (`uid`), which can be either a string or an integer number. 
Let’s see an example:

```python
import concurrent.futures
from time import sleep
from parallel_utils.thread import Monitor, create_thread

m = Monitor()

def print_and_sleep():
    print('Hello')
    m.lock_code(uid='example', max_threads=1)
    sleep(2)
    m.unlock_code('example')
    print('Goodbye')

th1 = create_thread(print_and_sleep)
th2 = create_thread(print_and_sleep)
th3 = create_thread(print_and_sleep)

concurrent.futures.wait([th1, th2, th3])
```

The example shown above takes 6 seconds to complete its execution, since we have a `lock_code` that only allows one thread 
 at a time to execute the `sleep` function, and we are launching three threads.

If we set the `lock_code` to allow up to three threads at the same time, then the code only needs 2 seconds to complete
 its execution, since all three threads can make the `sleep` blocking call at the same time.

We'll se more about the `create_thread` and `create_process` functions later.

The last line, [`concurrent.futures.wait`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.wait), 
 is a blocking call that waits until all three threads finish running.

For security and convenience, a context manager, `synchronized`, has been implemented that eliminates the need to explicitly 
use `lock_code` and `unlock_code`. This context manager automatically handles the locking and unlocking of code sections, 
simplifying the writing of code and improving readability.

In that case, the function above could be rewritten like this:

```python
m = Monitor()

def print_and_sleep():
    print('Hello')
    with m.synchronized(uid='example', max_threads=1):
        sleep(2)
    print('Goodbye')
```
##
#### @synchronized

In the previous example, we were only protecting the piece of code wrapping the `sleep` call. But, what if we want to wrap
 the entire function?
 
Of course, we could use the context manager to wrap the whole code and that would work just fine. Like this:

 ```python
m = Monitor()

def print_and_sleep():
    with m.synchronized(uid='example', max_threads=1):
        print('Hello')
        sleep(2)
        print('Goodbye')
```  

But to simplify life for the programmer and improve readability, there’s some syntactic sugar we could use. And this is 
where the `@synchronized` decorator comes in and turns the above code into this:

```python
from parallel_utils.thread import synchronized

@synchronized()
def print_and_sleep():
    print('Hello')
    sleep(2)
    print('Goodbye')
```

Let's see the decorator prototype:

```python
@synchronized(max_threads: int = 1)
```

As you can see, the `@synchronized` decorator doesn’t need an identifier, and by default only allows one thread to enter 
 the function at the same time. However, we can override that default behavior with the optional `max_threads` argument.

If we want, for example, to allow up to two threads to enter the function at the same time, we only need to write:

```python
@synchronized(2)
def print_and_sleep():
    print('Hello')
    sleep(2)
    print('Goodbye')
```

Note that **this decorator has its own namespace for uids**, which is completely independent of the namespace of any 
`Monitor` class you instantiate.

#### Second example

> 2. It organizes a set of functions so that they follow a strict order in their execution, regardless of the thread
 from which they are called.

To achieve the second goal, the `Monitor` class includes the following couple of functions:

```python
def lock_priority_code(uid: str | int, order: int = 1, total: int = 1)

def unlock_code(uid: str | int, order: int)
```

Yes, the `unlock_code` function is the same as before. And these two functions work quite similarly to the previous 
example, wrapping the code snippet that we want to control and sharing the same `uid` between them.

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

This example will always print:

```
Entering goodbye
. . . (3 secs after)
Entering hello
Hello Peter!
Goodbye Peter!
```

even if you start the `say_goodbye` function long before the `say_hello` function. This is because the snippet in 
 `say_goobye` does not have the first turn, but the second, so it will make a blocking call and wait until `say_hello` 
 calls `unlock_code`.

The `total` argument must be supplied **at least once** in any of the calls to `lock_priority_code`.

With these two functions, you can sort the execution of as many code snippets as you need.

Note that `lock_code` and `lock_priority_code` share the same namespace for uids, as they are methods of the same 
instantiated Monitor, `m`.

There is also a context manager implemented in this case, similar to before, called `synchronized_priority`, that can 
rewrite the above code to look like this:

```python
m = Monitor()

def say_hello(name):
    print('Entering hello')
    with m.synchronized_priority('id1', order=1, total=2):
        print(f'Hello {name}!')

def say_goodbye(name):
    print('Entering goodbye')
    with m.synchronized_priority('id1', order=2):
        print(f'Goodbye {name}!')
```

##
#### @synchronized_priority

Similar to before, there is a decorator that we can use to wrap an entire function and set its relative order of execution 
 with respect to others.

This is its prototype:

```python
@synchronized_priority(uid: str | int, order: int = 1, total: int = None)
```
 
With it, the previous example would look like this:

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

This time, we’ve provided the `total` argument in the second call instead of the first one. You could even supply it in both.

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

### StaticMonitor

For the convenience of programmers, a `Monitor` has already been instantiated and named `StaticMonitor`. Actually, there 
 are two of them, as usual: one can be imported from `parallel_utils.process` and the other can be imported from 
 `parallel_utils.thread`.

This object saves you the need to instantiate a `Monitor`, store it in a variable, and then use it. Instead, you can just 
 call its methods like this:

```python
from parallel_utils.process import StaticMonitor

def say_hello(name):
    print('Entering hello')
    StaticMonitor.lock_priority_code('id1', order=1, total=2)
    print(f'Hello {name}!')
    StaticMonitor.unlock_code('id1')
```

or better:

```python
from parallel_utils.process import StaticMonitor

def say_hello(name):
    print('Entering hello')
    with StaticMonitor.synchronized_priority('id1', order=1, total=2):
        print(f'Hello {name}!')
```

Note that this object has a unique namespace for uids that is shared among all calls to its methods. 

### Launching threads and processes

This library includes two very useful functions to quickly start processes and threads, and retrieve their results, which 
 we have already seen in our examples:

```python
def create_thread(func: Callable, *args: Any, **kwargs: Any) -> Future

def create_process(func: Callable, *args: Any, **kwargs: Any) -> Future
``` 

Like the rest of the classes and objects in this library, they are located in `parallel_utils.thread` and
 `parallel_utils.process` respectively.

Their first argument is a `Callable` that, in turn, is called with `*args` and `**kwargs`.
 
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