from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,startFinYear,panchayatCrawlThreshold,panchayatRetryThreshold
from crawlFunctions import crawlPanchayat,parseMuster
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
  parser.add_argument('-mid', '--musterID', help='Muster ID', required=False)
  parser.add_argument('-p', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-pm', '--processMusters', help='ProcessMusters', required=False,action='store_const', const=1)
  parser.add_argument('-cp', '--crawlPanchayat', help='crawlPanchayat', required=False,action='store_const', const=1)
  parser.add_argument('-rm', '--resetMusters', help='Reset Musters and set Processed to zero', required=False,action='store_const', const=1)
  parser.add_argument('-e', '--execute', help='Manage Panchayat Crawl Queue', required=False,action='store_const', const=1)
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
  if args['resetMusters']:
    panchayatCode=args['panchayatCode']
    myMusters=Muster.objects.filter(panchayat__code=panchayatCode)
    for eachMuster in myMusters:
      eachMuster.isProcessed=False
      logger.info(eachMuster.id)
      eachMuster.save()
  if args['crawlPanchayat']:
    panchayatCode=args['panchayatCode']
    eachPanchayat=Panchayat.objects.filter(code=panchayatCode).first()
    crawlPanchayat(logger,eachPanchayat,startFinYear)
 
  if args['processMusters']:
    logger.info("Goiong to Debug Musers")
    mid=args['musterID']
    eachMuster=Muster.objects.filter(id=mid).first()
    logger.info(eachMuster)
    parseMuster(logger,eachMuster)
   
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
