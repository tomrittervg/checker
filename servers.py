#!/usr/bin/env python3

import logging

from twisted.python.filepath import FilePath
from twisted.web import server, resource, http

class StatusSite(resource.Resource):
    isLeaf = True
    def __init__(self, statusTracker):
        resource.Resource.__init__(self)
        self.statusTracker = statusTracker
    def render_GET(self, request):
        if self.statusTracker.isMailGood() and self.statusTracker.isJobsGood():
            logging.debug("Indicating that everything seems to be okay")
            s = "True"
        elif not self.statusTracker.isMailGood():
            logging.warn("Indicating that we have a problem with Mail")
            s = "MailProblem"
        elif not self.statusTracker.isJobsGood():
            logging.warn("Indicating that we have a problem with Jobs")
            s = "JobProblem"

        request.setResponseCode(200)
        return s.encode("utf-8")

class PingSite(resource.Resource):
    isLeaf = True
    def __init__(self, statusTracker):
        resource.Resource.__init__(self)
        self.statusTracker = statusTracker
    def render_POST(self, request):
        self.statusTracker.markJobRan()
        emailStatus = request.content.read()
        emailStatus = "True" in emailStatus
        
        logging.debug("Got notification of jobs ran")
        if emailStatus:
            logging.debug("Email is working")
        else:
            logging.warn("Email is _not_ working")

        self.statusTracker.markEmailStatus(emailStatus)
        request.setResponseCode(200)
        return "OK".encode("utf-8")

