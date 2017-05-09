#!/usr/bin/env python
# coding=utf-8

""" Ejecuta una pasada completa de actualización de base de datos """

from eventmanager import EventManager

def main():
    """ Main function """
    manager = EventManager()

    manager.execute_all()


if __name__ == '__main__':
    main()
