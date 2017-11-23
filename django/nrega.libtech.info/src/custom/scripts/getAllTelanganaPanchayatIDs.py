from bs4 import BeautifulSoup
import requests
import os
import sys
import re
import urllib.request
import django
from django.core.wsgi import get_wsgi_application

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
from wrappers.logger import loggerFetch
sys.path.append(djangoDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
# This is so Django knows where to find stuff.
# This is so my local_settings.py gets loaded.
django.setup()
from nrega.models import State,District,Block,Panchayat




def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
 


  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
