#!/usr/bin/env python

import os
import sys
import json
import pickle
import hashlib
import logging
import argparse
import binascii
import ConfigParser

import requests

from twisted.internet import reactor, ssl
from twisted.web import server

from jobmanager import JobManager
from statustracker import StatusTracker
from servers import StatusSite, PingSite
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check your stuff.")
    parser.add_argument('-m', '--mode', choices=['daemon', 'cron'], required=True, help='The mode the application will run it.')
    parser.add_argument('-c', '--crontime', choices=['minute', 'hour'], help='When in cron mode, the increment of cron.')
    parser.add_argument('-v', action="store_true", help="Print verbose debugging information to stderr")

    args = parser.parse_args()

    config = ConfigParser.ConfigParser()
    config.read('settings.cfg')
    if not config.get('email', 'user') or \
        not config.get('email', 'pass') or \
        not config.get('email', 'smtpserver') or \
        not config.get('email', 'smtpport') or \
        not config.get('email', 'imapserver'):
        print "Sending email address is not configured"
        sys.exit(1)
    if not config.get('alertcontact', 'default'):
        print "Default alert contact is not configured"
        sys.exit(1)



    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.CRITICAL)
    logging.basicConfig(format="%(asctime)s:%(levelname)s:  %(message)s")
    log = logging.getLogger()
    if args.v:
        log.setLevel(logging.DEBUG)

    if args.mode == 'daemon':
        log.info("Starting up daemon")
        statusTracker = StatusTracker(config)
        reactor.listenTCP(5000, server.Site(StatusSite(statusTracker)))
        reactor.listenTCP(5001, server.Site(PingSite(statusTracker)), interface='127.0.0.1')
        reactor.run()
    elif args.mode == 'cron':
        jobManager = JobManager(config)
        if not args.crontime:
            log.warn("Did not run cron, no crontime specified")
            parser.print_help()
            sys.exit(-1)
        else:
            log.info("Running cron at frequency " + args.crontime)
            if jobManager.execute_jobs(args.crontime):
                jobManager.mark_jobs_ran()
            else:
                jobManager.mark_jobs_ran_with_error()
