#!/usr/bin/env python

import os
import base64
import logging
import datetime 

import requests

import JobBase

class MetricsChecker(JobBase.JobBase):
    def executeEvery(self):
        return JobBase.JobFrequency.DAY_NOON
    def execute(self):
        body = ""
        ys = datetime.date.today() - datetime.timedelta(hours=24)
        url = "https://example.com/out/relay-descriptors/consensus/" + str(ys.year) + "/" + str(ys.month).zfill(2) + "/" + str(ys.day).zfill(2) + "/"
        try:
            r = requests.get(url)
            if "12-00-00-consensus" in r.content:
                pass
            else:
                body = "Could not find 12-00-00-consensus in the body:\n\n" + r.content
        except Exception as e:
            body = "Caught an exception:\n\n" + str(e)
        if body:
            logging.warn("tor metrics is broken?")
            logging.warn(body)
            return self.sendEmail("tor metrics is broken?", body)
        else:
            return True
