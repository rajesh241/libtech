from bs4 import BeautifulSoup
import requests
import os
import sys
from os import errno
import datetime
import re
import urllib.request
import django
from subprocess import call,Popen

from django.core.wsgi import get_wsgi_application
from django.db.models import Count,Sum
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings
from apuSurvey import createWorkDaysReport,createAPUWorkPaymentAP,sampleWorkersAP,updateAPWorkPayment,selectWorkersAPU,createSampleWorkersReport,createTransactionReport,getDiffFTOMuster,createTransactionReportHTML,justlikethat,createAPURajendran
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


def create_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
  

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
    blockCode=args['testInput']
    if blockCode == '3403009': # Basia
      dirname = '/tmp/Basia'
      startDate=datetime.datetime.strptime('15082017', "%d%m%Y").date()
      endDate=datetime.datetime.strptime('15082018', "%d%m%Y").date()
      needed = [
        'kumhari',
        'eitam',
        'turbunga',
        'banai',
        'pokta',
        'konbir',
        'mamarla',
        'kaliga',
        'pantha',
      ]
    elif blockCode == '2721003':
      dirname = '/tmp/Jawaja'
      '''
      needed = [
        'किशनपुरा'
        'ब्यावरख्ाास',
        'देलवाडा',
        'काबरा',
        'गोहाना',
        'बडकोचरा',
        'सुरजपुरा',
        'नरबदखेडा',
        'सरवीना',
        #'आसन',
        'अतीतमण्ड',
        'बलाड',
        'बडाखेडा',
        'सुरडिया',
        'नाईकां',
        'जवाजा',
        'नूरी मालदेव',
      ]
      '''
      mapping = [
        '2721003070', # Bar kochra 	बडकोचरा
        '2721003071', # Bada Khera 	बडाखेडा
        '2721003073', # Balar		बलाड
        '2721003074', # Kabra		काबरा
        '2721003082', # Sarveena	सरवीना
        '2721003084', # Suradiya	सुरडिया
        '2721003085', # Surajpura	सुरजपुरा
        '2721003088', # Delwara	  देलवाडा
        '2721003091', # Jawaja		जवाजा
        '2721003092', # Narbad Khera	नरबदखेडा
        '2721003098', # Ateetmand	अतीतमण्ड
        '2721003099', # Gohana		गोहाना
        '2721003094', # Noondri Maldeo	नून्द्री मालदेव
        '2721003093', # Nai Kalan	नाईकलां
        '2721003078', # Kishanpura	किशनपुरा
        '2721003096', # Asan		आसन
        '2721003067', # Beawar Khas	ब्यावरख्ाास        
      ]

      needed = ['Panchayat-' + panchayatCode for panchayatCode in mapping]
      
    elif blockCode == '3406004': # Manika
      dirname = '/tmp/Manika'
      needed = [
        'dundu',
        'donki',
        'kope',
        'badkadih',
        'janho',
        'vishunbandh',
        'rawkikala',
        'barwaiya kala',
        'sinjo',
        'banduwa',
        ]      
    else: # Chhatarpur
      dirname = '/tmp/Chhatarpur'
      transactionStartDate=datetime.datetime.strptime('15042017', "%d%m%Y").date()
      transactionEndDate=datetime.datetime.strptime('15082018', "%d%m%Y").date()      
      needed = [
        'musamdag',
        'kawal',
        'kalapahar',
        'dali',
        'cherain',
        'dinadag',
        'susiganj',
        'kachanpur',
        'rudwa',
      ]
    create_dir(dirname)
    create_dir(dirname+'Aggregate')
    create_dir(dirname+'Villages')
    eachBlock=Block.objects.filter(code=blockCode).first()
    myPanchayats=Panchayat.objects.filter(block=eachBlock) #[:1]
    for eachPanchayat in myPanchayats:
      if eachPanchayat.slug in needed:
      #if eachPanchayat.name in needed:
        logger.info('Create report for Panchayat[%s]' % eachPanchayat)
        #createAPURajendran(logger,eachPanchayat,transactionStartDate,transactionEndDate,'18')
        createAPURajendran(logger,eachPanchayat, dirname)
      else:
        logger.info('Skipping Panchayat[%s]' % eachPanchayat.slug)
        continue
        
    exit(0)
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
