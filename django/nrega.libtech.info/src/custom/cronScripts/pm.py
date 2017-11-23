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
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
regex1=re.compile(r'</td></font></td>',re.DOTALL)
from customSettings import repoDir,djangoDir,djangoSettings
from customSettings import musterTimeThreshold
sys.path.insert(0, repoDir)
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getjcNumber,getVilCode
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone


os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag,WorkDetail,Wagelist,Worker,Applicant

maxMusterDownloadQueue=200


def populateMusterQueue(logger,q,queueSize,stateCode,panchayatCode,musterID,addLimit):
  alwaysTag=LibtechTag.objects.filter(name="Always")
  if musterID is not None:
    myMusters=Muster.objects.filter(id=musterID)
  elif panchayatCode is not None:
    myMusters=Muster.objects.filter(isDownloaded=1,isProcessed=0,panchayat__crawlRequirement="FULL",panchayat__code=panchayatCode)[:addLimit] 
  elif stateCode is not None:
    myMusters=Muster.objects.filter(isDownloaded=1,isProcessed=0,panchayat__isnull=False,panchayat__crawlRequirement="FULL",panchayat__block__district__state__code=stateCode)[:addLimit] 
  else:
    myMusters=Muster.objects.filter(isDownloaded=1,isProcessed=0,panchayat__isnull=False,panchayat__crawlRequirement="FULL")[:addLimit]

  musterIDs=''
  logger.info("Lenght of myMusters is "+str(len(myMusters)))
  if len(myMusters) > 0:
    for eachMuster in myMusters:
      musterIDs+=str(eachMuster.id)+"-"
      q.put(eachMuster.id)
      eachMuster.musterDownloadAttemptDate=timezone.now()
      eachMuster.save()
    logger.info("Added Musters: %s " % musterIDs)

def processMuster(logger,eachMuster):
  error=None
  if error is None:
    logger.info("MusterID: %s MusterNo: %s, blockCode: %s, finyear: %s workName:%s" % (eachMuster.id,eachMuster.musterNo,eachMuster.block.code,eachMuster.finyear,eachMuster.workName))
#    logger.info(eachMuster.panchayat.code+eachMuster.panchayat.crawlRequirement+eachMuster.panchayat.name)
    myhtml=eachMuster.musterFile.read()

#Getting the Payment Date from Muster HTML
    s1=myhtml.decode("UTF-8").replace(u'\xa0', u' ')
    s=s1.replace("\n","").replace("\r","").replace(" ","")
    r=re.search('PaymentDate:([^\<]*)',s)
    if r is not None:
      paymentDateString=r.group(1).lstrip().rstrip()
      if paymentDateString != '':
        paymentDate = time.strptime(paymentDateString, '%d/%m/%Y')
        paymentDate = time.strftime('%Y-%m-%d', paymentDate)
      else:
        paymentDate=None
    else:
      paymentDate=None

    stateShortCode=eachMuster.block.district.state.stateShortCode
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    mytable=htmlsoup.find('table',id="musterDetails")
    tr_list = mytable.findAll('tr')
    acnoPresent=0
    for tr in tr_list: #This loop is to find staus Index
      cols = tr.findAll('th')
      if len(cols) > 7:
        i=0
        
        while i < len(cols):
          value="".join(cols[i].text.split())
          if "Status" in value:
            statusindex=i
          if ("Sharpening Charge" in cols[i].text) or ("औज़ार सम्बंधित भुगतान" in cols[i].text):
            sharpeningIndex=i
          if ("A/C No." in cols[i].text) or ("खाता क्रमांक" in cols[i].text):
            acnoPresent=1
          i=i+1
    isComplete=1
    allApplicantFound=1
    allWorkerFound=True
    totalCount=0
    totalPending=0
    reMatchString="%s-" % (stateShortCode)
    #logger.info("Account No Presnet: %s " % str(acnoPresent))
    #logger.info("Sharpening Index is %s " % str(sharpeningIndex))
    for i in range(len(tr_list)):
      cols=tr_list[i].findAll("td")
      if len(cols) > 7:
        nameandjobcard=cols[1].text.lstrip().rstrip()
        if stateShortCode in nameandjobcard:
          totalCount=totalCount+1
          status=cols[statusindex].text.lstrip().rstrip()
          if status != 'Credited':
            totalPending=totalPending+1
            isComplete=0      
          musterIndex=cols[0].text.lstrip().rstrip()
          nameandjobcard=cols[1].text.lstrip().rstrip()
          nameandjobcard=nameandjobcard.replace('\n',' ')
          nameandjobcard=nameandjobcard.replace("\\","")
          nameandjobcardarray=re.match(r'(.*)'+reMatchString+'(.*)',nameandjobcard)
          name_relationship=nameandjobcardarray.groups()[0]
          name=name_relationship.split("(")[0].lstrip().rstrip()
