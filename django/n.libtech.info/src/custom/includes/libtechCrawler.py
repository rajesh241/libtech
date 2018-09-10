
import re
import shutil
import unicodecsv as csv
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
#import csv
from io import BytesIO
from bs4 import BeautifulSoup
from customSettings import repoDir,djangoDir,djangoSettings,telanganaThresholdDate,telanganaJobcardTimeThreshold,searchIP,wagelistTimeThreshold,musterTimeThreshold,apStateCode,crawlRetryThreshold,nregaPortalMinHour,nregaPortalMaxHour,wagelistGenerationThresholdDays,crawlerTimeThreshold,telanganaStateCode
from reportFunctions import createExtendedPPReport,createExtendedRPReport,createWorkPaymentReportAP
import sys
import time
import os
from queue import Queue
from threading import Thread
import threading
import requests
import time
import crawlFunctions
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

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,Village,Jobcard,Worker,Wagelist,PanchayatStat,FTO,PaymentInfo,APWorkPayment,CrawlQueue,JobcardStat,CrawlState
from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,getCurrentFinYear,savePanchayatReport,correctDateFormat,getjcNumber,getVilCode,getEncodedData,getCenterAlignedHeading,getTelanganaDate,table2csv,dateStringToDateObject,Report,datetimeDifference


def getNumberProcesses(q,isPanchayatLevelProcess):
  if isPanchayatLevelProcess == True:
    n=1
  else:
    if q < 10:
      n=1
    elif q < 100:
      n=10
    elif q< 500:
      n=40
    elif q< 1000:
      n=80
    else:
      n=90
  return n


def getNextCrawlState(logger,crawlState,isNIC,isAP,isTelangana):
  nextSequence=crawlState.sequence+1
  if isNIC==True:
    nextCrawlState=CrawlState.objects.filter(sequence=nextSequence,crawlType="NIC").first()
  elif isAP==True: 
    nextCrawlState=CrawlState.objects.filter(sequence=nextSequence,crawlType="AP").first()
  elif isTelangana==True:
    nextCrawlState=CrawlState.objects.filter(sequence=nextSequence,crawlType="Telangana").first()
  else:
    nextCrawlState=None
  return nextCrawlState

def getCrawlQueueStateCode(logger,eachCrawlQueue):
  if eachCrawlQueue.block is not None:
    stateCode=eachCrawlQueue.block.district.state.code
  else:
    stateCode=eachCrawlQueue.panchayat.block.district.state.code
  return stateCode

def getCrawlQueueIsNIC(logger,eachCrawlQueue):
  if eachCrawlQueue.block is not None:
    isNIC=eachCrawlQueue.block.district.state.isNIC
  else:
    isNIC=eachCrawlQueue.panchayat.block.district.state.isNIC
  return isNIC

