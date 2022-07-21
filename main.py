#!/usr/bin/env python3

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
import os
import sys
import json
import pickle
import hashlib
import logging
import argparse
import binascii
import configparser

import requests

from twisted.internet import reactor, ssl
from twisted.web import server

from jobmanager import JobManager
from statustracker import StatusTracker
from servers import StatusSite, PingSite

# We only run one command on the hour and day marks, but we need to execute all the jobs in that instance,
# including our minute jobs and hour jobs
def convert_crontimes(crontime):
    ret = ["minute"]
    if crontime == "minute":
        pass
    elif crontime == "hour":
        ret.append("hour")
    elif crontime == "day":
        ret.append("hour")
        ret.append("day")
    elif crontime == "day_noon":
        ret.append("hour")
        ret.append("day_noon")
    return ret
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check your stuff.")
    parser.add_argument('-m', '--mode', choices=['daemon', 'cron'], required=True, help='The mode the application will run it.')
    parser.add_argument('-c', '--crontime', choices=['minute', 'hour', 'day', 'day_noon'], help='When in cron mode, the increment of cron.')
    parser.add_argument('-v', action="store_true", help="Print verbose debugging information to the logfile")
    parser.add_argument('-d', action="store_true", help="Print verbose debugging information to stderr")
    parser.add_argument('--nomail', action="store_true", help="Do everything except sending email")
    parser.add_argument('-f', '--config', help="Configuration file (default: settings.cfg)")

    args = parser.parse_args()

    config = configparser.ConfigParser()
    if args.config:
        config.read(args.config)
    else:
        config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings.cfg'))
    if args.nomail:
        config.set('email', 'nomail', "True")

    if not config.getboolean('email', 'nomail') and (\
        not config.get('email', 'user') or \
        not config.get('email', 'pass') or \
        not config.get('email', 'smtpserver') or \
        not config.get('email', 'smtpport') or \
        not config.get('email', 'imapserver')):
        print("Sending email address is not configured")
        sys.exit(1)
    if not config.get('general', 'servername') or \
        not config.get('general', 'alertcontact'):
        print("Default alert contact is not configured")
        sys.exit(1)



    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.CRITICAL)
    log_formatter = logging.Formatter(fmt="%(asctime)s:%(levelname)s:  %(message)s")
    log = logging.getLogger()
    if args.v:
        log.setLevel(logging.DEBUG)
        log_file_handler = logging.FileHandler(config.get('general', 'logfile'))
        log_file_handler.setFormatter(log_formatter)
        log.addHandler(log_file_handler)
    if args.d:
        log.setLevel(logging.DEBUG)
        log_stderr_handler = logging.StreamHandler()
        log_stderr_handler.setFormatter(log_formatter)
        log.addHandler(log_stderr_handler)

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
            log.info("Running cron at frequencies " + str(convert_crontimes(args.crontime)))
            try:
                if jobManager.execute_jobs(convert_crontimes(args.crontime)):
                    jobManager.mark_jobs_ran()
                else:
                    jobManager.mark_jobs_ran_with_error()
            except Exception as e:
                logging.critical("Caught an exception trying to execute jobs:" + repr(e))
                logging.critical(logging.traceback.format_exc())
                jobManager.mark_jobs_ran_with_error()
