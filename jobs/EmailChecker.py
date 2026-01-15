#!/usr/bin/env python3

from builtins import str
import os
import base64
import datetime
import logging
import time

import imaplib

from . import JobBase


class EmailChecker(JobBase.JobBase):
    def executeEvery(self):
        return JobBase.JobFrequency.HOUR

    def notifyOnFailureEvery(self):
        return JobBase.JobFailureNotificationFrequency.EVERYTIME

    def numberFailuresBeforeNotification(self):
        return JobBase.JobFailureCountMinimumBeforeNotification.ONE

    def execute(self):
        if self.config.getboolean("email", "nomail"):
            logging.debug("Pretending the EmailChecker job succeeded.")
            return True

        USER = self.config.get("email", "user")
        PASS = self.config.get("email", "pass")
        FROM = self.config.get("email", "from", fallback=USER)

        logdetails = ""

        # Generate a random subject
        subj = base64.b64encode(os.urandom(20)).decode("utf-8")
        logdetails += "Target subject is " + subj + "\n\n"

        if not self.sendEmail(subj, "", FROM):
            return False

        if self.config.has_option("email", "imapwait"):
            wait = self.config.getint("email", "imapwait")
            logdetails += f"Waiting {wait}s before imap login"
            time.sleep(wait)

        M = imaplib.IMAP4_SSL(self.config.get("email", "imapserver"))
        M.login(USER, PASS)

        mailbox = self.config.get("email", "imapmailbox")
        logdetails += f"Switching to {mailbox}\n"
        M.select(mailbox)

        criteria = (
            '(FROM "'
            + FROM
            + '" SINCE "'
            + (datetime.date.today() - datetime.timedelta(hours=24)).strftime(
                "%d-%b-%Y"
            )
            + '")'
        )
        logdetails += "Criteria: " + criteria + "\n"
        typ, data = M.search(None, criteria)

        foundSubject = False
        for num in data[0].split():
            logdetails += "Found IMAP item" + str(num) + "\n"
            typ, data = M.fetch(num, "(BODY.PEEK[HEADER.FIELDS (Subject)])")
            logdetails += "IMAP details: " + str(data) + "\n"
            if subj.encode("utf-8") in data[0][1]:
                logdetails += "Found the target subject!!\n"
                foundSubject = True
        M.close()
        M.logout()

        self.logdetails = logdetails
        return foundSubject

    def onFailure(self):
        return self.sendEmail("Email Fetch Failure", self.logdetails)
