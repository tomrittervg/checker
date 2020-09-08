#!/usr/bin/env python3

from builtins import str
from builtins import object
import time
import random
import base64
import logging
import datetime

import smtplib

class JobFrequency(object):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    DAY_NOON = "day_noon"

class JobFailureNotificationFrequency(object):
    EVERYTIME = "every"
    EVERYFIVEMINUTES = "5min"
    EVERYTENMINUTES = "10min"
    EVERYHOUR = "hour"
    EVERYDAY = "day"
    ONSTATECHANGE = "state_change"

class JobFailureCountMinimumBeforeNotification(object):
    ONE = 1
    TWO = 2
    FIVE = 5
    TEN = 10

class JobBase(object):
    def __init__(self, config, *args):
        self.config = config
        statename = self.getName() + "|" + "|".join([str(a) for a in args])
        self.stateName = base64.b64encode(statename.encode("utf-8")).decode("utf-8")

    """ Return a friendly name to identify this Job"""
    def getName(self):
        return str(self.__class__)

    """Return a non-friendly, guarenteed-unique name to identify this Job
       Needed to keep track of the job's run history. 
       Takes into account the contructor arguments to uniquely identify JobSpawner-jobs"""
    def getStateName(self):
        return self.stateName

    """Returns True if the job should execute this cron-run"""
    def shouldExecute(self, cronmodes):
        frequency = self.executeEvery()
        if frequency in cronmodes:
            return True
        return False

    """Returns True if the jobmanager should call 'onFailure' to alert the admin after a job failed"""
    def shouldNotifyFailure(self, jobState):
        notifyFrequency = self.notifyOnFailureEvery()
        minFailureCount = self.numberFailuresBeforeNotification()
        currentFailureCount = jobState.NumFailures

        if 1 + currentFailureCount >= minFailureCount:
            pass #keep evaluating
        else:
            return False #Do not notify

        if notifyFrequency == JobFailureNotificationFrequency.EVERYTIME:
            return True
        elif notifyFrequency == JobFailureNotificationFrequency.EVERYFIVEMINUTES:
            now = time.time()
            lastNotify = jobState.LastNotifyTime
            if datetime.timedelta(seconds=(now - lastNotify)) > datetime.timedelta(minutes=4, seconds=30):
                return True
            return False
        elif notifyFrequency == JobFailureNotificationFrequency.EVERYTENMINUTES:
            now = time.time()
            lastNotify = jobState.LastNotifyTime
            if datetime.timedelta(seconds=(now - lastNotify)) > datetime.timedelta(minutes=9, seconds=15):
                return True
            return False
        elif notifyFrequency == JobFailureNotificationFrequency.EVERYHOUR:
            now = time.time()
            lastNotify = jobState.LastNotifyTime
            if datetime.timedelta(seconds=(now - lastNotify)) > datetime.timedelta(minutes=59, seconds=0):
                return True
            return False
        elif notifyFrequency == JobFailureNotificationFrequency.EVERYDAY:
            now = time.time()
            lastNotify = jobState.LastNotifyTime
            if datetime.timedelta(seconds=(now - lastNotify)) > datetime.timedelta(hours=23, minutes=50, seconds=0):
                return True
            return False
        elif notifyFrequency == JobFailureNotificationFrequency.ONSTATECHANGE:
            if minFailureCount == 1:
                # If we notify on the first failure, only notify if the last JobState was a Success
                return jobState.CurrentStateSuccess
            else:
                # If we notify after N failures, only notify if this is exactly the nth failure
                return 1 + currentFailureCount == minFailureCount
        return True

    """Helper method to send email"""
    def sendEmail(self, subject, body, to=""):
        return sendEmail(self.config, subject, body, to)


    """OVERRIDE ME
        Returns a JobFrequency indicating how often the job should be run."""
    def executeEvery(self):
        pass

    """OVERRIDE ME
        Returns a JobFailureNotificationFrequency indicating how often a failure 
        notification email should be sent"""
    def notifyOnFailureEvery(self):
        pass

    """OVERRIDE ME
        Returns a JobFailureCountMinimumBeforeNotification indicating how many 
        failures should occur before a notification email should be sent"""
    def numberFailuresBeforeNotification(self):
        pass

    """OVERRIDE ME
       Executes the job's actions, and returns true to indicate the job succeeded."""
    def execute(self):
        pass

    """OVERRIDE ME
       Notify the admin the job failed. Returns True if the email could be 
       successfully sent.
       Example: return self.sendEmail(self.subject, self.body, self.notificationAddress)"""
    def onFailure(self):
        pass

    """OVERRIDE ME
       Notify the admin the job succeeded (when it was previously failing). Only used for
       JobFailureNotificationFrequency.ONSTATECHANGE

       Returns True if the email could be successfully sent.
       Example: return self.sendEmail(self.subject, self.body, self.notificationAddress)"""
    def onStateChangeSuccess(self):
        log.warn(self.getName() + " did not override onStateChangeSuccess")
        return True

def sendEmail(config, subject, body, to=""):
    if config.getboolean('email', 'nomail'):
        logging.info("Not sending email with subject '" + subject + '" but pretending we did.\n' + body)
        return True

    FROM = config.get('email', 'user')
    PASS = config.get('email', 'pass')
    if not to:
        to = config.get('general', 'alertcontact')

    # Prepare actual message
    # Avoid gmail threading
    subject = "[" + config.get('general', 'servername') + "] " + subject + "       " 
    if config.getboolean('email', 'bustgmailthreading'):
        subject += str(random.random())
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s""" \
        % (FROM, ", ".join(to), subject, body)
    try:
        server = smtplib.SMTP(config.get('email', 'smtpserver'), config.get('email', 'smtpport'))
        server.ehlo()
        server.starttls()
        server.login(FROM, PASS)
        server.sendmail(FROM, to, message)
        server.close()
        return True
    except Exception as e:
        logging.critical("Caught an exception trying to send an email:" + str(e))
        return False
