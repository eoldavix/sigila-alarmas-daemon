#!/usr/bin/env python
# coding=utf-8

""" Ejecuta una pasada completa de actualización de base de datos """

from sigilaalarmas.lib.eventmanager import EventManager
import sys

def main():
    """ Main function """
    manager = EventManager()

    if sys.argv[1] == "foreground":
        print "Ejecución en foreground..."
        manager.events_scheduling()
    else:
        manager.execute_all()


if __name__ == '__main__':
    main()
