#!/usr/bin/env python

import time
import logging

class StatusTracker:
    emailNotificationsAreWorking = False
    lastRunJob = 0
    def __init__(self, config):
        self.emailNotificationsAreWorking = False
        self.lastRunJob = 0
        self.config = config
        
    def isAllGood(self):
        return self.emailNotificationsAreWorking and \
            time.time() - self.lastRunJob < 120

    def markJobRan(self):
        self.lastRunJob = time.time()

    def markEmailStatus(self, working):
        self.emailNotificationsAreWorking = working