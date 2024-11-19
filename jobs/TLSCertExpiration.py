#!/usr/bin/env python3

from builtins import str
import ssl
import time
import logging
import http.client
import OpenSSL
import datetime

from . import JobBase
from . import JobSpawner


class TLSCertExpiration(JobSpawner.JobSpawner):
    servers = [
        (
            "ritter.vg:443",
            JobBase.JobFrequency.HOUR,
            JobBase.JobFailureNotificationFrequency.EVERYDAY,
            JobBase.JobFailureCountMinimumBeforeNotification.ONE,
        ),
    ]

    class CertChecker(JobBase.JobBase):
        def __init__(
            self,
            config,
            url,
            frequency,
            failureNotificationFrequency,
            failuresBeforeNotification,
        ):
            self.config = config
            self.url = url
            self.frequency = frequency
            self.failureNotificationFrequency = failureNotificationFrequency
            self.failuresBeforeNotification = failuresBeforeNotification
            super(TLSCertExpiration.CertChecker, self).__init__(config, url)

        def getName(self):
            return str(self.__class__) + " for " + self.url

        def executeEvery(self):
            return self.frequency

        def notifyOnFailureEvery(self):
            return self.failureNotificationFrequency

        def numberFailuresBeforeNotification(self):
            return self.failuresBeforeNotification

        def execute(self):
            try:
                context = ssl._create_unverified_context()
                c = http.client.HTTPSConnection(self.url, context=context)
                c.request("GET", "/")
                asn1 = c.sock.getpeercert(True)
                x509 = OpenSSL.crypto.load_certificate(
                    OpenSSL.crypto.FILETYPE_ASN1, asn1
                )
                na = time.mktime(
                    time.strptime(
                        x509.get_notAfter()[:-1].decode("utf-8"), "%Y%m%d%H%M%S"
                    )
                )
                now = time.time()
                delta = datetime.timedelta(seconds=(na - now))
                if delta < datetime.timedelta(days=30):
                    self.failuremsg = (
                        "Server Certificate for "
                        + self.url
                        + " expires in "
                        + str(delta.days)
                        + " days"
                    )
                    return False
                return True
            except Exception as e:
                self.failuremsg = (
                    "Could not get server certificate " + self.url + "\n" + str(e)
                )
                logging.warn(self.failuremsg)
                logging.warn(logging.traceback.format_exc())
                return False

        def onFailure(self):
            return self.sendEmail(self.failuremsg, "")

        def onStateChangeSuccess(self):
            return self.sendEmail("Successfully hit " + self.url, "")

    def get_sub_jobs(self, config):
        for s in self.servers:
            yield self.CertChecker(config, s[0], s[1], s[2], s[3])
