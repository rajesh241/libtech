from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,startFinYear,panchayatCrawlThreshold,panchayatRetryThreshold,telanganaStateCode,panchayatAttemptRetryThreshold,apStateCode,crawlRetryThreshold
from crawlFunctions import crawlPanchayat,crawlPanchayatTelangana,libtechCrawler
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

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag,PanchayatCrawlQueue,CrawlQueue

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
  parser.add_argument('-qid', '--qid', help='Queue Id for which this needs to be run', required=False)
  parser.add_argument('-bc', '--blockCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-m', '--manage', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-e', '--execute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-p', '--populate', help='Populate CrawlQueue', required=False,action='store_const', const=1)
  parser.add_argument('-se', '--singleExecute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-d', '--debug', help='Debug Panchayat Crawl Queue', required=False,action='store_const', const=1)
  parser.add_argument('-t', '--test', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)

  args = vars(parser.parse_args())
  return args
    
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))

  if args['populate']:
    panchayatCode=args['panchayatCode']
    blockCode=args['blockCode']
    if panchayatCode is not None:
      eachPanchayat=Panchayat.objects.filter(code=panchayatCode).first()
      CrawlQueue.objects.create(panchayat=eachPanchayat)
    elif blockCode is not None:
      eachBlock=Block.objects.filter(code=blockCode).first()
      CrawlQueue.objects.create(block=eachBlock,priority=500)

  if args['execute']:
    stage=args['step']
    limit=args['limit']
    qid=args['qid']
    if qid is not None:
      libtechCrawler(logger,stage,qid=qid)
    else:
      libtechCrawler(logger,stage)

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
