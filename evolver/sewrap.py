#!/usr/bin/env python

# TODO: tab completion

import sys, os, fcntl, time, readline
from subprocess import *

HIST_FILE = os.path.join(os.getenv("HOME"), ".sewrap.hist")
# Right now, unlimited.  Set with readline.set_history_length( <lines> )

p = Popen('evolver ' + ' '.join(sys.argv[1:]), shell=True, 
            stdin=PIPE, stdout=PIPE, close_fds=True)
p.stdin.flush()
fcntl.fcntl(p.stdout, fcntl.F_SETFL, os.O_NONBLOCK)
try:
    readline.read_history_file(HIST_FILE)
except IOError:
    pass

while 1:
    try:
        try:
            line = p.stdout.read()
        except IOError:
            time.sleep(0.1)
        else:
            if line == '':
    #            print "EOF"
                break
            lines = line.split('\n')
            if len(lines) > 1:
                sys.stdout.write('\n'.join(lines[:-1]) + '\n')
                line = lines[-1]
            if line:
                try:
                    linein = raw_input(line)
                except EOFError:
                    sys.stdout.write('\n')
                    break # p.stdin.close() should send EOF
                p.stdin.write(linein + '\n')
                p.stdin.flush()
    except KeyboardInterrupt:
        # Note that ^C also goes through to child automagically.  But in case
        # evolver is really stuck, we'll give an option to force a quit
        response = ''
        while response not in ('y', 'n', 'q'):
            response = raw_input(' detected.  Do you wish to exit? (y/n): ')[0]
        if response in ('y', 'q'):
            break

p.stdout.close()
p.stdin.close()
try:
    readline.write_history_file(HIST_FILE)
except IOError:
    print "Warning: Could not save history file to", HIST_FILE
#sys.stdout.write('\n')
sys.exit(0)
