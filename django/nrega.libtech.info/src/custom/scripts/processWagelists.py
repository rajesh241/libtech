from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
import time
from customSettings import repoDir,djangoDir,djangoSettings

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getjcNumber
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import F
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Applicant,Muster,WorkDetail,Wagelist,FTO

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This Script is for Processing Muster')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)

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
  stateCode=args['stateCode']
  if stateCode is not None:
    logger.info("StateCode is %s" % stateCode)
    myWagelists=Wagelist.objects.filter(isDownloaded=1,isProcessed=0,block__district__state__code=stateCode)[:limit] 
  else:
    myWagelists=Wagelist.objects.filter(isDownloaded=1,isProcessed=0)[:limit]

  for eachWagelist in myWagelists:
    logger.info("Wage list id: %s, wagelistno : %s " % (str(eachWagelist.id),eachWagelist.wagelistNo))
#  myMusters=Muster.objects.filter(id=10924) 
    myhtml=eachWagelist.wagelistFile.read()
    stateShortCode=eachWagelist.block.district.state.stateShortCode
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    isComplete=True
    mytable=htmlsoup.find('table',id="myTable")
    rows = mytable.findAll('tr')
    for row in rows:
      cols=row.findAll('td')
      if "WageList No" in str(row):
        logger.info("Skipping this row")
        for i,col in enumerate(cols):
          if col.text.lstrip().rstrip() == "FTO No.":
            ftoIndex=i
        logger.info(ftoIndex)
      else:
        ftoNo=cols[ftoIndex].text.lstrip().rstrip()
        logger.info(ftoNo)
        if stateShortCode not in ftoNo:
          isComplete=False
        else:
          logger.info("FTO Number seems to be correct")
          matchedFTO=FTO.objects.filter(ftoNo=ftoNo,block=eachWagelist.block,finyear=eachWagelist.finyear).first()
          if matchedFTO is not None:
            logger.info("FTO Found")
          else:
            FTO.objects.create(ftoNo=ftoNo,block=eachWagelist.block,finyear=eachWagelist.finyear)
            logger.info("Created FTO")
    eachWagelist.isProcessed=1
    logger.info("Value of is Complete is %s " % str(isComplete))
    eachWagelist.isComplete=isComplete
    eachWagelist.save()

  logger.info("...END PROCESSING") 
  exit(0)

if __name__ == '__main__':
  main()
