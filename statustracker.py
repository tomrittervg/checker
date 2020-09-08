#!/usr/bin/env python3

from builtins import object
import time
import logging

class StatusTracker(object):
    emailNotificationsAreWorking = False
    lastRunJob = 0
    def __init__(self, config):
        self.emailNotificationsAreWorking = False
        self.lastRunJob = 0
        self.config = config
        
    def isMailGood(self):
        return self.emailNotificationsAreWorking

    def isJobsGood(self):
        return time.time() - self.lastRunJob < 120

    def markJobRan(self):
        self.lastRunJob = time.time()

    def markEmailStatus(self, working):
        self.emailNotificationsAreWorking = working
