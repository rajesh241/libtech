from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,startFinYear,panchayatCrawlThreshold,panchayatRetryThreshold,telanganaStateCode
from crawlFunctions import crawlPanchayat,crawlPanchayatTelangana
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q,Sum,Count
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag,PanchayatCrawlQueue

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='State for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-sf', '--startFinYear', help='From which financial year data needs to be crawled default is 2015-2016', required=False)
  parser.add_argument('-step', '--step', help='Step for which the script needs to run', required=False)
  parser.add_argument('-p', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-m', '--manage', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-e', '--execute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-d', '--debug', help='Debug Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-t', '--test', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)

  args = vars(parser.parse_args())
  return args


def main():
  alwaysTag=LibtechTag.objects.filter(name="Always")
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  startFinYear='16' 
  
  if args['manage']:
    logger.info("Going to Manage the Panchayat Crawl Queue")
    #We will Populate the Panchayat Queue    
    myPanchayats=Panchayat.objects.filter( Q(crawlRequirement="FULL",lastCrawlDate__isnull=True,block__district__state__isNIC=True) | Q (crawlRequirement="FULL",lastCrawlDate__lt = panchayatCrawlThreshold,block__district__state__isNIC=True))
    for eachPanchayat in myPanchayats:
      logger.info("Starting to crawl Panchayat %s Block %s District %s State %s" % (eachPanchayat.name,eachPanchayat.block.name,eachPanchayat.block.district.name,eachPanchayat.block.district.state.name))
      myPanchayatCrawlQueue=PanchayatCrawlQueue.objects.filter(panchayat=eachPanchayat,isComplete=False).first()
      if myPanchayatCrawlQueue is None:
        PanchayatCrawlQueue.objects.create(panchayat=eachPanchayat)
        logger.info("Putting The panchayat in the CrawlQueue")
     
  if args['test']:
    myLibtechTagArray=LibtechTag.objects.filter(slug="august-2017-hearing")
    myPanchayats=Panchayat.objects.filter(libtechTag__in = myLibtechTagArray).values("block__district__state__slug").annotate(dcount=Count('pk'))
    for eachobj in myPanchayats:
      logger.info(eachobj["block__district__state__slug"])
      stateSlug=eachobj["block__district__state__slug"]
      eachPanchayat=Panchayat.objects.filter(libtechTag__in = myLibtechTagArray,block__district__state__slug=stateSlug).first()
      logger.info("Starting to crawl Panchayat %s Block %s District %s State %s" % (eachPanchayat.name,eachPanchayat.block.name,eachPanchayat.block.district.name,eachPanchayat.block.district.state.name))
      myPanchayatCrawlQueue=PanchayatCrawlQueue.objects.filter(panchayat=eachPanchayat,isComplete=False).first()
      if myPanchayatCrawlQueue is None:
        PanchayatCrawlQueue.objects.create(panchayat=eachPanchayat,priority=5)
        logger.info("Putting The panchayat in the CrawlQueue")
      
       
  if args['execute']:
    if args['debug']:
      panchayatCode=args['panchayatCode']
      curQueue=PanchayatCrawlQueue.objects.filter(panchayat__code=panchayatCode)[:1]
      step=int(args['step'])
    elif args['step']:
      step=int(args['step'])
      curStep=step-1
      #curQueue=PanchayatCrawlQueue.objects.filter( Q(isComplete=False,isError=False,step=) | Q(isError=True,isComplete=False,crawlStartDate__lt=panchayatRetryThreshold) ).order_by("-priority","created")[:limit]
      curQueue=PanchayatCrawlQueue.objects.filter( Q(isComplete=False,isError=False,status=curStep) | Q(isError=True,isComplete=False,status=curStep,crawlAttemptDate__lt=panchayatRetryThreshold) ).order_by("-priority","crawlAttemptDate","created")[:limit]
    else:
      curQueue=PanchayatCrawlQueue.objects.filter( Q(isComplete=False,isError=False) | Q(isError=True,isComplete=False,crawlStartDate__lt=panchayatRetryThreshold) ).order_by("-priority","created")[:limit]
      step=None
    for obj in curQueue:
      qid=obj.id
      obj.crawlAttemptDate=timezone.now()
      if obj.panchayat.block.district.state.isNIC == False:
        if obj.panchayat.block.district.state.code == telanganaStateCode:
          crawlPanchayatTelangana(logger,qid,step)
        else:
          obj.isError=True
          obj.save()
      logger.info(qid)
      if obj.panchayat.block.district.state.isNIC == True:
        logger.info("Starting to Crawl Panchayat %s " % str(qid))
        crawlPanchayat(logger,qid,step)
          
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
