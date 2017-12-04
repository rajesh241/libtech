from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
from queue import Queue
from threading import Thread
import threading
import os
import sys
import re
import time
from firebase import firebase
sys.path.insert(0, "./../scripts")
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,startFinYear

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,getCurrentFinYear
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag,Jobcard,Worker,Phonebook,Partner,WorkDetail
def getNumberProcesses(q):
  if q < 10:
    n=1
  elif q < 100:
    n=10
  elif q< 500:
    n=40
  else:
    n=80
  return n
def updateTransactionTableWorker(logger,q,firebase):
  while True:
    myID = q.get()  # if there is no url, this will wait
    if myID is None:
      break
    name = threading.currentThread().getName()

    eachJobcard=Jobcard.objects.filter(id=myID).first()
    error=updateJobcardNode(logger,firebase,eachJobcard)
    errorString='' 
    logger.info("Current Queue: %s Thread : %s Jobcard: %s FullblockCode: %s status: %s" % (str(q.qsize()),name,eachJobcard.jobcard,eachJobcard.panchayat.block.code,errorString))

    q.task_done()
 



def getJobcardDictKey(logger,eachJobcard):
  if eachJobcard.panchayat.block.district.state.isNIC == True:
    jobcardSlug=eachJobcard.jobcard.replace("/","_")
    myJobcard=eachJobcard.jobcard
  else:
    jobcardSlug=eachJobcard.tjobcard
    myJobcard=eachJobcard.tjobcard
  return jobcardSlug,myJobcard

def updateJobcardNode(logger,firebase,eachJobcard):
  error=None
  #logger.info("Updating Jobcard Node %s " % eachJobcard.jobcard)
  jobcardDictKey,myJobcard=getJobcardDictKey(logger,eachJobcard)
#  result = firebase.delete('https://libtech-app.firebaseio.com/transactions/%s/' % (jobcardDictKey),None)
  transactions=firebase.get('https://libtech-app.firebaseio.com/transactions/',jobcardDictKey)
  if transactions is None:
    transactions={}
  # Fetch all the workers related tot his jobcard.

  myWorkers=Worker.objects.filter(jobcard=eachJobcard)
  for eachWorker in myWorkers:
    #logger.info(eachWorker.name)
    myWDRecords=WorkDetail.objects.filter(worker=eachWorker)
    for eachWDRecord in myWDRecords:
      #logger.info(eachWDRecord)
      startDate=eachWDRecord.muster.dateFrom
      startDateString=startDate.strftime('%Y%m%d')
      applicantNo=eachWorker.applicantNo
      wagelistArray=eachWDRecord.wagelist.all()
      if len(wagelistArray) > 0:
        wagelist=wagelistArray[len(wagelistArray) -1 ].wagelistNo
      else:
        wagelist=''
      curKey='%s:%s%s' % (jobcardDictKey,startDateString,str(eachWorker.applicantNo))
    #  logger.info(curKey) 
      if curKey not in transactions:
        transactions[curKey]={}
        overWriteTransactions=True
      else:
        #Here we need to write the Code for reading the transactions.
        curTransaction=transactions[curKey]
        #logger.info(curTransaction)
        overWriteTransactions=False

      if overWriteTransactions==True:
        transactions[curKey] = {'wdID':str(eachWDRecord.id),'musterStatus': eachWDRecord.musterStatus, 'musterNo': str(eachWDRecord.muster.musterNo), 'creditedDate': eachWDRecord.creditedDate, 'daysWorked': eachWDRecord.daysWorked, 'workName': eachWDRecord.muster.workName, 'jobcard': eachJobcard.jobcard, 'totalWage': eachWDRecord.totalWage, 'secondSignatoryDate': '', 'accountNo': '', 'dateFrom': eachWDRecord.muster.dateFrom, 'name': eachWorker.name, 'paymentDate': '', 'dateTo': eachWDRecord.muster.dateTo, 'wagelistNo': wagelist, 'panchayatName': eachJobcard.panchayat.name }
