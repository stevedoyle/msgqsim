#!/usr/bin/env python

import simpy
import logging

def producer(env):
    duration = 2
    while True:
        # Put a message onto a message q
        logging.info('Producer: Sumbitting a job')
        yield env.timeout(duration)

def consumer(env):
    duration = 3
    while True:
        # Get a message from a message q
        # Process the message
        yield env.timeout(duration)


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
env = simpy.Environment()
env.process(producer(env))
env.process(consumer(env))
env.run(until=15)
