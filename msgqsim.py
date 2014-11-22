#!/usr/local/bin/python

import argparse
import simpy
import logging
from collections import namedtuple

import pdb

Msg = namedtuple('Msg', 'id, duration')

class Producer:
    def __init__(self, name, env, q, sync, rate, priority, msg_duration):
        self.name = name
        self.env = env
        self.q = q
        self.sync = sync
        self.rate = rate # in units per 100 ticks
        self.priority = priority
        self.msg_duration = msg_duration
        self.put_count = 0
        self.unit_count = 0
        self.tokens = self.rate
        self.last_put_time = 0
        self.next_token_refresh_time = self.env.now + 100
        self.env.process(self.run())

    def run(self):
        while True:
            logging.debug('%s - tokens:%d' % (self.name, self.tokens))
            msg = Msg(self.next_message_id(), self.msg_duration)
#            pdb.set_trace()
            if self.tokens < msg.duration:
#                yield self.env.timeout(msg.duration - self.tokens)
                yield self.env.timeout(self.next_token_refresh_time - self.env.now)
                self.tokens += self.rate
                self.next_token_refresh_time += 100
            
            self.tokens -= msg.duration
        
            with self.sync.request(priority=self.priority) as request:
                yield request
                yield self.q.put(msg)
                self.put_count += 1
                self.unit_count += msg.duration
                logging.debug("%s put %s at %d" % (self.name, msg, self.env.now))

#            self.tokens += (self.env.now - self.last_put_time) / 100 * self.rate
#            self.last_put_time = self.env.now

    def next_message_id(self):
        return "%s_%s" % (self.name, self.put_count)
    
    def print_stats(self):
        print('%s put %d messages, %d units' % (self.name, self.put_count, self.unit_count))

class Consumer:
    def __init__(self, name, env, q):
        self.name = name
        self.env = env
        self.q = q
        self.get_count = 0
        self.unit_count = 0
        env.process(self.run())

    def run(self):
        while True:
            msg = yield self.q.get()
            self.get_count += 1
            self.unit_count += msg.duration
            logging.debug("%s got %s at %d" % (self.name, msg, self.env.now))
            yield self.env.timeout(msg.duration)

    def print_stats(self):
        print('%s got %d messages, %d units' % (self.name, self.get_count, self.unit_count))

def generate_consumers(env, q, count):
    return [Consumer("C%d" % i, env, q) for i in range(0,count)]

def generate_producers(env, q, sync, profiles):
    return [Producer("P%d" % i, env, q, sync, p[0], p[1], p[2]) for i,p in enumerate(profiles)]

#############################
def main():
    parser = argparse.ArgumentParser(description="Message Scheduling Simulation")

    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-vv', '--very_verbose', action='store_true', 
        help='Very verbose output')
    parser.add_argument('-p', '--prods', nargs='?', default='2', type=int,
        help='Number of producers in the similation (default = 2)')
    parser.add_argument('-c', '--consumers', nargs='?', default='1', type=int,
        help='Number of parallel consumers in the simulation. (default = 1)')
    parser.add_argument('-d', '--duration', nargs='?', default='1000', type=int,
        help='Simulation duration (default = 1000)')
        
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    elif args.very_verbose:
        logging.basicConfig(level=logging.DEBUG)

    env = simpy.Environment()
    num_consumers = args.consumers
    msgq = simpy.Store(env, capacity=num_consumers)
    sync = simpy.PriorityResource(env, capacity=1)
    consumers = generate_consumers(env, msgq, num_consumers)
    producers = generate_producers(env, msgq, sync, [(28,1,4), (24,1,8), (20,1,2), (20,1,6)])

    env.run(until=1000)

    for p in producers:
        p.print_stats()

    for c in consumers:
        c.print_stats()

if __name__ == '__main__':
    main()