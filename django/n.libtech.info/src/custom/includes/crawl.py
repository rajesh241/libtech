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

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,Village,Jobcard,Worker,Wagelist,PanchayatStat,FTO,PaymentInfo,APWorkPayment,CrawlQueue,JobcardStat,CrawlState,DownloadManager
from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,getCurrentFinYear,savePanchayatReport,correctDateFormat,getjcNumber,getVilCode,getEncodedData,getCenterAlignedHeading,getTelanganaDate,table2csv,dateStringToDateObject,Report,datetimeDifference
musterregex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)

def NICStats(logger,objID,finyear=None):
  eachPanchayat=Panchayat.objects.filter(id=objID).first()
  error=downloadPanchayatStat(logger,eachPanchayat)
  if error is None:
    processPanchayatStat(logger,eachPanchayat)
    isComplete=True
  else:
    isComplete=False
  return isComplete

def validateStatsHTML(myhtml):
  error=None
  statsTable=None
  htmlsoup=BeautifulSoup(myhtml,"html.parser")
  tables=htmlsoup.findAll('table')
  for table in tables:
    if "Persondays Generated so far" in str(table):
      statsTable=table
  if statsTable is None:
    error="Stats Table not found"
  return error,statsTable


def downloadPanchayatStat(logger,eachPanchayat):
  reportType="nicStatsHTML"
  finyear=getCurrentFinYear()
  statusURL="%s?panchayat_code=%s&panchayat_name=%s&block_code=%s&block_name=%s&district_code=%s&district_name=%s&state_code=%s&state_name=%s&page=p&fin_year=2014-2015" % (statsURL,eachPanchayat.code,eachPanchayat.name,eachPanchayat.block.code,eachPanchayat.block.name,eachPanchayat.block.district.code,eachPanchayat.block.district.name,eachPanchayat.block.district.state.code,eachPanchayat.block.district.state.name)
  logger.debug(statusURL) 
 
  try:
    r  = requests.get(statusURL)
    error=None
  except requests.exceptions.RequestException as e:  # This is the correct syntax
    logger.debug(e) 
    error=1
  if error is None:
    myhtml=r.text
    error,statsTable=validateStatsHTML(myhtml)
    if error is None:
      logger.debug("Successfully Downloaded")
      outhtml=''
      outhtml+=stripTableAttributes(statsTable,"statsTable")
      title="NIC Panchayat Statistics state:%s District:%s block:%s panchayat: %s  " % (eachPanchayat.block.district.state.name,eachPanchayat.block.district.name,eachPanchayat.block.name,eachPanchayat.name)
      outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
      try:
        outhtml=outhtml.encode("UTF-8")
      except:
        outhtml=outhtml
      filename="nicStats_%s_%s_%s.html" % (eachPanchayat.slug,eachPanchayat.code,finyear)
      savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
  eachPanchayat.statsCrawlDate=timezone.now()
  eachPanchayat.save()
  return error

def processPanchayatStat(logger,eachPanchayat):
  reportType="nicStatsHTML"
  curfinyear=getCurrentFinYear()
  logger.debug(eachPanchayat.name+","+eachPanchayat.code)
  panchayatReport=Report.objects.filter(reportType=reportType,finyear=curfinyear,panchayat=eachPanchayat).first()
  statFound=0
  if panchayatReport is not None:
    logger.debug("Panchayat Report Exists")
    myhtml=panchayatReport.reportFile.read()  
    #myhtml=eachPanchayat.jobcardRegisterFile.read()
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    rows=htmlsoup.findAll("tr")
    nicTotalApplicants=None
    nicTotalJobcards=None
    for row in rows:
      if "Total No. of Workers" in str(row):
        cols=row.findAll("td")
        wArray=[]
        for col in cols:
          wArray.append(col.text.lstrip().rstrip().replace(",",""))
        logger.debug(str(wArray))  
        nicTotalApplicants=wArray[1]
      
      if "Total No. of JobCards issued" in str(row):
        cols=row.findAll("td")
        wArray=[]
        for col in cols:
          wArray.append(col.text.lstrip().rstrip().replace(",",""))
        logger.debug(str(wArray))  
        nicTotalJobcards=wArray[1]
        
      if "II             Progress" in str(row):
        statFound=1
        logger.debug(str(row)) 
        cols=row.findAll("td")
        fArray=[]
        for col in cols:
          fArray.append(col.text.lstrip().rstrip()[-2:])
        logger.debug(str(fArray))  
      if "Persondays Generated so far" in str(row):
        logger.debug(str(row)) 
        cols=row.findAll("td")
        fArrayData=[]
        for col in cols:
          fArrayData.append(col.text.lstrip().rstrip().replace(",",""))
        logger.debug(str(fArrayData))
  
  curfinyear=getCurrentFinYear()
  mypanchayatStat=PanchayatStat.objects.filter(finyear=curfinyear,panchayat=eachPanchayat).first()
  if mypanchayatStat is None:
    PanchayatStat.objects.create(finyear=curfinyear,panchayat=eachPanchayat)
  myStat=PanchayatStat.objects.filter(finyear=curfinyear,panchayat=eachPanchayat).first()
  myStat.nicWorkersTotal=nicTotalApplicants
  myStat.nicJobcardsTotal=nicTotalJobcards 
  myStat.save()
  if statFound == 1:
    for i,finyear in enumerate(fArray):
      if i != 0:
        workDays=fArrayData[i]
        mypanchayatStat=PanchayatStat.objects.filter(finyear=finyear,panchayat=eachPanchayat).first()
        if mypanchayatStat is None:
          PanchayatStat.objects.create(finyear=finyear,panchayat=eachPanchayat)
        myStat=PanchayatStat.objects.filter(finyear=finyear,panchayat=eachPanchayat).first()
        myStat.nicWorkDays=workDays
        myStat.save()


