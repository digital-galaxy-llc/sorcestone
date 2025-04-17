#    Author: Alex Savatieiev (a.savex@gmail.com)
#    April-May 2023
import unittest

from unittest import TextTestResult, TextTestRunner
from tests.test_base import tests_dir


class MyTestResult(TextTestResult):
    # overide test name in output
    def getDescription(self, test):
        if self.descriptions and test.shortDescription():
            return '\n'.join((str(test), test.shortDescription()))
        else:
            return f"{test.__class__.__module__}." \
                    "{test.__class__.__name__}.{test._testMethodName}"


class MyTestRunner(TextTestRunner):
    resultclass = MyTestResult


def _cleanup():
    pass


if __name__ == '__main__':
    # remove old files if exists
    _cleanup()

    # start tests
    suite = unittest.TestLoader().discover(tests_dir, "test*", tests_dir)
    runner = MyTestRunner(verbosity=3)
    runner.run(suite)

    # cleanup after testrun
    _cleanup()
