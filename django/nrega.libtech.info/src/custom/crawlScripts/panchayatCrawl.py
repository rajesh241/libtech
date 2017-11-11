from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,startFinYear
from crawlFunctions import crawlPanchayat
from crawlFunctions import saveJobcardRegister,processJobcardRegister,downloadMusters,processMusters,downloadPanchayatStat,processPanchayatStat
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,LibtechTag

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
  parser.add_argument('-sf', '--startFinYear', help='From which financial year data needs to be crawled default is 2015-2016', required=False)
  parser.add_argument('-p', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-cr', '--crawlRequirement', help='Kindly put the tag of crawlRequiremtn that panchayats are tagged with, by default it will do it for panchayats which are tagged with crawlRequirement of FULL', required=False)

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
  if args['crawlRequirement']:
    crawlRequirement=args['crawlRequirement']
  else:
    crawlRequirement="FULL"
  startFinYear='16' 
  endFinYear=getCurrentFinYear()
  
  eachPanchayat=Panchayat.objects.filter(code="2103003257").first()
  eachPanchayat=Panchayat.objects.filter(code="3406007003").first()
  crawlPanchayat(logger,eachPanchayat,startFinYear)

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