#          accountno=cols[statusindex-5].text.lstrip().rstrip()
          totalWage=cols[sharpeningIndex-2].text.lstrip().rstrip()
          dayWage=cols[sharpeningIndex-3].text.lstrip().rstrip()
          daysWorked=cols[sharpeningIndex-4].text.lstrip().rstrip()
          jobcard=reMatchString+nameandjobcardarray.groups()[1].lstrip().rstrip()
         #if acnoPresent == 1:
         #  totalWage=cols[statusindex-6].text.lstrip().rstrip()
         #  dayWage=cols[statusindex-10].text.lstrip().rstrip()
         #  daysWorked=cols[statusindex-11].text.lstrip().rstrip()
         #else:
         #  totalWage=cols[statusindex-5].text.lstrip().rstrip()
         #  dayWage=cols[statusindex-9].text.lstrip().rstrip()
         #  daysWorked=cols[statusindex-10].text.lstrip().rstrip()
          #logger.info("TotalWage: %s daywage: %s " % (totalWage,dayWage))
          wagelistNo=cols[statusindex-1].text.lstrip().rstrip()
          creditedDateString=cols[statusindex+1].text.lstrip().rstrip()
          if creditedDateString != '':
            creditedDate = time.strptime(creditedDateString, '%d/%m/%Y')
            creditedDate = time.strftime('%Y-%m-%d', creditedDate)
          else:
            creditedDate=None
        myWDRecord=WorkDetail.objects.filter(muster=eachMuster,musterIndex=musterIndex).first()
        if myWDRecord is None:
          #logger.info("New Record Created")
          WorkDetail.objects.create(muster=eachMuster,musterIndex=musterIndex)
        myWDRecord=WorkDetail.objects.filter(muster=eachMuster,musterIndex=musterIndex).first()
        
        matchedWagelist=Wagelist.objects.filter(wagelistNo=wagelistNo,block=eachMuster.panchayat.block,finyear=eachMuster.finyear).first()
        if matchedWagelist is None:
          try:
            Wagelist.objects.create(wagelistNo=wagelistNo,block=eachMuster.panchayat.block,finyear=eachMuster.finyear)
          except:
            logger.info("Wagelist created by Another Thread")
        matchedWagelist=Wagelist.objects.filter(wagelistNo=wagelistNo,block=eachMuster.panchayat.block,finyear=eachMuster.finyear).first()

        myWDRecord.wagelist.add(matchedWagelist)
        matchedWorkers=Worker.objects.filter(jobcard__jobcard=jobcard,name=name)
        if len(matchedWorkers) == 1:
          myWDRecord.worker=matchedWorkers.first()
        else:
          allWorkerFound=False
           
        matchedApplicants=Applicant.objects.filter(jobcard__jobcard=jobcard,name=name)
        #logger.info("jobcard %s name: %snameENds " % (jobcard,name)) 
        if len(matchedApplicants) == 1:
          #logger.info("MatchedApplicant Found")
          myWDRecord.applicant=matchedApplicants.first()
        else:
          #logger.info(str(len(matchedApplicants)))
          allApplicantFound=0
        myWDRecord.zjcNo=getjcNumber(jobcard) 
        myWDRecord.zvilCode=getVilCode(jobcard) 
        myWDRecord.zname=name
        myWDRecord.zjobcard=jobcard
#        myWDRecord.zaccountNo=accountno
        myWDRecord.totalWage=totalWage
        myWDRecord.dayWage=dayWage
        myWDRecord.daysWorked=daysWorked
        myWDRecord.creditedDate=creditedDate
        myWDRecord.musterStatus=status 
        myWDRecord.save()
    eachMuster.isComplete=isComplete
    eachMuster.paymentDate=paymentDate
    eachMuster.isProcessed=1
    eachMuster.allApplicantFound=allApplicantFound
    eachMuster.allWorkerFound=allWorkerFound
    eachMuster.save()
    #logger.info("Processed Muster: MusterID: %s MusterNo: %s, blockCode: %s, finyear: %s workName:%s all ApplicantFound: %s " % (eachMuster.id,eachMuster.musterNo,eachMuster.block.code,eachMuster.finyear,eachMuster.workName,str(allApplicantFound)))
  
  return error


def musterProcessWorker(logger,q,inputargs):
  while True:
    musterID = q.get()  # if there is no url, this will wait
    if musterID is None:
      break
    name = threading.currentThread().getName()

    eachMuster=Muster.objects.filter(id=musterID).first()
#   try:
#     myhtml=getMuster(logger,eachMuster)
#     myhtml=myhtml.replace("</td></td>","</td>")
#     error,musterTable,musterSummaryTable=validateMusterHTML(eachMuster,myhtml)
#   except:
#     error="downloadError"
    error=processMuster(logger,eachMuster)
    errorString='' 
    logger.info("Processing name: %s musterID: %s musterNo: %s FullblockCode: %s status: %s" % (name,str(eachMuster.id),eachMuster.musterNo,eachMuster.block.code,errorString))
    #nlogger.info(eachMuster.musterURL)

    q.task_done()
 
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
  parser.add_argument('-m', '--musterID', help='MusterID that needs tobe processed', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  stateCode=args['stateCode']
  panchayatCode=args['panchayatCode']
  musterID=args['musterID']
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1

  if args['queueSize']:
    queueSize=int(args['queueSize'])
  else:
    queueSize=20

  if args['numberOfThreads']:
    numberOfThreads=int(args['numberOfThreads'])
  else:
    numberOfThreads=5


  addLimit = queueSize-numberOfThreads
  if addLimit < 0:
    addLimit =1

  logger.info("Starting Muster Download Script with Queue Size: %s and Number of Threads: %s " % (queueSize,numberOfThreads))
  q = Queue(maxsize=queueSize)
  populateMusterQueue(logger,q,queueSize,stateCode,panchayatCode,musterID,addLimit)


  #Starting Crawler Threads
  for i in range(numberOfThreads):
    logger.info("Starting worker Thread %s " % str(i))
    
    t = Thread(name = 'Thread-' + str(i), target=musterProcessWorker, args=(logger,q,args ))
    t.daemon = True
    t.start()

  q.join()       # block until all tasks are done
  for i in range(numberOfThreads):
    q.put(None)

  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
