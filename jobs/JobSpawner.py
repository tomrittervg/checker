#!/usr/bin/env python

class JobSpawner:
    """OVERRIDE ME
       Returns an array (or using 'yield') of Job objects to run"""
    def get_sub_jobs(self, config):
        pass
