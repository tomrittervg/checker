#!/usr/bin/env python

import os
import time
import logging
import datetime
import requests

from jobs import JobFinder, JobBase
from jobstate import JobState

class JobManager:
    def __init__(self, config):
        jobsFinder = JobFinder(config)
        self.jobs = jobsFinder.get_jobs()
        self.config = config
        self.statefile = config.get('general', 'statefile')
        self._load_state()

    def _load_state(self):
        self.state = {}
        if not os.path.isfile(self.statefile):
            logging.warn("Could not find statefile at " + self.statefile + "; creating a new one.")
        else:
            f = open(self.statefile, "r")
            lines = f.readlines()
            for l in lines:
                s = JobState.Parse(l)
                self.state[s.name] = s
            f.close()

    def _save_state(self):
        logging.info("Saving State...")
        f = open(self.statefile, "w")
        for i in self.state:
            f.write(self.state[i].serialize())
        f.close()

    def list_jobs(self):
        return self.jobs
    
    def execute_jobs(self, cronmode):
        logging.info("Executing jobs...")
        emailWorks = True
        for thisJob in self.jobs:
            if thisJob.shouldExecute(cronmode):
                logging.info("Executing " + thisJob.getName() + "(" + thisJob.getStateName() + ")")
                try:
                    lastRunStatus = self.state[thisJob.getStateName()]
                except:
                    logging.warn("No state was found for " + thisJob.getStateName() + \
                                 ", making up a dummy state for it.")
                    lastRunStatus = self.state[thisJob.getStateName()] = JobState.Empty(thisJob.getStateName(), thisJob.getName())

                if not thisJob.execute():
                    #Unsuccessful run
                    logging.info("Execution of " + thisJob.getName() + " failed")
                    if thisJob.shouldNotifyFailure(lastRunStatus):
                        lastRunStatus.markFailedAndNotify()
                        logging.info("Notifying of failure for " + thisJob.getName())
                        if not thisJob.onFailure():
                            emailWorks = False
                    else:
                        logging.info("Skipping notification of failure for " + thisJob.getName())
                        lastRunStatus.markFailedNoNotify()
                else:
                    #Successful Run
                    logging.info("Execution of " + thisJob.getName() + " succeeded")
                    if lastRunStatus.CurrentStateSuccess == False and \
                        thisJob.notifyOnFailureEvery() == JobBase.JobFailureNotificationFrequency.ONSTATECHANGE and \
                        lastRunStatus.NumFailures >= thisJob.numberFailuresBeforeNotification():
                        if not thisJob.onStateChangeSuccess():
                            emailWorks = False
                    lastRunStatus.markSuccessful()
        self._save_state()
        return emailWorks
        
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
