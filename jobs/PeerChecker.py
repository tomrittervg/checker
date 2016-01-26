#!/usr/bin/env python

import os
import base64
import datetime 

import imaplib

import JobBase

class PeerChecker(JobBase.JobBase):
    def executeEvery(self):
        return JobBase.JobFrequency.HOUR
    def execute(self):
        testSuccess = True
        peers = self.config.items('peers')
        for p in peers:
            peer = p[1].split(',')
            peerOK = False

            try:
                response = requests.get(peer[0])
                if response.status_code != 200:
                    peerOK = False
                    subject = peer[0] + " returned a non-standard status code."
                else:
                    if "True" in response.content:
                        peerOK = True
                    elif "False" in response.content:
                        peerOK = False
                        subject = peer[0] + " reports it cannot send email."
            except:
                peerOK = False
                subject = peer[0] + " is not responding."
            
            if not peerOK:
                if not self.sendEmail(subject, "", peer[1]):
                    testSuccess = False
        return testSuccess