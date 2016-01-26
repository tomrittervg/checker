#!/usr/bin/env python

import time
import logging
import requests

from jobs import JobFinder

class JobManager:
    def __init__(self, config):
        jobsFinder = JobFinder(config)
        self.jobs = jobsFinder.get_jobs()
        self.config = config

    def list_jobs(self):
        return self.jobs
    
    def execute_jobs(self, cronmode):
        logging.info("Executing jobs...")
        success = True
        for thisJob in self.jobs:
            thisJob.setConfig(self.config)
            if thisJob.shouldExecute(cronmode):
                logging.info("Executing " + thisJob.getName())
                if not thisJob.execute():
                    success = False
        return success
        
    def mark_jobs_ran(self):
        logging.debug("Marking jobs as run successfully.")
        try:
            requests.post("http://localhost:5001/", data="True")
        except:
            pass
            #Nothing we can do except hope our peers save us

    def mark_jobs_ran_with_error(self):
        logging.warning("Marking jobs as run unsuccessfully.")
        try:
            requests.post("http://localhost:5001/", data="False")
        except:
            pass
            #Nothing we can do except hope our peers save us
