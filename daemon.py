#!/usr/bin/env python
# coding=utf-8

""" Ejecutable """

from __future__ import print_function
import sys
from sigilaalarmas.lib.daemon import EventManagerDaemon

def usagehelp():
    """ Help Function """
    print("usage: %s start|stop|restart" % sys.argv[0])
    sys.exit(2)

def main():
    """ Main Function """
    daemon = EventManagerDaemon("/var/run/pid")

    actions = {'start': daemon.start,
               'stop': daemon.stop,
               'restart': daemon.restart
              }

    if len(sys.argv) == 2:
        actions.get(sys.argv[1], usagehelp)()
    else:
        usagehelp()

    sys.exit(0)

if __name__ == "__main__":
    main()
