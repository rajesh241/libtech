import re
import shutil
import unicodecsv as csv
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
#import csv
from io import BytesIO
from bs4 import BeautifulSoup
from customSettings import repoDir,djangoDir,djangoSettings,telanganaThresholdDate,telanganaJobcardTimeThreshold,searchIP,wagelistTimeThreshold,musterTimeThreshold,apStateCode,crawlRetryThreshold,nregaPortalMinHour,nregaPortalMaxHour,wagelistGenerationThresholdDays,crawlerTimeThreshold,statsURL
from reportFunctions import createExtendedPPReport,createExtendedRPReport,createWorkPaymentReportAP
import sys
import time
import os
from queue import Queue
from threading import Thread
import threading
import requests
import time
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from wrappers.logger import loggerFetch
import datetime
import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q,Sum
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,Village,Jobcard,Worker,Wagelist,PanchayatStat,FTO,PaymentInfo,APWorkPayment,CrawlQueue,JobcardStat,CrawlState,DownloadManager,Task
from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,getCurrentFinYear,savePanchayatReport,correctDateFormat,getjcNumber,getVilCode,getEncodedData,getCenterAlignedHeading,getTelanganaDate,table2csv,dateStringToDateObject,Report,datetimeDifference
musterregex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)


def test(logger,objID,finyear=None):
  logger.debug("using importlib Test Function %s" % (str(objID)))
  time.sleep(10)
  return True
