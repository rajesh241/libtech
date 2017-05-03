from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
import threading
from datetime import datetime,date,timedelta
import requests
import os
import sys
import re
import time
from customSettings import repoDir,djangoDir,djangoSettings
from customSettings import musterTimeThreshold
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone


os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster

maxMusterDownloadQueue=200
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing Jobcards')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-n', '--numberOfThreads', help='Number of Threads default 5', required=False)
  parser.add_argument('-q', '--queueSize', help='Number of Musters in Queue default 200', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args

def validateMusterHTML(muster,myhtml):
  error=None
  musterTable=None
  musterSummaryTable=None
  jobcardPrefix=muster.block.district.state.stateShortCode+"-"
  if (jobcardPrefix in myhtml):
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if muster.workCode in str(table):
        musterSummaryTable=table
    if musterSummaryTable is None:
      error="Muster Summary Table not found"
    musterTable=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
    if musterTable is None:
      error="Muster Table not found"
  else:
    error="Jobcard Prefix not found"
  return error,musterTable,musterSummaryTable

def musterQueueManager(logger,q,queueSize,stateCode):
  addLimit=queueSize-50
  while True:
    if(q.qsize() < 50):
      if stateCode is not None:
        myMusters=Muster.objects.filter( Q(isDownloaded=False,isRequired=1,block__district__state__code=stateCode) | Q(musterDownloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isRequired=1,isProcessed=1,block__district__state__code=stateCode) ).order_by("musterDownloadAttemptDate")[:addLimit]
      else:
        myMusters=Muster.objects.filter( Q(isDownloaded=False,isRequired=1) | Q(musterDownloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isRequired=1,isProcessed=1) ).order_by("musterDownloadAttemptDate")[:addLimit]
      musterIDs=''
      logger.info("This is where I am")
      logger.info("Lenght of myMusters is "+str(len(myMusters)))
      if len(myMusters) > 0:
        for eachMuster in myMusters:
      #    print("Added muster ID : %s " % str(eachMuster.id))
          musterIDs+=str(eachMuster.id)+"-"
          q.put(eachMuster.id)
          eachMuster.musterDownloadAttemptDate=timezone.now()
          eachMuster.save()
        logger.info("Added Musters: %s " % musterIDs)
    else:
      logger.info("Queu is not empty")
    time.sleep(60)
        
def musterDownloadWorker(logger,q,inputargs,driver,display):
  time.sleep(20)
  while True:
    musterID = q.get()  # if there is no url, this will wait
    name = threading.currentThread().getName()
 #   print("Thread: {0} start download {1} at time = {2} \n".format(name, str(musterID), time.strftime('%H:%M:%S')))

    eachMuster=Muster.objects.filter(id=musterID).first()
#    logger.info(eachMuster.musterURL)  
    logger.info("Processing name: %s musterID: %s musterNo: %s FullblockCode: %s " % (name,str(eachMuster.id),eachMuster.musterNo,eachMuster.block.code))
#     musterURL="http://%s/netnrega/citizen_html/musternew.aspx?state_name=%s&district_name=%s&block_name=%s&panchayat_name=%s&workcode=%s&panchayat_code=%s&msrno=%s&finyear=%s&dtfrm=%s&dtto=%s&wn=%s&id=1" % (eachMuster.block.district.state.crawlIP,eachMuster.block.district.state.name,eachMuster.block.district.name,eachMuster.block.name,eachMuster.panchayat.name,eachMuster.workCode,eachMuster.panchayat.fullPanchayatCode,eachMuster.musterNo,fullfinyear,datefromstring,datetostring,eachMuster.workName.replace(" ","+"))
    driver.get(eachMuster.musterURL)
    driver.get(eachMuster.musterURL)
    logger.info(eachMuster.musterURL)
    myhtml = driver.page_source
  #  f=open("/tmp/"+str(eachMuster.id)+".html","w")
  #  f.write(myhtml)
    error,musterTable,musterSummaryTable=validateMusterHTML(eachMuster,myhtml)
    logger.info(error)
    if error is None:  
      outhtml=''
      outhtml+=stripTableAttributes(musterSummaryTable,"musterSummary")
      outhtml+=stripTableAttributes(musterTable,"musterDetails")
      title="Muster: %s state:%s District:%s block:%s finyear:%s " % (eachMuster.musterNo,eachMuster.block.district.state.name,eachMuster.block.district.name,eachMuster.block.name,getFullFinYear(eachMuster.finyear))
#      logger.info(title) 
      outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
      try:
        outhtml=outhtml.encode("UTF-8")
      except:
        outhtml=outhtml
      filename="%s.html" % (eachMuster.musterNo)
      eachMuster.musterFile.save(filename, ContentFile(outhtml))
      eachMuster.musterDownloadAttemptDate=timezone.now()
      eachMuster.isDownloaded=True
      eachMuster.isProcessed=False
      eachMuster.save()
    else:
  #    logger.info("Muster Download Erorr: %s " % (error))
      eachMuster.musterDownloadAttemptDate=timezone.now()
      eachMuster.downloadError=error
      eachMuster.save()

    q.task_done()
 
 
 

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  stateCode=args['stateCode']
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  if ((args['queueSize']) and ( int(args['queueSize']) > 200)):
    queueSize=int(args['queueSize'])
  else:
    queueSize=200
  if args['numberOfThreads']:
    numberOfThreads=int(args['numberOfThreads'])
  else:
    numberOfThreads=5
  logger.info("Starting Muster Download Script with Queue Size: %s and Number of Threads: %s " % (queueSize,numberOfThreads))
  q = Queue(maxsize=queueSize)

  t1 = Thread(name = 'musterQueueManager', target=musterQueueManager, args=(logger,q,queueSize,stateCode ))
  t1.daemon = True
  t1.start()


  #Starting Crawler Threads
  driverArray=[]
  displayArray=[]
  for i in range(numberOfThreads):
    logger.info("Starting worker Thread %s " % str(i))
    
    display = displayInitialize(args['visible'])
    driver = driverInitialize(args['browser'])
    driverArray.append(driver)
    displayArray.append(display)
    t = Thread(name = 'Thread-' + str(i), target=musterDownloadWorker, args=(logger,q,args,driver,display ))
    t.daemon = True
    t.start()

  time.sleep(120) 
  q.join()       # block until all tasks are done
  for driver in driverArray:
    driverFinalize(driver)
  for display in displayArray:
    displayFinalize(display)

  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
