#!/usr/bin/env python

import os
import socket
import logging

import JobBase
import JobSpawner

class TCPServerChecker(JobSpawner.JobSpawner):
    servers = [ 
                #("example.com", 53, "example.com:tcpdns", JobBase.JobFrequency.MINUTE, JobBase.JobFailureNotificationFrequency.EVERYTIME, JobBase.JobFailureCountMinimumBeforeNotification.ONE)
              ]

    class ServerChecker(JobBase.JobBase):
        def __init__(self, config, ip, port, friendlyName, frequency, failureNotificationFrequency, failuresBeforeNotification):
            self.config = config
            self.ip = ip
            self.port = port
            self.friendlyName = friendlyName + "(" + self.ip + ":" + str(self.port) + ")"
            self.frequency = frequency
            self.failureNotificationFrequency = failureNotificationFrequency
            self.failuresBeforeNotification = failuresBeforeNotification
            super(TCPServerChecker.ServerChecker, self).__init__(config, ip, port, friendlyName, frequency, failureNotificationFrequency, failuresBeforeNotification)

        def getName(self):
            return str(self.__class__) + " for " + self.friendlyName
        def executeEvery(self):
            return self.frequency
        def notifyOnFailureEvery(self):
            return self.failureNotificationFrequency
        def numberFailuresBeforeNotification(self):
            return self.failuresBeforeNotification
        def execute(self):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((self.ip, self.port))
                s.close()
                return True
            except:
                self.failuremsg = "Could not hit server " + self.friendlyName
                logging.warn(self.failuremsg)
                return False
        def onFailure(self):
            return self.sendEmail(self.failuremsg, "")
        def onStateChangeSuccess(self):
            return self.sendEmail("Successfully hit " + self.friendlyName, "")

    def get_sub_jobs(self, config):
        for s in self.servers:
            yield self.ServerChecker(config, s[0], s[1], s[2], s[3], s[4], s[5])

            
