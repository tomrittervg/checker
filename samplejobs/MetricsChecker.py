#!/usr/bin/env python3

from builtins import str
import logging
import datetime 

import requests

import JobBase

class MetricsChecker(JobBase.JobBase):
    def executeEvery(self):
        return JobBase.JobFrequency.DAY_NOON
    def notifyOnFailureEvery(self):
        return JobBase.JobFailureNotificationFrequency.EVERYTIME
    def numberFailuresBeforeNotification(self):
        return JobBase.JobFailureCountMinimumBeforeNotification.ONE
    def execute(self):
        body = ""
        ys = datetime.date.today() - datetime.timedelta(hours=24)
        url = "https://collector.ritter.vg/recent/relay-descriptors/consensuses/"
        try:
            r = requests.get(url)
            this_consensus = str(ys.year) + "-" + str(ys.month).zfill(2) + "-" + str(ys.day).zfill(2) + "-12-00-00-consensus" 
            if this_consensus in r.text:
                pass
            else:
                body = "Could not find 12-00-00-consensus in the body:\n\n" + r.text
        except Exception as e:
            body = "Caught an exception:\n\n" + str(e)
        if body:
            logging.warn("tor metrics is broken?")
            logging.warn(body)
            self.logdetails = body
            return False
        else:
            return True
    def onFailure(self):
        return self.sendEmail("tor metrics is broken?", self.logdetails)

