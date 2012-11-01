#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from threading import Thread, Event

## \brief Auxiliary Class to execute functions periodically.
#
class RepeatTimer(Thread):
    
    ## Class constructor.
    #
    #  Executes the given function each interval time, a certain number of times (iterations).
    #
    # \param interval Interval, in seconds
    # \param function Function or callable object to execute
    # \param iterations Maximum number of iterations
    # \param args Function arguments
    # \param kwargs Arguments cictionary 
    def __init__(self, interval, function, iterations=0, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.iterations = iterations
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()
 
    ## Statrs thread
    #
    def run(self):
        count = 0
        while not self.finished.is_set() and (self.iterations <= 0 or count < self.iterations):
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
                count += 1

    ## Cancel execution
    #
    def cancel(self):
        self.finished.set()
