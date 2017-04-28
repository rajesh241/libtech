from bs4 import BeautifulSoup
from datetime import datetime,date,timedelta
import requests
import os
import sys
import re
import time
from customSettings import repoDir,djangoDir,djangoSettings
from customSettings import musterTimeThreshold
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import Q


os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for Downloading Rejected Payments')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-f', '--finyear', help='Financial year for which reports need to be downloaded', required=True)
  parser.add_argument('-c', '--crawlRequirement', help='Download for which type, STAT or FULL ', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  if args['crawlRequirement']:
    crawlRequirement=args['crawlRequirement']
  else:
    crawlRequirement='STAT'
  finyear=args['finyear']
  fullfinyear=getFullFinYear(finyear)
  myBlocks=Block.objects.filter(crawlRequirement=crawlRequirement)[:limit]
  for eachBlock in myBlocks:
    if eachBlock.district.state.stateCode != '02':
      logger.info("BlockName: %s BlockCode: %s " % (eachBlock.name,eachBlock.fullBlockCode))
      reportTypes=["I","R"]
      for rtype in reportTypes:
        url="http://%s/netnrega/FTO/rejection.aspx?lflag=eng&state_code=%s&state_name=%s&district_code=%s&page=d&Block_code=%s&Block_name=%s&district_name=%s&fin_year=%s&typ=%s&linkr=X&" %(eachBlock.district.state.crawlIP,eachBlock.district.state.stateCode,eachBlock.district.state.name,eachBlock.district.fullDistrictCode,eachBlock.fullBlockCode,eachBlock.name,eachBlock.district.name,fullfinyear,rtype)  
        logger.info(url) 
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