def getCrawlObjs(logger,crawlStateName,finyear=None,eachBlock=None,eachPanchayat=None,isPanchayatLevelProcess=None):
  myobjs=None
  if isPanchayatLevelProcess == True:
    if eachBlock is not None:
      myobjs=Panchayat.objects.filter(block=eachBlock)
    else:
      myobjs=Panchayat.objects.filter(id=eachPanchayat.id)


  if crawlStateName=="computeJobcardStat": 
    if eachBlock is not None:
      myobjs=Jobcard.objects.filter(panchayat__block=eachBlock)
    else:
      myobjs=Jobcard.objects.filter(panchayat=eachPanchayat)

  if crawlStateName== "ftoProcess":
    if eachBlock is not None:
      myobjs=FTO.objects.filter( Q (block=eachBlock) & Q ( Q( downloadManager__isDownloaded=True,downloadManager__isProcessed=False) | Q (downloadManager__downloadAttemptCount__gte = 10  ) ))
    else:
      myobjs=FTO.objects.filter( Q (block=eachPanchayat.block) & Q ( Q( downloadManager__isDownloaded=True,downloadManager__isProcessed=False) | Q (downloadManager__downloadAttemptCount__gte = 10  ) ))

  if crawlStateName == "ftoDownload":
    if eachBlock is not None:
      myobjs=FTO.objects.filter( Q (isComplete=False,block=eachBlock,downloadManager__downloadAttemptCount__lte=10) & Q ( Q( downloadManager__isDownloaded=False) | Q (downloadManager__downloadDate__lt = crawlerTimeThreshold)  ) )
    else:
      myobjs=FTO.objects.filter( Q (isComplete=False,block=eachPanchayat.block,downloadManager__downloadAttemptCount__lte=10) & Q ( Q( downloadManager__isDownloaded=False) | Q (downloadManager__downloadDate__lt = crawlerTimeThreshold)  ) )

  if crawlStateName == "wagelistDownload":
    if eachBlock is not None:
      myobjs=Wagelist.objects.filter( Q (isComplete=False,block=eachBlock,downloadManager__downloadAttemptCount__lte=10) & Q ( Q( downloadManager__isDownloaded=False) | Q (downloadManager__downloadDate__lt = crawlerTimeThreshold)  ) )
    else:
      myobjs=Wagelist.objects.filter( Q (isComplete=False,block=eachPanchayat.block,downloadManager__downloadAttemptCount__lte=10) & Q ( Q( downloadManager__isDownloaded=False) | Q (downloadManager__downloadDate__lt = crawlerTimeThreshold)  ) )

  if crawlStateName== "wagelistProcess":
    if eachBlock is not None:
      myobjs=Wagelist.objects.filter( Q (block=eachBlock) & Q ( Q( downloadManager__isDownloaded=True,downloadManager__isProcessed=False) | Q (downloadManager__downloadAttemptCount__gte = 10  ) ))
    else:
      myobjs=Wagelist.objects.filter( Q (block=eachPanchayat.block) & Q ( Q( downloadManager__isDownloaded=True,downloadManager__isProcessed=False) | Q (downloadManager__downloadAttemptCount__gte = 10  ) ))

  if crawlStateName== "musterProcess":
    if eachBlock is not None:
      myobjs=Muster.objects.filter( Q (panchayat__block=eachBlock) & Q ( Q( downloadManager__isDownloaded=True,downloadManager__isProcessed=False) | Q (downloadManager__downloadAttemptCount__gte = 10  ) ))
    else:
      myobjs=Muster.objects.filter( Q (panchayat=eachPanchayat) & Q ( Q( downloadManager__isDownloaded=True,downloadManager__isProcessed=False) | Q (downloadManager__downloadAttemptCount__gte = 10  ) ))

  if crawlStateName == "musterDownload":
    if eachBlock is not None:
      myobjs=Muster.objects.filter( Q (isComplete=False,panchayat__block=eachBlock,downloadManager__downloadAttemptCount__lte=10) & Q ( Q( downloadManager__isDownloaded=False) | Q (downloadManager__downloadDate__lt = crawlerTimeThreshold)  ) )
    else:
      myobjs=Muster.objects.filter( Q (isComplete=False,panchayat=eachPanchayat,downloadManager__downloadAttemptCount__lte=10) & Q ( Q( downloadManager__isDownloaded=False) | Q (downloadManager__downloadDate__lt = crawlerTimeThreshold)  ) )

  if crawlStateName == "apJobcardProcess":
    if eachBlock is not None:
      myobjs=Jobcard.objects.filter( Q (tjobcard__isnull=False,panchayat__block=eachBlock) & Q ( Q( downloadManager__isDownloaded=True,downloadManager__isProcessed=False) | Q (downloadManager__downloadAttemptCount__gte = 10  ) ))
    else:
      myobjs=Jobcard.objects.filter( Q (tjobcard__isnull=False,panchayat=eachPanchayat) & Q ( Q( downloadManager__isDownloaded=True,downloadManager__isProcessed=False) | Q (downloadManager__downloadAttemptCount__gte = 10  ) ))

  if ( (crawlStateName == "apJobcardDownload") or (crawlStateName == "telanganaJobcardDownload")):
    if eachBlock is not None:
      myobjs=Jobcard.objects.filter( Q (tjobcard__isnull=False,panchayat__block=eachBlock,downloadManager__downloadAttemptCount__lte=10) & Q ( Q( downloadManager__isDownloaded=False) | Q (downloadManager__downloadDate__lt = crawlerTimeThreshold)  ) )
    else:
      myobjs=Jobcard.objects.filter( Q (tjobcard__isnull=False,panchayat=eachPanchayat,downloadManager__downloadAttemptCount__lte=10) & Q ( Q( downloadManager__isDownloaded=False) | Q (downloadManager__downloadDate__lt = crawlerTimeThreshold)  ) )
  return myobjs

def libtechQueueManager(logger,myobjs,nicHourRestriction,modelName,isPanchayatLevelProcess,startFinYear):
  if len(myobjs) > 0:
    n=getNumberProcesses(len(myobjs),isPanchayatLevelProcess)
    queueSize=n+len(myobjs)+10
    q = Queue(maxsize=queueSize)
    logger.info("Queue Size %s Numbe of Threads %s " % (str(queueSize),str(n)))
    for obj in myobjs:
      q.put(obj.id)
      obj.downloadAttemptDate=timezone.now()
      obj.save()

    for i in range(n):
      logger.debug("Starting worker Thread %s " % str(i))
      t = Thread(name = 'Thread-' + str(i), target=libtechQueueWorker, args=(logger,nicHourRestriction,q,modelName,startFinYear,isPanchayatLevelProcess ))
      t.daemon = True  
      t.start()


    q.join()       # block until all tasks are done
    for i in range(n):
      q.put(None)
     
