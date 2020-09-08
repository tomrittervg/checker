#!/usr/bin/env python3

from __future__ import absolute_import
from builtins import str
import os
import base64
import datetime 

import imaplib
import requests

from . import JobBase
from . import JobSpawner

class PeerChecker(JobSpawner.JobSpawner):
    class IndividualPeerChecker(JobBase.JobBase):
        def __init__(self, config, checkurl, notificationAddress):
            self.checkurl = checkurl
            self.notificationAddress = notificationAddress
            super(PeerChecker.IndividualPeerChecker, self).__init__(config, checkurl, notificationAddress)

        def getName(self):
            return str(self.__class__) + " for " + self.checkurl
        def executeEvery(self):
            return JobBase.JobFrequency.HOUR
        def notifyOnFailureEvery(self):
            return JobBase.JobFailureNotificationFrequency.EVERYTIME
        def numberFailuresBeforeNotification(self):
            return JobBase.JobFailureCountMinimumBeforeNotification.ONE
        def execute(self):
            peerOK = False

            self.subject = ""
            self.body = ""

            try:
                response = requests.get(self.checkurl)
                if response.status_code != 200:
                    peerOK = False
                    self.subject = self.checkurl + " returned a non-standard status code."
                    self.body = str(response.status_code) + "\n" + response.content
                else:
                    if "True" in response.content:
                        peerOK = True
                    elif "MailProblem" in response.content:
                        peerOK = False
                        self.subject = self.checkurl + " reports it cannot send email."
                        self.body = str(response.status_code) + "\n" + response.content
                    elif "JobProblem" in response.content:
                        peerOK = False
                        self.subject = self.checkurl + " reports its jobs are not running."
                        self.body = str(response.status_code) + "\n" + response.content
                    else:
                        peerOK = False
                        self.subject = self.checkurl + " had an unexpected response."
                        self.body = str(response.status_code) + "\n" + response.content
            except Exception as e:
                peerOK = False
                self.subject = self.checkurl + " is not responding."
                self.body = str(e)
            return peerOK

        def onFailure(self):
            return self.sendEmail(self.subject, self.body, self.notificationAddress)
        def onStateChangeSuccess(self):
            return self.sendEmail("Successfully hit " + self.checkurl, "", self.notificationAddress)

    def get_sub_jobs(self, config):
        peers = config.items('peers')
        for p in peers:
            (address, email) = p[1].split(',')
            yield self.IndividualPeerChecker(config, address, email)
