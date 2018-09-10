from bs4 import BeautifulSoup
import requests
import os
import sys
import re
import urllib.request
import django
from subprocess import call,Popen

from django.core.wsgi import get_wsgi_application
from django.db.models import Count,Sum
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings
from apuSurvey import createWorkDaysReport,createAPUWorkPaymentAP,sampleWorkersAP,updateAPWorkPayment,selectWorkersAPU,createSampleWorkersReport,createTransactionReport,getDiffFTOMuster,createTransactionReportHTML,justlikethat
#from crawlFunctions import getAPJobcardData,computeWorkPaymentStatus,crawlWagelists,parseMuster,getAPJobcardData,processAPJobcardData,computeJobcardStat,getJobcardRegister1
from crawlFunctions import getJobcardRegister1,jobcardRegister
from reportFunctions import createJobcardReport
from nregaFunctions import is_ascii
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
from wrappers.logger import loggerFetch
sys.path.append(djangoDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
# This is so Django knows where to find stuff.
# This is so my local_settings.py gets loaded.
django.setup()
from nrega.models import State,District,Block,Panchayat,PaymentInfo,LibtechTag,CrawlQueue,Jobcard,APWorkPayment,Wagelist,Worker,Village,LanguageDict
from django.contrib.auth.models import User



def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-t', '--test', help='Test Function can be used to run any script', required=False, action='store_const', const=1)
  parser.add_argument('-s', '--sample', help='Run a Sub Process', required=False, action='store_const', const=1)
  parser.add_argument('-tr', '--transactionReport', help='Create Transaction Report', required=False, action='store_const', const=1)
  parser.add_argument('-sp', '--selectPanchayats', help='Select Panchayats Randomly', required=False, action='store_const', const=1)
  parser.add_argument('-cd', '--createDict', help='Select Panchayats Randomly', required=False, action='store_const', const=1)
  parser.add_argument('-gh', '--getHindi', help='Select Panchayats Randomly', required=False, action='store_const', const=1)
  parser.add_argument('-ti', '--testInput', help='Log level defining verbosity', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['sample']:
    logger.info("Sampling jobcards")
    blockCodes=['0203020']
    for blockCode in blockCodes:
      eachBlock=Block.objects.filter(code=blockCode).first()
      createSampleWorkersReport(logger,eachBlock)
  #   myPanchayats=Panchayat.objects.filter(block__code=blockCode)
  #   for eachPanchayat in myPanchayats:
  #     logger.info("Processing panchayat %s " % eachPanchayat.name)
  #     selectWorkersAPU(logger,eachPanchayat)

  if args['createDict']:
    filename="/tmp/dict1.csv"
    with open(filename) as fp:
      for line in fp:
        line=line.lstrip().rstrip()
        if line != '':
          phrases=line.split(",")
          phrase1=phrases[0]
          phrase2=phrases[1]
          logger.info("phrease 1 %s phrase 2 %s " % (phrase1,phrase2))
          LanguageDict.objects.create(phrase1=phrase1,lang1="english",phrase2=phrase2,lang2="telugu") 
  if args['transactionReport']:
    myPanchayats=Panchayat.objects.filter(block__code="0203020")
    for eachPanchayat in myPanchayats:
      logger.info("Creating reports for %s %s " % (eachPanchayat.name,eachPanchayat.code))
      createTransactionReportHTML(logger,eachPanchayat)
#      justlikethat(logger,eachPanchayat)

  if args['test']:
    eachBlock=Block.objects.filter(code="0203020").first()
    getDiffFTOMuster(logger,eachBlock)
    exit(0)
    myobjs=Jobcard.objects.filter(panchayat__block__code="0203020",downloadManager__isnull=False)
    n=len(myobjs)
    for obj in myobjs:
      logger.info(n)
      n=n-1
      myDM=obj.downloadManager
      myDM.isProcessed=False
      myDM.save()
    exit(0)
    jobcardID=args['testInput']
    error=apJobcardProcess(logger,jobcardID)
    exit(0)
    logger.info("Doing Test")
    blockCodes=["2721003"]
    blockCodes=['0203020']
    for blockCode in blockCodes:
      myPanchayats=Panchayat.objects.filter(block__code=blockCode)[:1]
      for eachPanchayat in myPanchayats:
        createWorkDaysReport(logger,eachPanchayat)
        #createAPUWorkPaymentAP(logger,eachPanchayat)
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
