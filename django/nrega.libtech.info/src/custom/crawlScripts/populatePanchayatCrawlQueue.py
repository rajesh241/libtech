from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,startFinYear,panchayatCrawlThreshold,panchayatRetryThreshold,telanganaStateCode
from crawlFunctions import crawlPanchayat
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
  parser.add_argument('-pc', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-bc', '--blockCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-p', '--priority', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-a', '--add', help='Add toPanchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-e', '--execute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-af', '--augustHearing', help='August Hearing', required=False,action='store_const', const=1)
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
  if args['add']:
    priority=args['priority']
    panchayatCode=args['panchayatCode']
    blockCode=args['blockCode']
    if blockCode is not None:
      myPanchayats=Panchayat.objects.filter(block__code=blockCode)
      for eachPanchayat in myPanchayats:
        PanchayatCrawlQueue.objects.create(panchayat=eachPanchayat,priority=priority)
    else:
      eachPanchayat=Panchayat.objects.filter(code=panchayatCode).first()
      PanchayatCrawlQueue.objects.create(panchayat=eachPanchayat,priority=priority)
  if args['test']:
    priority=args['priority']
    myPanchayats=Panchayat.objects.filter(crawlRequirement="FULL",block__district__state__code=telanganaStateCode)
    for eachPanchayat in myPanchayats:
      logger.info(eachPanchayat.name)
      PanchayatCrawlQueue.objects.create(panchayat=eachPanchayat,priority=priority)
      
  if args["augustHearing"]:
    startFinYear='18' 
    stateCode=args['stateCode']
    logger.info("Populating the Queue for August Hearing") 
    myLibtechTag=LibtechTag.objects.filter(name="August 2017 Hearing")
    myPanchayats=Panchayat.objects.filter(block__district__state__code=stateCode,libtechTag__in=myLibtechTag)
    i=0
    for eachPanchayat in myPanchayats:
      i=i+1
      logger.info("crawl %s Panchayat %s Block %s District %s State %s" % (str(i),eachPanchayat.name,eachPanchayat.block.name,eachPanchayat.block.district.name,eachPanchayat.block.district.state.name))
      PanchayatCrawlQueue.objects.create(panchayat=eachPanchayat,priority=5,startFinYear=startFinYear)
      logger.info("Putting The panchayat in the CrawlQueue")
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
