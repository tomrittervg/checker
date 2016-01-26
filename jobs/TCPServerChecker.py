#!/usr/bin/env python

import os
import socket
import logging

import JobBase
import JobSpawner

class TCPServerChecker(JobSpawner.JobSpawner):
    servers = [ 
                #("example.com", 53, "example.com:tcpdns", JobBase.JobFrequency.MINUTE),
              ]

    class ServerChecker(JobBase.JobBase):
        def __init__(self, ip, port, friendlyName, frequency):
            self.ip = ip
            self.port = port
            self.friendlyName = friendlyName + "(" + self.ip + ":" + str(self.port) + ")"
            self.frequency = frequency

        def getName(self):
            return str(self.__class__) + " for " + self.friendlyName
        def executeEvery(self):
            return self.frequency
        def execute(self):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.ip, self.port))
                s.close()
                return True
            except:
                msg = "Could not hit server " + self.friendlyName
                logging.warn(msg)
                return self.sendEmail(msg, "")

    def get_sub_jobs(self):
        for s in self.servers:
            yield self.ServerChecker(s[0], s[1], s[2], s[3])

            
