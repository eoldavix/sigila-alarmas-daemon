#!/usr/bin/env python
# coding=utf-8


import unittest
from ..config.config import Config

class TestMyConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config()


    def test_true(self):
        self.assertTrue('Red de Alumnos' in self.config.events['network_alum']['string'], msg="Probando")


def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestMyConfig))
    return test_suite


if __name__ == '__main__':
    unittest.main()
