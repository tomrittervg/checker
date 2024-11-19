#!/usr/bin/env python3

import os
import sys
import inspect
import logging
import importlib
import traceback

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
        self._jobs = set()
        self.config = config
        
        job_modules = self.get_job_modules_dynamic()
        
        for module in job_modules:
            # Check every declaration in that module
            for name in dir(module):
                obj = getattr(module, name)
                if name not in module.__name__:
                    # Jobs have to have the same class name as their module name
                    continue
                
                if inspect.isclass(obj):
                    # A class declaration was found in that module
                    # Checking if it's a subclass of JobBase
                    if obj != jobs.JobBase.JobBase and obj != jobs.JobSpawner.JobSpawner:
                        logging.info(f"Found {obj}")
                        if issubclass(obj, jobs.JobBase.JobBase):
                            # A job was found, keep it
                            self._jobs.add(obj(self.config))
                        elif issubclass(obj, jobs.JobSpawner.JobSpawner):
                            spawner = obj()
                            for j in spawner.get_sub_jobs(self.config):
                                self._jobs.add(j)
                                
    def get_job_modules_dynamic(self):
        job_modules = []
        
        job_dir = jobs.__path__[0]
        full_job_dir = os.path.join(sys.path[0], job_dir)
        if os.path.exists(full_job_dir):
            for root, dirs, files in os.walk(full_job_dir):
                del dirs[:]  # Do not walk into subfolders of the job directory
                jobs_loaded = []
                for source in (s for s in files if s.endswith(".py")):
                    module_name = os.path.splitext(os.path.basename(source))[0]
                    if module_name in jobs_loaded:
                        continue
                    jobs_loaded.append(module_name)
                    full_name = os.path.splitext(source)[0].replace(os.path.sep, '.')
                    
                    try:
                        # Try to import the job package
                        module = importlib.import_module(f"jobs.{full_name}")
                    except Exception as e:
                        logging.critical(f"Import Error on {module_name}: {repr(e)}")
                        logging.critical(traceback.format_exc())
                        jobs.JobBase.sendEmail(self.config, f"Import Error on {module_name}", str(e))
                        continue
                    job_modules.append(module)
        return job_modules
                
    def get_jobs(self):
        return self._jobs
