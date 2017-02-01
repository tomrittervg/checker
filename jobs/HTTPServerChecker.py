#!/usr/bin/env python

import logging
import requests

import JobBase
import JobSpawner

class HTTPServerChecker(JobSpawner.JobSpawner):
    servers = [ 
                #("http://example.com", JobBase.JobFrequency.MINUTE, JobBase.JobFailureNotificationFrequency.EVERYTIME, JobBase.JobFailureCountMinimumBeforeNotification.ONE),
                #("https://exampletwo.com", JobBase.JobFrequency.MINUTE, JobBase.JobFailureNotificationFrequency.EVERYTIME, JobBase.JobFailureCountMinimumBeforeNotification.ONE)
              ]

    class ServerChecker(JobBase.JobBase):
        def __init__(self, config, url, frequency, failureNotificationFrequency, failuresBeforeNotification):
            self.config = config
            self.url = url
            self.frequency = frequency
            self.failureNotificationFrequency = failureNotificationFrequency
            self.failuresBeforeNotification = failuresBeforeNotification
            super(HTTPServerChecker.ServerChecker, self).__init__(config, url)

        def getName(self):
            return str(self.__class__) + " for " + self.url
        def executeEvery(self):
            return self.frequency
        def notifyOnFailureEvery(self):
            return self.failureNotificationFrequency
        def numberFailuresBeforeNotification(self):
            return self.failuresBeforeNotification
        def execute(self):
            try:
                i = requests.get(self.url)
                if i.status_code != 200:
                    self.failuremsg = "Error hitting server " + self.url + " (Code: " + str(i.status_code) + ")"
                else:
                    return True
            except:
                self.failuremsg = "Could not hit server " + self.url
            logging.warn(self.failuremsg)
            return False
        def onFailure(self):
            return self.sendEmail(self.failuremsg, "")
        def onStateChangeSuccess(self):
            return self.sendEmail("Successfully hit " + self.url, "")

    def get_sub_jobs(self, config):
        for s in self.servers:
            yield self.ServerChecker(config, s[0], s[1], s[2], s[3])

