# Checker

Checker is a monitoring service that is designed to alert you when things are going wrong with the various things you care about. It has sample jobs that can ping TCP ports and HTTP servers, and you can run any job you care about by writing a python class.

# Design

The primary problem with any sort of monitoring service is: "How do I know the monitoring service is running?".  Checker fixes this with two system jobs.

### Email Check

Checker is designed to send you email alerts when things break. To make sure its emails are getting through, Checker will email itself and confirm that it can recieve its own emails. If it can, it assumes that it can successfully email _you_.  It's your job to make sure it doesn't go into the spam bin.

### Peer Check

Checker can't (reliably) run by itself. It needs to have at least one peer. Checker will ask its peers if they're still running successfully. There are four answers a peer can give (and that it can give a peer): 

* I'm running fine (Success)
* I can't send email (Error)
* I don't seem to be running any jobs (Error)
* (No Response) (Error)

When checker sees that one of its peers has reported one of the three error conditions, it emails that peer's admin.  

Peering should be symmetrical - you check your friend's instance and your friend checks yours. Or you can run it yourself on two servers (when you do this, you only need one server to run all the jobs, the other one can just run as a no-job peer).

# Custom Jobs

This wouldn't be any good if you couldn't specify your own custom jobs. There are two ways to do this:

### Inherit JobBase

JobBase is the base for a job, and should be used when you have a single, custom job you want to run.  Your job needs to match the name of the file it is in. You should override two functions:

* executeEvery
 * This should return a JobFrequency constant indicating how often you want the job to run
* execute
 * This does the work
 * It should _not_ return False if it fails, instead it should return False _only if it cannot send email_.  If this function returns false, checker assumes it cannot send mail. 

An appropriate way to end the function would be:

    if not success:
        return self.sendEmail("Failed executing bob-job", failureMessage)
    else:
        return True


### Inherit JobSpawner

JobSpawner should be used when you want to run the same logic for multiple servers. Look at HTTPServerChecker and TCPServerChecker for examples of how one can use it.

# Install

### Edit the config file

1. Copy settings.cfg.example to settings.cfg
1. Fill in servername and alertcontact
1. Give it the email account details it should send mail from.  I create a specific gmail account for this. 
 1. If you don't create the 'auto-delete messages from me' filter, set that setting to False
1. If you have no peers, comment out all the lines. If you have peers, add them in.  
 1. If you want a peer, I'll give it a shot. Email me

### Cron Entries

Checker relies on the system cron to run at every interval. You need one cron job line for each frequency that is defined in JobFrequency.

First edit the ... to your path, then enter the following into your cron

    * * * * * .../checker/main.py -m cron -c minute >/dev/null 2>&1
    0 * * * * .../checker/main.py -m cron -c hour   >/dev/null 2>&1
    0 0 * * * .../checker/main.py -m cron -c day    >/dev/null 2>&1
    0 0 12 * * .../checker/main.py -m cron -c day_noon >/dev/null 2>&1
  
# TODO

* Implement throttling logic so if a job fails, you don't get an email every single time it fails. Instead get one email when it starts failing and then one email when it's back up. (And let this be customizable.)
* Make JobBase.execute more intuitive for job authors. Remove the "return if the mail sent successfully" requirement.
