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
import re
regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
regex1=re.compile(r'</td></font></td>',re.DOTALL)
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

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag

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
  parser.add_argument('-p', '--panchayatCode', help='StateCode for which the numbster needs to be downloaded', required=False)
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
def populateMusterQueue(logger,q,queueSize,stateCode,panchayatCode,addLimit):
  alwaysTag=LibtechTag.objects.filter(name="Always")
  if panchayatCode is not None:
    myMusters=Muster.objects.filter( Q(isDownloaded=False,panchayat__isnull=False,panchayat__code=panchayatCode,panchayat__crawlRequirement="FULL") | Q(musterDownloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isProcessed=1,panchayat__isnull=False,panchayat__code=panchayatCode,panchayat__crawlRequirement="FULL") ).order_by("panchayat__block__district__state__code","downloadAttemptCount","-finyear")[:addLimit]
  elif stateCode is not None:
    myMusters=Muster.objects.filter( Q(isDownloaded=False,panchayat__isnull=False,panchayat__block__district__state__code=stateCode,panchayat__crawlRequirement="FULL") | Q(musterDownloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isProcessed=1,panchayat__isnull=False,panchayat__block__district__state__code=stateCode,panchayat__crawlRequirement="FULL") ).order_by("panchayat__block__district__state__code","downloadAttemptCount","-finyear")[:addLimit]
    #myMusters=Muster.objects.filter( Q(isDownloaded=False,isRequired=1,block__district__state__code=stateCode) | Q(musterDownloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isRequired=1,isProcessed=1,block__district__state__code=stateCode) ).order_by("musterDownloadAttemptDate")[:addLimit]
  else:
    myMusters=Muster.objects.filter( Q(isDownloaded=False,panchayat__isnull=False,panchayat__crawlRequirement="FULL",panchayat__libtechTag__in=alwaysTag) | Q(musterDownloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isProcessed=1,panchayat__isnull=False,panchayat__crawlRequirement="FULL",panchayat__libtechTag__in=alwaysTag) ).order_by("panchayat__block__district__state__code","downloadAttemptCount")[:addLimit]
  musterIDs=''
  logger.info("Lenght of myMusters is "+str(len(myMusters)))
  if len(myMusters) > 0:
    for eachMuster in myMusters:
  #    print("Added muster ID : %s " % str(eachMuster.id))
      musterIDs+=str(eachMuster.id)+"-"
      q.put(eachMuster.id)
      eachMuster.musterDownloadAttemptDate=timezone.now()
      eachMuster.save()
    logger.info("Added Musters: %s " % musterIDs)
def musterQueueManager(logger,q,queueSize,stateCode):
  addLimit=queueSize-1100
  addLimit=1
  while True:
    if(q.qsize() < 1000):
      populateMusterQueue(logger,q,queueSize,stateCode,addLimit)
    else:
      logger.info("Queu is not empty")
    time.sleep(600)
       
def getMuster(logger,eachMuster):
  url = 'http://%s/netnrega/citizen_html/musternew.aspx' % (eachMuster.panchayat.block.district.state.crawlIP)
  logger.info("Printing Muster URl %s" % url)
  headers = {
      'Accept-Encoding': 'gzip, deflate',
      'Accept-Language': 'en-US,en;q=0.8',
      'Upgrade-Insecure-Requests': '1',
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36 Vivaldi/1.91.867.42',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
  }
  stateName=eachMuster.panchayat.block.district.state.name
  districtName=eachMuster.panchayat.block.district.name
  blockName=eachMuster.panchayat.block.name
  panchayatName=eachMuster.panchayat.name
  workCode=eachMuster.workCode
  workName=eachMuster.workName
  panchayatCode=eachMuster.panchayat.code
  musterNo=eachMuster.musterNo
  fullfinyear=getFullFinYear(eachMuster.finyear)
  logger.info(stateName+districtName+fullfinyear)
  dateArray=str(eachMuster.dateFrom).split("-")
  dateFrom="%s/%s/%s" % (dateArray[2],dateArray[1],dateArray[0])
  dateArray=str(eachMuster.dateTo).split("-")
  dateTo="%s/%s/%s" % (dateArray[2],dateArray[1],dateArray[0])

  params = (
      ('state_name', stateName),
      ('district_name', districtName),
      ('block_name', blockName),
      ('panchayat_name', panchayatName),
      ('workcode', workCode),
      ('panchayat_code', panchayatCode),
      ('msrno', musterNo),
      ('finyear', fullfinyear),
      ('dtfrm', dateFrom),
      ('dtto', dateTo),
      ('wn', workName),
      ('id', '1'),
  )

  response = requests.get(url, headers=headers, params=params)
  cookies = response.cookies
  logger.info(cookies)
      
  response = requests.get(url, headers=headers, params=params, cookies=cookies)
  logger.info(response.cookies)
