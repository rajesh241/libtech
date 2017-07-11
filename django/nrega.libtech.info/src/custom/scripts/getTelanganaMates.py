from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
from customSettings import repoDir,djangoDir,djangoSettings

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getjcNumber,getCurrentFinYear
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import F,Q,Count
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Applicant,PanchayatReport,Village,VillageReport,TelanganaJobcard,TelanganaSSSGroup

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This script would parse the worker list from MIS')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1

  myGroups=TelanganaSSSGroup.objects.all()[:limit]
  for eachGroup in myGroups:
    groupName=eachGroup.groupName
    villageCode=eachGroup.village.tcode
    villageName=eachGroup.village.name
    groupCode=eachGroup.groupCode
    groupID=villageCode+groupCode[1:]
    logger.info("GroupName: %s, villageName: %s villageCode: %s, GropCode: %s " % (groupName,villageName,villageCode,groupCode))
    url="http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=SSSanghaRH&actionVal=StatusofSSS&id=%s$&type=-1&type1=null&yearType=&Linktype=null&finYear=" % groupID
    logger.info(url)
#  myobjs=TelanganaJobcard.objects.filter(village__panchayat__block__code="3614005").values("groupName","groupCode","village__tcode").annotate(dcount=Count('pk'))[:limit]
 
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
