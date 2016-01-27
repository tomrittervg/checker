#!/usr/bin/env python

import os
import time
import base64
import logging
import datetime 

import requests

import JobBase

class BWAuthChecker(JobBase.JobBase):
    def executeEvery(self):
        return JobBase.JobFrequency.HOUR
    def execute(self):
        body = ""
        url = "https://example.com/bwauth/bwscan.V3BandwidthsFile"
        try:
            r = requests.get(url)
            lines = r.content.split("\n")
            if len(lines) < 1:
                body = "Got no response from the server.\n\n" + r.content
            else:
                then = datetime.datetime.utcfromtimestamp(int(lines[0]))
                now = datetime.datetime.utcfromtimestamp(time.time())
                if now - then > datetime.timedelta(hours=2):
                    body = "The bandwidth file is more than 2 hours old.\n"
                    body += str((now-then).seconds / 60) + " minutes old.\n"
                elif len(lines) < 8800:
                    body = "The bandwidth file has a low number of relays: " + str(len(lines)) + "\n"
        except Exception as e:
            body = "Caught an exception:\n\n" + str(e)
        if body:
            logging.warn("tor bwauth is broken?")
            logging.warn(body)
            return self.sendEmail("tor bwauth is broken?", body)
        else:
            return True
