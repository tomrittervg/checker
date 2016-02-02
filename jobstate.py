#!/usr/bin/env python

import time
import logging
import datetime

class JobState:
	def __init__(self, name, friendlyname):
		self.name = name
		self.friendlyname = friendlyname
		self.CurrentStateSuccess = True
		self.FirstFailureTime = 0
		self.LastNotifyTime = 0

	def markFailedAndNotify(self):
		if self.CurrentStateSuccess:
			self.CurrentStateSuccess = False
			self.FirstFailureTime = time.time()
			self.LastNotifyTime = self.FirstFailureTime
		else:
			self.LastNotifyTime = time.time()

	def markFailedNoNotify(self):
		if self.CurrentStateSuccess:
			logging.warn("Somehow we called markFailedNoNotify, on a success condition, without notifying the user")
			self.CurrentStateSuccess = False
			self.FirstFailureTime = time.time()
			self.LastNotifyTime = 0
		else:
			pass

	def markSuccessful(self):
		if self.CurrentStateSuccess:
			pass
		else:
			self.CurrentStateSuccess = True
			self.FirstFailureTime = 0
			self.LastNotifyTime = 0

	def serialize(self):
		ret  = self.name + "|" 
		ret += "Succeeding" if self.CurrentStateSuccess else "Failing"
		ret += "|" + str(self.FirstFailureTime)
		ret += "|" + str(self.LastNotifyTime) + "|"
		ret += self.friendlyname + "\n"
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
		s.friendlyname = parts[4] 

		return s

	@staticmethod
	def Empty(name, friendlyname):
		s = JobState(name, friendlyname)
		return s