#  logger.info(response)
# filename="/tmp/%s.html" % (musterNo) 
# with open(filename, 'wb') as html_file:
#     logger.info('Writing [%s]' % filename)
#     html_file.write(response.text.encode('utf-8'))

  return response.text


def musterDownloadWorker(logger,q,inputargs,driver,display):
  while True:
    musterID = q.get()  # if there is no url, this will wait
    if musterID is None:
      break
    name = threading.currentThread().getName()

    eachMuster=Muster.objects.filter(id=musterID).first()
#    logger.info(eachMuster.musterURL)  
    try:
      myhtml=getMuster(logger,eachMuster)
      myhtml=myhtml.replace("</td></td>","</td>")
  #    myhtml=re.sub(regex,"",myhtml)
  #    myhtml=re.sub(regex1,"</font></td>",myhtml)
     
    #  driver.get(eachMuster.musterURL)
    #  driver.get(eachMuster.musterURL)
    #  myhtml = driver.page_source
      error,musterTable,musterSummaryTable=validateMusterHTML(eachMuster,myhtml)
      #logger.info(musterTable)
    except:
      error="downloadError"
  
  #  f=open("/tmp/"+str(eachMuster.id)+".html","w")
  #  f.write(myhtml)
    if error is None:
      errorString="No ERROR"
    else:
      errorString=error

    logger.info("Processing name: %s musterID: %s musterNo: %s FullblockCode: %s status: %s" % (name,str(eachMuster.id),eachMuster.musterNo,eachMuster.block.code,errorString))
    logger.info(eachMuster.musterURL)

    if error is None:  
      outhtml=''
      outhtml+=stripTableAttributes(musterSummaryTable,"musterSummary")
      #strippedTable=stripTableAttributes(musterTable,"musterDetails")
      #logger.info(strippedTable)
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
      eachMuster.downloadAttemptCount=eachMuster.downloadAttemptCount+1
      eachMuster.downloadCount=eachMuster.downloadCount+1
      eachMuster.isDownloaded=True
      eachMuster.isProcessed=False
      eachMuster.save()
    else:
  #    logger.info("Muster Download Erorr: %s " % (error))
      eachMuster.musterDownloadAttemptDate=timezone.now()
      eachMuster.downloadAttemptCount=eachMuster.downloadAttemptCount+1
      eachMuster.downloadError=error
      eachMuster.save()

    q.task_done()
 
 
 

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  stateCode=args['stateCode']
  panchayatCode=args['panchayatCode']
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  #if ((args['queueSize']) and ( int(args['queueSize']) > 200)):
  if args['queueSize']:
    queueSize=int(args['queueSize'])
  else:
    queueSize=20
  if args['numberOfThreads']:
    numberOfThreads=int(args['numberOfThreads'])
  else:
    numberOfThreads=5
  logger.info("Starting Muster Download Script with Queue Size: %s and Number of Threads: %s " % (queueSize,numberOfThreads))
  q = Queue(maxsize=queueSize)
  addLimit=queueSize
  populateMusterQueue(logger,q,queueSize,stateCode,panchayatCode,addLimit)
  #t1 = Thread(name = 'musterQueueManager', target=musterQueueManager, args=(logger,q,queueSize,stateCode ))
#  t1 = Thread(name = 'musterQueueManager', target=populateMusterQueue, args=(logger,q,queueSize,stateCode,addLimit ))
  #t1.daemon = True
#  t1.start()


  #Starting Crawler Threads
  driverArray=[]
  displayArray=[]
  for i in range(numberOfThreads):
    logger.info("Starting worker Thread %s " % str(i))
    
    display =''# displayInitialize(args['visible'])
    driver = ''#driverInitialize(args['browser'])
    driverArray.append(driver)
    displayArray.append(display)
    t = Thread(name = 'Thread-' + str(i), target=musterDownloadWorker, args=(logger,q,args,driver,display ))
    t.daemon = True
    t.start()

#  time.sleep(120) 
  q.join()       # block until all tasks are done
  for i in range(numberOfThreads):
    q.put(None)
# for driver in driverArray:
#   driverFinalize(driver)
# for display in displayArray:
#   displayFinalize(display)

  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
