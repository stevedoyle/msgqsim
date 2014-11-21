#!/usr/local/bin/python

import argparse
import simpy
import logging
from collections import namedtuple

Msg = namedtuple('Msg', 'id, duration')

class Producer:
    def __init__(self, name, env, q, put_interval, msg_duration):
        self.name = name
        self.env = env
        self.q = q
        self.put_interval = put_interval
        self.msg_duration = msg_duration
        self.put_count = 0
        self.env.process(self.run())

    def run(self):
        while True:
            msg = Msg(self.next_message_id(), self.msg_duration)
            time_before_put = self.env.now
            yield self.q.put(msg)
            self.put_count += 1
            logging.debug("%s put %s at %d" % (self.name, msg, self.env.now))

            time_to_next_put = self.put_interval - (self.env.now - time_before_put)
            if time_to_next_put < 0: 
                continue
            
            yield self.env.timeout(self.put_interval)

    def next_message_id(self):
        return "%s_%s" % (self.name, self.put_count)
    
    def print_stats(self):
        print('%s put %d messages' % (self.name, self.put_count))

class Consumer:
    def __init__(self, name, env, q):
        self.name = name
        self.env = env
        self.q = q
        self.get_count = 0
        env.process(self.run())

    def run(self):
        while True:
            msg = yield self.q.get()
            self.get_count += 1
            logging.debug("%s got %s at %d" % (self.name, msg, self.env.now))
            yield self.env.timeout(msg.duration)

    def print_stats(self):
        print('%s got %d messages' % (self.name, self.get_count))

def generate_consumers(env, q, count):
    return [Consumer("C%d" % i, env, q) for i in range(0,count)]

def generate_producers(env, q, profiles):
    return [Producer("P%d" % i, env, q, p[0], p[1]) for i,p in enumerate(profiles)]

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
    consumers = generate_consumers(env, msgq, num_consumers)
    producers = generate_producers(env, msgq, [(20,4), (20,8), (20,2), (20,6)])

    env.run(until=1000)

    for p in producers:
        p.print_stats()

    for c in consumers:
        c.print_stats()

if __name__ == '__main__':
    main()