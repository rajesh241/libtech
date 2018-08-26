
import re
import shutil
import unicodecsv as csv
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
#import csv
from io import BytesIO
from bs4 import BeautifulSoup
from customSettings import repoDir,djangoDir,djangoSettings,telanganaThresholdDate,telanganaJobcardTimeThreshold,searchIP,wagelistTimeThreshold,musterTimeThreshold
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
from django.db.models import F,Q,Count,Sum
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,Village,Jobcard,Worker,Wagelist,PanchayatStat,FTO,PaymentInfo,APWorkPayment
from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,getCurrentFinYear,saveBlockReport,savePanchayatReport,correctDateFormat,getjcNumber,getVilCode,getEncodedData,getCenterAlignedHeading,getTelanganaDate,table2csv

musterregex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
statsURL="http://mnregaweb4.nic.in/netnrega/all_lvl_details_new.aspx"

def createJobcardReport(logger,eachPanchayat,finyear,eachBlock=None):
  f = BytesIO()
  f.write(u'\ufeff'.encode('utf8'))
  w = csv.writer(f, encoding='utf-8-sig',delimiter=',')
  reportType="jobcardcsv"
  a=[]
  a.extend(["panchayat","village","jobcard","names","caste","daysWorked19",'payOrderAmount19','disbursedAmount19','pendingAmount19','daysWorked18','payOrderAmount18','disbursedAmount18','pendingAmount18'])
  w.writerow(a)
  if eachBlock is not None:
    jobcards=Jobcard.objects.filter(panchayat__block=eachBlock)
  else:
    jobcards=Jobcard.objects.filter(panchayat=eachPanchayat)
  logger.info("Total Jobcards %s" % str(len(jobcards)))
  for eachJobcard in jobcards:
    if eachJobcard.tjobcard is not None:
      jobcard="~"+eachJobcard.tjobcard
    else:
      jobcard=eachJobcard.jobcard
    workerString=''
    if eachJobcard.village is not None:
      village=eachJobcard.village.name
    else:
      village=''
    caste=eachJobcard.caste
    if eachJobcard.panchayat.block.district.state.code == apStateCode:
      myDaysWorked=APWorkPayment.objects.filter(jobcard=eachJobcard).values("finyear").annotate(dsum=Sum('daysWorked'),psum=Sum('payorderAmount'),csum=Sum('disbursedAmount'))
    else:
      myDaysWorked=WorkPayment.objects.filter(jobcard=eachJobcard).values("finyear").annotate(dsum=Sum('daysWorked'),psum=Sum('totalWage'),csum=Sum('disbursedAmount'))
    daysWorked19=0
    payOrderAmount19=0
    creditedAmount19=0
    pendingAmount19=0
    daysWorked18=0
    payOrderAmount18=0
    creditedAmount18=0
    pendingAmount18=0
    for obj in myDaysWorked:
      if obj['finyear'] == '19':
        daysWorked19=obj['dsum']
        payOrderAmount19=obj['psum']
        creditedAmount19=obj['csum']
        pendingAmount19=payOrderAmount19-creditedAmount19
      if obj['finyear'] == '18':
        daysWorked18=obj['dsum']
        payOrderAmount18=obj['psum']
        creditedAmount18=obj['csum']
        pendingAmount18=payOrderAmount18-creditedAmount18
#myWorkDetails=WorkDetail.objects.filter(worker__jobcard__panchayat__block__id=2639,musterStatus='Rejected').values("worker__jobcard__panchayat__block__id","muster__finyear").annotate(dcount=Count('pk'),tcount=Sum('totalWage'))
    workers=Worker.objects.filter(jobcard=eachJobcard)
    for eachWorker in workers:
      workerString+=eachWorker.name
      workerString+="|"
    a=[]
    a.extend([eachPanchayat.name,village,jobcard,workerString,caste,daysWorked19,payOrderAmount19,creditedAmount19,pendingAmount19,daysWorked18,payOrderAmount18,creditedAmount18,pendingAmount18])
    w.writerow(a)
  f.seek(0)
  outcsv=f.getvalue()
  if eachBlock is not None:
    csvfilename=eachBlock.slug+"_"+finyear+"_jobcards.csv"
    saveBlockReport(logger,eachBlock,finyear,reportType,csvfilename,outcsv)
  else:
    csvfilename=eachPanchayat.slug+"_"+finyear+"_jobcards.csv"
    savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)


