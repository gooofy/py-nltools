#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2017 Guenter Bartsch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# A simple thread pool implementation
#
from __future__ import print_function

import traceback
import logging

from Queue import Queue, Empty
from threading import Thread, Lock

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks, idx):
        Thread.__init__(self)
        self.tasks  = tasks
        self.idx    = idx
        #self.daemon = True
        self.finish = False
        self.start()

    def run(self):
        while not self.finish:

            # print "worker #%2d" % self.idx

            try:
                func, args, kargs = self.tasks.get(True, 0.1)
                try:
                    func(*args, **kargs)
                except:
                    logging.error('ThreadPool Worker caught exception: %s' % traceback.format_exc())
                    traceback.print_exc()
                finally:
                    self.tasks.task_done()

            except Empty:
                # print "worker #%2d empty" % self.idx
                pass


class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue()
        self.terminal_lock = Lock()
        self.workers = []
        for idx in range(num_threads): 
            self.workers.append(Worker(self.tasks, idx))

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def print_synced(self, s):
        self.terminal_lock.acquire()
        print(s)
        self.terminal_lock.release()

    def shutdown(self):
        print("shutdown: tasks.join...")
        self.tasks.join()
        print("shutdown: tasks.join...done. finishing workers...")
        # for worker in self.workers:
        #     worker.finish = True
        #     worker.join()

        print("shutdown complete.")


