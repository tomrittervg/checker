#!/usr/bin/env python

import random
import logging

import smtplib

class JobFrequency:
    MINUTE = "minute"
    HOUR = "hour"

class JobBase:
    def __init__(self):
        self.config = None
    def getName(self):
        return str(self.__class__)
    def shouldExecute(self, cronmode):
        frequency = self.executeEvery()
        if cronmode == frequency:
            return True
        return False
    def setConfig(self, config):
        self.config = config
       
    def sendEmail(self, subject, body, to=""):
        return sendEmail(self.config, subject, body, to)

    def executeEvery(self):
        pass
    def execute(self):
        pass

def sendEmail(config, subject, body, to=""):
    FROM = config.get('email', 'user')
    PASS = config.get('email', 'pass')
    if not to:
        to = config.get('general', 'alertcontact')

    # Prepare actual message
    # Avoid gmail threading
    subject = "[" + config.get('general', 'servername') + "] " + subject + "       " + str(random.random())
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
