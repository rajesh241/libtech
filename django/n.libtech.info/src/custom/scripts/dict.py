from bs4 import BeautifulSoup
import requests
import os
import sys
import re
import urllib.request
import json
import django
from django.core.wsgi import get_wsgi_application
from django.db.models import Count,Sum
from django.db import transaction

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings
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
from nrega.models import State,District,Block,Panchayat,PaymentInfo,LibtechTag,CrawlQueue,Jobcard,Task


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-t', '--test', help='Test Function can be used to run any script', required=False, action='store_const', const=1)
  parser.add_argument('-sp', '--selectPanchayats', help='Select Panchayats Randomly', required=False, action='store_const', const=1)
  parser.add_argument('-lock', '--lock', help='Select Panchayats Randomly', required=False, action='store_const', const=1)
  parser.add_argument('-ti', '--testInput', help='Log level defining verbosity', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-s', '--stateCode', help='stateCode', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['lock']:
    with transaction.atomic():
      objs = Task.objects.select_for_update().filter(isComplete=True)[:1]
      for obj in objs:
        logger.info(obj.id)
      objs = Task.objects.select_for_update().filter(isComplete=True)[:1]
      for obj in objs:
        logger.info(obj.id)
  if args['test']:
    d=dict()

    logger.info("Creating a Dictionary")
    pids=["253261","159361"]
    for pid in pids:
      myPanchayats=Panchayat.objects.filter(id=pid)
      for eachPanchayat in myPanchayats:
        p=dict()
        logger.info(eachPanchayat.name)
        a=[]
        a.append(eachPanchayat.id)
        a.append(eachPanchayat.block.district.name)
        a.append(eachPanchayat.block.district.state.name)
        logger.info(a)
        b=[]
        b.append(eachPanchayat.id)
        p[eachPanchayat.block.name]=a
        p['ptids']=b
        d[eachPanchayat.name]=p
    logger.info(d)
    with open('/tmp/panchayats.json', 'w') as f:
      json.dump(d, f, ensure_ascii=False)
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
