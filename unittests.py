#!/usr/bin/env python
# coding=utf-8

import unittest

def main():
    testmodules = [
        'sigilaalarmas.unittest.config',
        #'sigilaalarmas.unittest.test',
        ]

    suite = unittest.TestSuite()

    for t in testmodules:
        try:
            # If the module defines a suite() function, call it to get the suite.
            mod = __import__(t, globals(), locals(), ['suite'])
            suitefn = getattr(mod, 'suite')
            suite.addTest(suitefn())
        except (ImportError, AttributeError):
            # else, just load all the test cases from the module.
            suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()
