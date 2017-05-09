from bs4 import BeautifulSoup
from datetime import datetime,date,timedelta
import requests
import os
import sys
import re
import time
from random import shuffle
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

from django.contrib.auth.models import User
from nrega.models import State,District,Block,Panchayat,Muster


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing Jobcards')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  myUser=User.objects.filter(username='demo').first()
  myobjs=District.objects.filter(state__isNIC=True)
  if args['limit']:
    limit=args['limit']
  else:
    limit=1
  for eachDistrict in myobjs:
    logger.info(eachDistrict.name)
    myPanchayats=list(Panchayat.objects.filter(block__district__code=eachDistrict.code,crawlRequirement='NONE'))
    shuffle(myPanchayats)
    myPanchayats=myPanchayats[:limit]
    for eachPanchayat in myPanchayats:
      logger.info(eachPanchayat.name)
      eachPanchayat.crawlRequirement="FULL"
      eachPanchayat.save()
      myBlock=eachPanchayat.block
      myBlock.partners.add(myUser)
      myBlock.save()
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
