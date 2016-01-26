#!/usr/bin/env python

import logging

from twisted.python.filepath import FilePath
from twisted.web import server, resource, http

class StatusSite(resource.Resource):
    isLeaf = True
    def __init__(self, statusTracker):
        resource.Resource.__init__(self)
        self.statusTracker = statusTracker
    def render_GET(self, request):
        if self.statusTracker.isAllGood():
            logging.debug("Indicating that everything seems to be okay")
            s = "True"
        else:
            logging.warn("Indicating that everything does not seem to be okay")
            s = "False"

        request.setResponseCode(200)
        return s

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
        return "OK"

