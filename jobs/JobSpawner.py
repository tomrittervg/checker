#!/usr/bin/env python3

from builtins import object


class JobSpawner(object):
    """OVERRIDE ME
    Returns an array (or using 'yield') of Job objects to run"""

    def get_sub_jobs(self, config):
        pass
