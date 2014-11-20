msgqsim
=======

Simulation of a message queue processing environemnt using simpy.

This is intended as a sandpit area for experimentation.

Of initial interest is multiple producer processes submitting jobs into 
message queues which are then consumed by a single consumer process. The 
simulator allows experimentation with various queue selection algorithms
within the consumer process. For example, what is the best algorithm to
use if (a) all the jobs take the same amount of time to process in the 
consumer or (b) different jobs require different processing times within
the consumer?