#  logger.info(transactions)
  result = firebase.patch('https://libtech-app.firebaseio.com/transactions/%s/' % (jobcardDictKey), transactions)
  return result


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='State for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-p', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-b', '--blockCode', help='Block for which the data needs to be updated', required=False)
  parser.add_argument('-j', '--jobcard', help='Jobcard for which date needs to be updated', required=False)
  parser.add_argument('-upt', '--updatePanchayatTable', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-dpt', '--deletePanchayatTable', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-ujt', '--updateJobcardTable', help='Update Jobcard Table', required=False, action='store_const', const=1)
  parser.add_argument('-utt', '--updateTransactionTable', help='Update Transaction Table', required=False, action='store_const', const=1)
  parser.add_argument('-djt', '--deleteJobcardTable', help='Update Jobcard Table', required=False, action='store_const', const=1)
  parser.add_argument('-gpt', '--getPanchayatTable', help='Get Panchayat Table', required=False, action='store_const', const=1)

  args = vars(parser.parse_args())
  return args


def main():
  from firebase import firebase
  firebase = firebase.FirebaseApplication('https://libtech-app.firebaseio.com/', None)
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  stateCode=args['stateCode']
  panchayatCode=args['panchayatCode']
  blockCode=args['blockCode']
  logger.info(blockCode)
  tagArray=LibtechTag.objects.filter(name="JSK")
  myPartner=Partner.objects.filter(slug='jharkhand-sahayta-kendra').first()
  if args['getPanchayatTable']:
    logger.info("Will Fetch Panchayat Table")
    exampleDictKey="jharkhand_latehar_manika_matlong"
    panchayatDict=firebase.get('https://libtech-app.firebaseio.com/panchayats/',exampleDictKey)
    logger.info(panchayatDict)
    if exampleDictKey in panchayatDict:
      logger.info("They Key Exists")
    else:
      logger.info("Key Does not Exists")


  if args['deletePanchayatTable']:
    panchayats=firebase.get('https://libtech-app.firebaseio.com/panchayats/',None)
    for key in panchayats:
      logger.info(key)
      result = firebase.delete('https://libtech-app.firebaseio.com/panchayats/%s/' % (key),None)
       
  if args['updatePanchayatTable']:
    if stateCode is not None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__code=stateCode,libtechTag__in=tagArray)
    elif blockCode is not None:
      myPanchayats=Panchayat.objects.filter(block__code=blockCode)
    elif panchayatCode is not None:
      myPanchayats=Panchayat.objects.filter(code=panchayatCode)
    else:  
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',libtechTag__in=tagArray)
    panchayatDict={}
    for eachPanchayat in myPanchayats:
      stateName=eachPanchayat.block.district.state.name
      districtName=eachPanchayat.block.district.name
      blockName=eachPanchayat.block.name
      panchayatName=eachPanchayat.name
      logger.info(stateName+districtName+blockName)
      dictKey="%s_%s_%s_%s" % (eachPanchayat.block.district.state.slug,eachPanchayat.block.district.slug,eachPanchayat.block.slug,eachPanchayat.slug)
      panchayatDict[dictKey] = {'state': eachPanchayat.block.district.state.name, 'district': eachPanchayat.block.district.name, 'block': eachPanchayat.block.name, 'name': eachPanchayat.name, 'slug': dictKey, 'code': eachPanchayat.code, 'jobcardCode': eachPanchayat.code}
    logger.info(panchayatDict)
    result = firebase.patch('https://libtech-app.firebaseio.com/panchayats/', panchayatDict)

  if args['deleteJobcardTable']:
    if stateCode is not None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__code=stateCode,libtechTag__in=tagArray)
    elif blockCode is not None:
      myPanchayats=Panchayat.objects.filter(block__code=blockCode)
    elif panchayatCode is not None:
      myPanchayats=Panchayat.objects.filter(code=panchayatCode)
    else:  
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',libtechTag__in=tagArray)
    for eachPanchayat in myPanchayats:
      panchayatDictKey="%s_%s_%s_%s" % (eachPanchayat.block.district.state.slug,eachPanchayat.block.district.slug,eachPanchayat.block.slug,eachPanchayat.slug)
      result = firebase.delete('https://libtech-app.firebaseio.com/jobcards/%s/' % (panchayatDictKey),None)

  if args['updateJobcardTable']:
    totalCredited=0
    totalPending=0
    totalRejected=0
    totalInvalid=0
    if stateCode is not None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__code=stateCode,libtechTag__in=tagArray)
    elif blockCode is not None:
      myPanchayats=Panchayat.objects.filter(block__code=blockCode)
    elif panchayatCode is not None:
      myPanchayats=Panchayat.objects.filter(code=panchayatCode)
    else:  
      myPanchayats=Panchayat.objects.filter(libtechTag__in=tagArray)
    for eachPanchayat in myPanchayats:
      jobcards={}
      panchayatDictKey="%s_%s_%s_%s" % (eachPanchayat.block.district.state.slug,eachPanchayat.block.district.slug,eachPanchayat.block.slug,eachPanchayat.slug)
      logger.info(panchayatDictKey)
      jobcards=firebase.get('https://libtech-app.firebaseio.com/jobcards/',panchayatDictKey)
      if jobcards is None:
        logger.info("Jobcards is Empty")
        jobcards={}
      #logger.info(jobcards)
      myJobcards=Jobcard.objects.filter(panchayat=eachPanchayat)
      phoneDict={} 
      for eachJobcard in myJobcards:
        panchayatSlug="%s_%s_%s_%s" % (eachJobcard.panchayat.block.district.state.slug,eachJobcard.panchayat.block.district.slug,eachJobcard.panchayat.block.slug,eachJobcard.panchayat.slug) 
        villageSlug="Unknown"
        if eachJobcard.village.slug:
          villageSlug=eachJobcard.village.slug
        if eachJobcard.panchayat.block.district.state.isNIC == True:
          jobcardSlug=eachJobcard.jobcard.replace("/","_")
          myJobcard=eachJobcard.jobcard
        else:
          jobcardSlug=eachJobcard.tjobcard
          myJobcard=eachJobcard.tjobcard

        phoneDict[eachJobcard.jobcard] = {}
        if villageSlug not in jobcards:
          jobcards[villageSlug] = {}
        if jobcardSlug in jobcards[villageSlug]:
           logger.info(jobcardSlug)
           myJobcard=jobcards[villageSlug][jobcardSlug]['jobcard']
           if 'applicants' in jobcards[villageSlug][jobcardSlug]:
             myWorkers=jobcards[villageSlug][jobcardSlug]['applicants']
             logger.info("Printing my Workers")
            # logger.info(myWorkers)
             totalWorkers=len(myWorkers)
             logger.info("Length of Total Workers is %s " % str(len(myWorkers)))
             for eachWorker in myWorkers:
               if eachWorker is not None:
                 #logger.info("printing each Worker %s " %str(eachWorker))
                 try:
                   key=myWorkers.index(eachWorker)
                   curWorker=eachWorker
                 except:
                   key=eachWorker
                   curWorker=myWorkers[key]
                 logger.info(key)
                 logger.info(curWorker)
                 if 'phone' in curWorker:
                   phone=curWorker['phone']
                   logger.info("Phone for applicant %s is %s " % (str(key),phone))
                   phoneDict[eachJobcard.jobcard][key]=phone
             key=5000
             while key < totalWorkers:
               logger.info("The value of is is %d" % key)
               name=''
               if myWorkers[key] is not None:
                 logger.info(myWorkers[key])
                 if "name" in myWorkers[key]:
                   name=myWorkers[key]['name']
                 if "phone" in myWorkers[key]:
                   phone=myWorkers[key]['phone']
                   logger.info("Phone for applicant %s is %s " % (name,myWorkers[key]['phone']))
                   phoneDict[key]=phone
               key=key+1
        
        jobcards[villageSlug][jobcardSlug] = {'totCredited': str(totalCredited), 'totPending': str(totalPending), 'totRejected': str(totalRejected), 'totInvalid': str(totalInvalid), 'jobcard_slug': jobcardSlug, 'jobcard': eachJobcard.jobcard}
        if 'applicants' not in jobcards[villageSlug][jobcardSlug]:
          jobcards[villageSlug][jobcardSlug]['applicants'] = {}
        
        jobcards[villageSlug][jobcardSlug]['applicants'] = {}
        #jobcards[villageSlug][jobcardSlug]['applicants'][0] = {'name':'','age':0}
        #jobcards[villageSlug][jobcardSlug]['applicants'][0] = None
        myWorkers=Worker.objects.filter(jobcard=eachJobcard).order_by("-applicantNo")
        for eachWorker in myWorkers:
          applicantNo=eachWorker.applicantNo
          if applicantNo in phoneDict[eachJobcard.jobcard]:
            phone=phoneDict[eachJobcard.jobcard][applicantNo]
            if phone.isdigit() and len(phone) == 10:
              myPhonebook=Phonebook.objects.filter(phone=phone).first()
              if myPhonebook is None:
                Phonebook.objects.create(phone=phone,partner=myPartner)
              myPhonebook=Phonebook.objects.filter(phone=phone).first()
              myPhonebook.worker=eachWorker
              myPhonebook.panchayat=eachPanchayat
              myPhonebook.save()
            logger.info("Phone nuber for Jobcard %s applicantNo %s is %s " % (eachJobcard.jobcard,applicantNo,'abcd'))
          else:
            phone=None
          if int(applicantNo) != 0:
            jobcards[villageSlug][jobcardSlug]['applicants'][applicantNo] = {'name': str(eachWorker.name), 'gender': str(eachWorker.gender), 'age': str(eachWorker.age), 'relationship': eachWorker.relationship, 'fatherHusbandName': eachWorker.fatherHusbandName,'phone' : phone}


      result = firebase.patch('https://libtech-app.firebaseio.com/jobcards/%s/' % (panchayatDictKey), jobcards)

  if args['updateTransactionTable']:
    logger.info("Updating the Transaction Table")
    if stateCode is not None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__code=stateCode,libtechTag__in=tagArray)
    elif blockCode is not None:
      myPanchayats=Panchayat.objects.filter(block__code=blockCode)
    elif panchayatCode is not None:
      myPanchayats=Panchayat.objects.filter(code=panchayatCode)
    else:  
      myPanchayats=Panchayat.objects.filter(libtechTag__in=tagArray)
    panchayatIDArray=[]
    for eachPanchayat in myPanchayats:
      panchayatIDArray.append(eachPanchayat.id)

    myJobcards=Jobcard.objects.filter(panchayat__id__in=panchayatIDArray)
    logger.info("Length of my jobcards %s " % str(len(myJobcards)))
    if len(myJobcards) > 0:
      n=getNumberProcesses(len(myJobcards))
      queueSize=n+len(myJobcards)+10
      q = Queue(maxsize=queueSize)
      logger.info("Queue Size %s Numbe of Threads %s " % (str(queueSize),str(n)))
      for eachJobcard in myJobcards:
        q.put(eachJobcard.id)
   
      for i in range(n):
        logger.info("Starting worker Thread %s " % str(i))
        t = Thread(name = 'Thread-' + str(i), target=updateTransactionTableWorker, args=(logger,q,firebase ))
        t.daemon = True  
        t.start()
   
   
      q.join()       # block until all tasks are done
      for i in range(n):
        q.put(None)


  logger.info("...END PROCESSING") 
  exit(0)

if __name__ == '__main__':
  main()
