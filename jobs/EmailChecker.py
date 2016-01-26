#!/usr/bin/env python

import os
import base64
import datetime 

import imaplib

import JobBase

class EmailChecker(JobBase.JobBase):
    def executeEvery(self):
        return JobBase.JobFrequency.HOUR
    def execute(self):
        USER = self.config.get('email', 'user')
        PASS = self.config.get('email', 'pass')
        
        #Generate a random subject
        subj = base64.b64encode(os.urandom(20))
        
        if not self.sendEmail(subj, "", USER):
            return False
        
        M = imaplib.IMAP4_SSL(self.config.get('email', 'imapserver'))
        M.login(USER, PASS)
        
        #If we have set up a filter to auto-delete messages from ourself
        if self.config.get('email', 'ideletesentmessagesautomatically'):
            M.select("[Gmail]/Trash")
        
        criteria = '(FROM "'+USER+'" SINCE "'+datetime.date.today().strftime("%d-%b-%Y")+'")'
        typ, data = M.search(None, criteria)
        
        foundSubject = False
        for num in data[0].split():
            typ, data = M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (Subject)])')
            if subj in data[0][1]:
                foundSubject = True
        M.close()
        M.logout()
        if not foundSubject:
            #This may not work, but try anyway
            self.sendEmail("Email Fetch Failure", "")
            return False
        else:
            return True
