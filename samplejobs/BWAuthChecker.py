#!/usr/bin/env python

import os
import re
import time
import base64
import logging
import datetime 

import requests

import JobBase

class BWAuthChecker(JobBase.JobBase):
    def executeEvery(self):
        return JobBase.JobFrequency.HOUR
    def notifyOnFailureEvery(self):
        return JobBase.JobFailureNotificationFrequency.EVERYTIME
    def execute(self):
        body = ""
        url = "https://bwauth.ritter.vg/bwauth/bwscan.V3BandwidthsFile"
        try:
            r = requests.get(url)
            lines = r.content.split("\n")
            if len(lines) < 1:
                body = "Got no response for " + url + " from the server.\n\n" + r.content
            else:
                then = datetime.datetime.utcfromtimestamp(int(lines[0]))
                now = datetime.datetime.utcfromtimestamp(time.time())
                if now - then > datetime.timedelta(hours=4):
                    body = "The bandwidth file is more than 4 hours old.\n"
                    body += str((now-then).seconds / 60) + " minutes old.\n"
                elif len(lines) < 8300:
                    body = "The bandwidth file has a low number of relays: " + str(len(lines)) + "\n"
        except Exception as e:
            body = "Caught an exception checking the bwandwidth file timestamp:\n\n" + str(e)

        url = "https://bwauth.ritter.vg/bwauth/AA_percent-measured.txt"
        try:
            r = requests.get(url)
            lines = r.content.split("\n")
            if len(lines) < 1:
                body += "\n\nGot no response for " + url + " from the server.\n\n" + r.content
            else:
                i = -1
                while not lines[i].strip():
                    i -= 1
                g = re.match('NOTICE\[.+\]:Measured ([0-9].+)% of all tor nodes', lines[i])
                if not g:
                    body += "\n\nCould not find the measured percentage at " + url
                else:
                    percent = float(g.groups(0)[0])
                    if percent < 96:
                        body += "\n\nMeasured percentant of all tor nodes is low: " + str(percent)
        except Exception as e:
            body += "\n\nCaught an exception measuring the percentage of relays measured:\n\n" + str(e)
                    

        url = "https://bwauth.ritter.vg/bwauth/AA_scanner_loop_times.txt"
        try:
            r = requests.get(url)
            lines = r.content.split("\n")
            if len(lines) < 1:
                body += "\n\nGot no response for " + url + " from the server.\n\n" + r.content
            else:
                this_scanner = 0
                last_measured = None
                measurement_times = {}
                for l in lines:
                    if "Scanner" in l:
                        if this_scanner != 0:
                            measurement_times[this_scanner] = last_measured
                        this_scanner = int(l.replace("Scanner ", "").strip())
                    elif l.strip():
                        last_measured = re.match("NOTICE\[[^\s]+ ([0-9a-zA-Z: ]+)\]", l).groups(0)[0]
                        last_measured = datetime.datetime.strptime(last_measured, "%b %d %H:%M:%S %Y")

                for t in measurement_times:
                    if measurement_times[t] + datetime.timedelta(days=6) < datetime.datetime.now():
                        body += "\n\nhttps://bwauth.ritter.vg/bwauth/AA_scanner_loop_times.txt\n"
                        body += "Scanner " + str(t) + " appears to be several days behind schedule."
        except Exception as e:
            body += "\n\nCaught an exception measuring the scanner loop times:\n\n" + str(e)

        if body:
            logging.warn("tor bwauth is broken?")
            logging.warn(body)
            self.logdetails = body
            return False
        else:
            return True
    def onFailure(self):
        return self.sendEmail("tor bwauth is broken?", self.logdetails)
