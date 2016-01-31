#!/usr/bin/env python

import os
import base64
import datetime 
import logging

import imaplib

import JobBase

class EmailChecker(JobBase.JobBase):
    def executeEvery(self):
        return JobBase.JobFrequency.HOUR
    def notifyOnFailureEvery(self):
        return JobBase.JobFailureNotificationFrequency.EVERYTIME
    def execute(self):
        USER = self.config.get('email', 'user')
        PASS = self.config.get('email', 'pass')

    	logdetails = ""
        
        #Generate a random subject
        subj = base64.b64encode(os.urandom(20))
        logdetails += "Target subject is " + subj + "\n\n"
        
        if not self.sendEmail(subj, "", USER):
            return False
        
        M = imaplib.IMAP4_SSL(self.config.get('email', 'imapserver'))
        M.login(USER, PASS)
        
        #If we have set up a filter to auto-delete messages from ourself
        if self.config.getboolean('email', 'ideletesentmessagesautomatically'):
            logdetails += "Switching to trash\n"
            M.select("[Gmail]/Trash")
        
        criteria = '(FROM "'+USER+'" SINCE "'+(datetime.date.today() - datetime.timedelta(hours=24)).strftime("%d-%b-%Y")+'")'
        logdetails += "Criteria: " + criteria + "\n"
        typ, data = M.search(None, criteria)
        
        foundSubject = False
        for num in data[0].split():
            logdetails += "Found IMAP item" + str(num) + "\n"
            typ, data = M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (Subject)])')
            logdetails += "IMAP details: " + str(data) + "\n"
            if subj in data[0][1]:
                logdetails += "Found the target subject!!\n"
                foundSubject = True
        M.close()
        M.logout()

        self.logdetails = logdetails
        return foundSubject
    def onFailure(self):
        return self.sendEmail("Email Fetch Failure", self.logdetails)
            
