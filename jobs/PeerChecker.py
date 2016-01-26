#!/usr/bin/env python

import os
import base64
import datetime 

import imaplib
import requests

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

            subject = ""
            body = ""

            try:
                response = requests.get(peer[0])
                if response.status_code != 200:
                    peerOK = False
                    subject = peer[0] + " returned a non-standard status code."
                    body = str(response.status_code) + "\n" + response.content
                else:
                    if "True" in response.content:
                        peerOK = True
                    elif "MailProblem" in response.content:
                        peerOK = False
                        subject = peer[0] + " reports it cannot send email."
                        body = str(response.status_code) + "\n" + response.content
                    elif "JobProblem" in response.content:
                        peerOK = False
                        subject = peer[0] + " reports its jobs are not running."
                        body = str(response.status_code) + "\n" + response.content
                    else:
                        peerOK = False
                        subject = peer[0] + " had an unexpected response."
                        body = str(response.status_code) + "\n" + response.content
            except Exception as e:
                peerOK = False
                subject = peer[0] + " is not responding."
                body = str(e)
            
            if not peerOK:
                if not self.sendEmail(subject, body, peer[1]):
                    testSuccess = False
        return testSuccess
