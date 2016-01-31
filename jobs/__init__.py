#!/usr/bin/env python

import os
import sys
import inspect
import logging
from imp import load_module, find_module
import importlib

import jobs
import jobs.JobBase
import jobs.JobSpawner

class JobFinder:
    def __init__(self, config):
        """
        Opens the jobs folder and looks at every .py module in that directory.
        Finds available jobs by looking at any class defined in those modules
        that implements the JobBase abstract class.
        Returns a list of job classes.
        """
        self._jobs = set([])
        self.config = config
        
        job_modules = self.get_job_modules_dynamic()
        
        for module in job_modules:
            # Check every declaration in that module
            for name in dir(module):
                obj = getattr(module, name)
                if name not in module.__name__:
                    # Jobs have to have the same class name as their module name
                    # This prevents Job B from being detected twice when there is a Job A that imports Job B
                    continue

                if inspect.isclass(obj):
                    # A class declaration was found in that module
                    # Checking if it's a subclass of JobBase
                    # Discarding JobBase as a subclass of JobBase
                    if obj != jobs.JobBase.JobBase and obj != jobs.JobSpawner.JobSpawner:
                        logging.info("Found " + str(obj))
                        for base in obj.__bases__:
                            # H4ck because issubclass() doesn't seem to work as expected on Linux
                            # It has to do with JobBase being imported multiple times (within jobs) or something
                            if base.__name__ == 'JobBase':
                                # A job was found, keep it
                                self._jobs.add(obj(self.config))
                            elif base.__name__ == 'JobSpawner':
                                spawner = obj()
                                for j in spawner.get_sub_jobs(self.config):
                                    self._jobs.add(j)

    
    def get_job_modules_dynamic(self):
        job_modules = []

        job_dir = jobs.__path__[0]
        full_job_dir = os.path.join(sys.path[0], job_dir)
        if os.path.exists(full_job_dir):
            for (root, dirs, files) in os.walk(full_job_dir):
                del dirs[:] # Do not walk into subfolders of the job directory
                # Checking every .py module in the job directory
                jobs_loaded = []
                for source in (s for s in files if s.endswith((".py"))):
                    module_name = os.path.splitext(os.path.basename(source))[0]
                    if module_name in jobs_loaded:
                        continue
                    jobs_loaded.append(module_name)
                    full_name = os.path.splitext(source)[0].replace(os.path.sep,'.')

                    try: # Try to import the job package
                    # The job package HAS to be imported as a submodule
                    # of module 'jobs' or it will break windows compatibility
                        (file, pathname, description) = \
                            find_module(full_name, jobs.__path__)
                        module = load_module('jobs.' + full_name, file,
                                                pathname, description)
                    except Exception as e:
                        logging.critical('Import Error on ' + module_name + ': ' + str(e))
                        jobs.JobBase.sendEmail(self.config, 'Import Error on ' + module_name, str(e))
                        continue
                    job_modules.append(module)
        return job_modules
    
    def get_jobs(self):
        return self._jobs