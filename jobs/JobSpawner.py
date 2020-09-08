#!/usr/bin/env python

from builtins import object
class JobSpawner(object):
    """OVERRIDE ME
       Returns an array (or using 'yield') of Job objects to run"""
    def get_sub_jobs(self, config):
        pass
