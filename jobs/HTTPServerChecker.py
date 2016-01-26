#!/usr/bin/env python

import logging
import requests

import JobBase
import JobSpawner

class HTTPServerChecker(JobSpawner.JobSpawner):
    servers = [ 
                #("http://example.com", JobBase.JobFrequency.MINUTE),
                #("https://exampletwo.com", JobBase.JobFrequency.MINUTE)
              ]

    class ServerChecker(JobBase.JobBase):
        def __init__(self, url, frequency):
            self.url = url
            self.frequency = frequency

        def getName(self):
            return str(self.__class__) + " for " + self.url
        def executeEvery(self):
            return self.frequency
        def execute(self):
            try:
                requests.get(self.url)
                return True
            except:
                msg = "Could not hit server " + self.url
                logging.warn(msg)
                return self.sendEmail(msg, "")

    def get_sub_jobs(self):
        for s in self.servers:
            yield self.ServerChecker(s[0], s[1])