def libtechQueueWorker(logger,nicHourRestriction,q,modelName,startFinYear,isPanchayatLevelProcess):
  while True:
    now=datetime.datetime.now()
    curhour=now.hour
    isComputeModel=False
    if (nicHourRestriction == False) or ( (curhour >= 6) and (curhour < 21) ): 
      objID = q.get()  # if there is no url, this will wait
      if objID is None:
        break
      name = threading.currentThread().getName()
      logger.debug("%s  QueueSize: %s Thread : %s objID: %s " % (modelName,str(q.qsize()),name,str(objID)))
      if isPanchayatLevelProcess == True:
        logger.debug("Panchayat Level Crawl is True")
        getattr(crawlFunctions,modelName)(logger,objID,startFinYear=startFinYear)
      else:
        getattr(crawlFunctions,modelName)(logger,objID)
      logger.debug("cur hour is %s" % str(curhour))
      q.task_done()
    else:
      time.sleep(10)
      logger.debug("Task is not Done, This is outside of Nrega Working Hours")


def libtechCrawler(logger,crawlState,finyear=None,qid=None,limit=None,forceRun=False,downloadLimit=None):
  logger.debug("Initiating Libtech Crawler witht crawlState %s " % (crawlState.name))
  if limit is None:
    limit=1
  if qid is  None:
    myQueueObjects=CrawlQueue.objects.filter(Q ( Q(crawlState=crawlState) & Q( Q(stepError=True,crawlAttemptDate__lt=crawlRetryThreshold) | Q(stepError=False) )) ).order_by("-priority","crawlAttemptDate","created")[:limit]
  else:
    myQueueObjects=CrawlQueue.objects.filter(id=qid)

  for eachCrawlQueue in myQueueObjects:
    #First we need to set up the variables which affect the states of the crawl Queue
    logger.info(eachCrawlQueue)
    isBlockCrawl=False
    if eachCrawlQueue.block is not None:
      isBlockCrawl=True
    isNIC=getCrawlQueueIsNIC(logger,eachCrawlQueue)
    stateCode=getCrawlQueueStateCode(logger,eachCrawlQueue)
    isAP=False
    if stateCode==apStateCode:
      isAP=True
    isTelangana=False
    if stateCode==telanganaStateCode:
      isTelangana=True
    if isBlockCrawl==True:
      myPanchayats=Panchayat.objects.filter(block=eachCrawlQueue.block)
    else:
      myPanchayats=Panchayat.objects.filter(code=eachCrawlQueue.panchayat.code)
    #Setting up StepError is True would set it to False at teh end of execution step 
    logger.debug("IsNIC is %s isAP is %s " % (str(isNIC),str(isAP)))
    eachCrawlQueue.stepError=True
    eachCrawlQueue.crawlAttemptDate=timezone.now()
    eachCrawlQueue.save()
    stepInProgress=False # if any of hte steps is in progress we will set it to True below.
    stepError=True

    #CrawlState Machine
    crawlStateName=crawlState.name
    crawlType=crawlState.crawlType
    needsQueueManager=crawlState.needsQueueManager
    nicHourRestriction=crawlState.nicHourRestriction
    isPanchayatLevelProcess=crawlState.isPanchayatLevelProcess
    iterateFinYear=crawlState.iterateFinYear
    if downloadLimit is None:
      objLimit=crawlState.objLimit
    else:
      objLimit=downloadLimit
    if iterateFinYear == False:
      startFinYear=getCurrentFinYear()
    else:
      startFinYear=eachCrawlQueue.startFinYear
    endFinYear=getCurrentFinYear()
    logger.info("Current CrawlState is %s " % crawlStateName)
    
    #Calling the function which will do the work
    if needsQueueManager==False:
      pending=1
      eachCrawlQueue.pending=pending
      eachCrawlQueue.save()
      stepError=False
      for eachPanchayat in myPanchayats:
        for finyear in range(int(startFinYear),int(endFinYear)+1):
          error = getattr(crawlFunctions,crawlStateName)(logger,eachPanchayat=eachPanchayat,finyear=finyear)
          if error==True:
            stepError=True
    else:
      
#      for finyear in range(int(startFinYear),int(endFinYear)+1):
      myobjs=getCrawlObjs(logger,crawlStateName,finyear=None,eachBlock=eachCrawlQueue.block,eachPanchayat=eachCrawlQueue.panchayat,isPanchayatLevelProcess=isPanchayatLevelProcess)
      logger.info("Going to process %s of total %s " % (str(objLimit),str(len(myobjs))))
      pending=len(myobjs)
      eachCrawlQueue.pending=pending
      eachCrawlQueue.save()
      if len(myobjs) > 0:
        libtechQueueManager(logger,myobjs[:objLimit],nicHourRestriction,crawlStateName,isPanchayatLevelProcess,startFinYear)
      if len(myobjs) > objLimit:
        stepInProgress=True
      stepError=False


    nextCrawlState=getNextCrawlState(logger,crawlState,isNIC,isAP,isTelangana)


    eachCrawlQueue.stepError=stepError
    if (stepError == False) and (stepInProgress == False):
      eachCrawlQueue.crawlState=nextCrawlState
      logger.info("Going to set up next satte")
      logger.info(eachCrawlQueue)
      eachCrawlQueue.save()
