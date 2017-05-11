#!/usr/bin/env python
# coding=utf-8

import unittest
from ..sigilaalarmas import config


class TestConfig(unittest.TestCase):

    def __init__(self):
        pass

def main():
    unittest.main()

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    main()
