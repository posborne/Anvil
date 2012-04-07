# Copyright (c) 2012 Paul Osborne <osbpau@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import Queue
import datetime
import functools
import threading


def iso_8601_to_datetime(dt):
    return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")


class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


class ThreadPoolWorker(threading.Thread):
    """A very simmple threadpool worker (off a queue)"""

    def __init__(self, queue, timeout=0.1):
        threading.Thread.__init__(self)
        self.queue = queue
        self.timeout = timeout
        self.has_exit = False

    def stop(self):
        self.has_exit = True

    def run(self):
        while True:
            try:
                action, args, kwargs = self.queue.get(timeout=self.timeout)
            except Queue.Empty:
                if self.has_exit:
                    return  # only quit when no work to do
            else:
                action(*args, **kwargs)


class ThreadPool(object):
    """Dirt simple threadpool implementation"""

    def __init__(self, workers=50):
        self.workers = workers
        self._workers = []
        self._queue = Queue.Queue()

    def start(self):
        for _ in xrange(50):
            worker = ThreadPoolWorker(self._queue)
            self._workers.append(worker)
            worker.start()

    def queue_action(self, fn, *args, **kwargs):
        self._queue.put((fn, args, kwargs))

    def stop(self):
        for worker in self._workers:
            worker.stop()

    def join(self):
        for worker in self._workers:
            worker.join()


def parallel_execute(*executables, **kwargs):
    """Execute a set of functions in parallel (on a threadpool)"""
    workers = min(len(executables), kwargs.get('workers', 500))
    threadpool = ThreadPool(workers=workers)
    threadpool.start()
    for fn in executables:
        threadpool.queue_action(fn)
    threadpool.stop()
    threadpool.join()
