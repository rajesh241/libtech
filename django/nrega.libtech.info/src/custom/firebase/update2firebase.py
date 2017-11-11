from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
from firebase import firebase
sys.path.insert(0, "./../scripts")
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

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag,Jobcard,Worker

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
  parser.add_argument('-upt', '--updatePanchayatTable', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-ujt', '--updateJobcardTable', help='Update Jobcard Table', required=False, action='store_const', const=1)
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
  tagArray=LibtechTag.objects.filter(name="Always")

  if args['getPanchayatTable']:
    logger.info("Will Fetch Panchayat Table")
    exampleDictKey="jharkhand_latehar_manika_matlong"
    panchayatDict=firebase.get('https://libtech-app.firebaseio.com/panchayats/',exampleDictKey)
    logger.info(panchayatDict)
    if exampleDictKey in panchayatDict:
      logger.info("They Key Exists")
    else:
      logger.info("Key Does not Exists")

  if args['updatePanchayatTable']:
    if stateCode is not None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__code=stateCode,libtechTag__in=tagArray)
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

  if args['updateJobcardTable']:
    tagArray=LibtechTag.objects.filter(name="baselineTreatment")
    totalCredited=0
    totalPending=0
    totalRejected=0
    totalInvalid=0
    if stateCode is not None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__code=stateCode,libtechTag__in=tagArray)
    else:  
      myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',libtechTag__in=tagArray)
    for eachPanchayat in myPanchayats:
      jobcards={}
      panchayatDictKey="%s_%s_%s_%s" % (eachPanchayat.block.district.state.slug,eachPanchayat.block.district.slug,eachPanchayat.block.slug,eachPanchayat.slug)
      logger.info(panchayatDictKey)
      jobcards=firebase.get('https://libtech-app.firebaseio.com/jobcards/',panchayatDictKey)
      logger.info(jobcards)
      myJobcards=Jobcard.objects.filter(panchayat=eachPanchayat)[:limit]
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


        if villageSlug not in jobcards:
          jobcards[villageSlug] = {}
        
        if jobcardSlug in jobcards[villageSlug]:
           logger.info(jobcardSlug)
           myJobcard=jobcards[villageSlug][jobcardSlug]['jobcard']
           if 'applicants' in jobcards[villageSlug][jobcardSlug]:
             myWorkers=jobcards[villageSlug][jobcardSlug]['applicants']
             i=0
             logger.info("Applicants Exits")
             logger.info(len(myWorkers))
             while i < len(myWorkers):
               if myWorkers[i] != None:
                 logger.info("The value of is is %d" % i)
                 logger.info(myWorkers[i])
                 name=''
                 if "name" in myWorkers[i]:
                   name=myWorkers[i]['name']
                 if "phone" in myWorkers[i]:
                   logger.info("Phone for applicant %s is %s " % (name,myWorkers[i]['phone']))
                   myWorker=Worker.objects.filter(jobcard__jobcard=myJobcard,name=name).first()
                   if myWorker is not None:
                     logger.info("The name of my Worker is %s " % (myWorker.name))
               i=i+1
        #Updating of Jobcards is Finished now we shall overwrite the array with new information.
    #  jobcards=firebase.get('https://libtech-app.firebaseio.com/jobcards/',panchayatDictKey)
      result = firebase.patch('https://libtech-app.firebaseio.com/jobcards/%s/' % (panchayatDictKey), jobcards)

#       if panchayatSlug not in jobcards:
#         jobcards[panchayatSlug] = {}
#       if villageSlug not in jobcards[panchayatSlug]:
#         jobcards[panchayatSlug][villageSlug] = {}
#       jobcards[panchayatSlug][villageSlug][jobcardSlug] = {'totCredited': str(totalCredited), 'totPending': str(totalPending), 'totRejected': str(totalRejected), 'totInvalid': str(totalInvalid), 'jobcard_slug': jobcardSlug, 'jobcard': eachJobcard.jobcard}
#
#       if 'applicants' not in jobcards[panchayatSlug][villageSlug][jobcardSlug]:
#         jobcards[panchayatSlug][villageSlug][jobcardSlug]['applicants'] = {}
#       
#       myWorkers=Worker.objects.filter(jobcard=eachJobcard)
#       for eachWorker in myWorkers:
#         applicantNo=eachWorker.applicantNo
#         jobcards[panchayatSlug][villageSlug][jobcardSlug]['applicants'][applicantNo] = {'name': str(eachWorker.name), 'gender': str(eachWorker.gender), 'age': str(eachWorker.age), 'relationship': eachWorker.relationship, 'fatherHusbandName': eachWorker.fatherHusbandName}
     # result = firebase.patch('https://libtech-app.firebaseio.com/jobcards/', jobcards)




  logger.info("...END PROCESSING") 
  exit(0)

if __name__ == '__main__':
  main()
