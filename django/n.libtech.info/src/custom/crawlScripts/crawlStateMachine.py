
from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
from subprocess import call,Popen,check_output,PIPE
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,startFinYear,panchayatCrawlThreshold,panchayatRetryThreshold,telanganaStateCode,panchayatAttemptRetryThreshold,apStateCode,crawlRetryThreshold,crawlProcessTimeThreshold,logDir
#from crawlFunctions import crawlPanchayat,crawlPanchayatTelangana,libtechCrawler
from libtechCrawler import libtechCrawler
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from libtechInit import libtechLoggerFetch
from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q,Sum,Count
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag,CrawlQueue,CrawlState,Task

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-downloadLimit', '--downloadLimit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='State for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-sf', '--startFinYear', help='From which financial year data needs to be crawled default is 2015-2016', required=False)
  parser.add_argument('-step', '--step', help='Step for which the script needs to run', required=False)
  parser.add_argument('-pc', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-qid', '--qid', help='Queue Id for which this needs to be run', required=False)
  parser.add_argument('-bc', '--blockCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-m', '--manage', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-e', '--execute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-p', '--populate', help='Populate CrawlQueue', required=False,action='store_const', const=1)
  parser.add_argument('-f', '--force', help='Force Run a step', required=False,action='store_const', const=1)
  parser.add_argument('-se', '--singleExecute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-csm', '--crawlStateMachine', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-d', '--debug', help='Debug Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-t', '--test', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)

  args = vars(parser.parse_args())
  return args

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

def getNextCrawlState(logger,crawlState,isNIC,isAP):
  nextSequence=crawlState.sequence+1
  if isNIC==True:
    nextCrawlState=CrawlState.objects.filter(sequence=nextSequence,crawlType="NIC").first()
  elif isAP==True: 
    nextCrawlState=CrawlState.objects.filter(sequence=nextSequence,crawlType="AP").first()
  else:
    nextCrawlState=None
  return nextCrawlState

def getCrawlObjs(logger,crawlStateName,eachBlock=None,eachPanchayat=None,isPanchayatLevelProcess=None):
  myobjs=None
  if isPanchayatLevelProcess == True:
    if eachBlock is not None:
      myobjs=Panchayat.objects.filter(block=eachBlock)
    else:
      myobjs=Panchayat.objects.filter(id=eachPanchayat.id)
  return myobjs

def populateTasks(logger,eachCrawlQueue):
  crawlStateName=eachCrawlQueue.crawlState.name
  crawlState=eachCrawlQueue.crawlState
  isPanchayatLevelProcess=eachCrawlQueue.crawlState.isPanchayatLevelProcess
  myobjs=getCrawlObjs(logger,crawlStateName,eachBlock=eachCrawlQueue.block,eachPanchayat=eachCrawlQueue.panchayat,isPanchayatLevelProcess=isPanchayatLevelProcess)
  for obj in myobjs:
    myTask=Task.objects.create(crawlQueue=eachCrawlQueue,crawlState=crawlState,objID=obj.id)

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  if args['crawlStateMachine']:
    logger.info("Running Crawl State Machine")
    crawlObjects=CrawlQueue.objects.filter(isComplete=False,isProcessDriven=True)
    for eachCrawlQueue in crawlObjects:
      crawlState=eachCrawlQueue.crawlState
      logger.info("Processing QID %s" % str(eachCrawlQueue.id))
      stateCode=getCrawlQueueStateCode(logger,eachCrawlQueue)
      isNIC=getCrawlQueueIsNIC(logger,eachCrawlQueue)
      if stateCode == apStateCode:
        isAP=True
      else:
        isAP=False

      proceedNextStage=False
      if crawlState.name == "initial":
        proceedNextStage=True

      if proceedNextStage == True:
        nextCrawlState=getNextCrawlState(logger,crawlState,isNIC,isAP)
        eachCrawlQueue.crawlState=nextCrawlState
        eachCrawlQueue.save()
        populateTasks(logger,eachCrawlQueue)

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
