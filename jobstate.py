#!/usr/bin/env python3

from builtins import str
from builtins import object
import time
import logging
import datetime


class JobState(object):
    def __init__(self, name, friendlyname):
        self.name = name
        self.friendlyname = friendlyname
        self.CurrentStateSuccess = True
        self.FirstFailureTime = 0
        self.LastNotifyTime = 0
        self.NumFailures = 0

    def markFailedAndNotify(self):
        # Confusing: In this function 'self' represents the lastRunStatus
        # and we know the current run has failed
        if self.CurrentStateSuccess:
            self.CurrentStateSuccess = False
            self.FirstFailureTime = time.time()
            self.LastNotifyTime = self.FirstFailureTime
            self.NumFailures = 1
        else:
            self.LastNotifyTime = time.time()
            self.NumFailures += 1

    def markFailedNoNotify(self):
        # Confusing: In this function 'self' represents the lastRunStatus
        # and we know the current run has failed
        if self.CurrentStateSuccess:
            self.CurrentStateSuccess = False
            self.FirstFailureTime = time.time()
            self.LastNotifyTime = 0
            self.NumFailures = 1
        else:
            self.NumFailures += 1

    def markSuccessful(self):
        # Confusing: In this function 'self' represents the lastRunStatus
        # and we know the current run has succeeded
        if self.CurrentStateSuccess:
            pass
        else:
            self.CurrentStateSuccess = True
            self.FirstFailureTime = 0
            self.LastNotifyTime = 0
            self.NumFailures = 0

    def serialize(self):
        ret = self.name + "|"
        ret += "Succeeding" if self.CurrentStateSuccess else "Failing"
        ret += "|" + str(self.FirstFailureTime)
        ret += "|" + str(self.LastNotifyTime) + "|"
        ret += self.friendlyname.replace("|", "#")  # Why yes, this is ugly!
        ret += "|" + str(self.NumFailures) + "\n"
        return ret

    @staticmethod
    def Parse(line):
        s = JobState("", "")

        line = line.strip()
        parts = line.split("|")

        s.name = parts[0]
        s.CurrentStateSuccess = True if parts[1] == "Succeeding" else False
        s.FirstFailureTime = float(parts[2])
        s.LastNotifyTime = float(parts[3])
        s.friendlyname = parts[4].replace("#", "|")

        if len(parts) > 5:
            s.NumFailures = int(parts[5])

        return s

    @staticmethod
    def Empty(name, friendlyname):
        s = JobState(name, friendlyname)
        return s
