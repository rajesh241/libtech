from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
from customSettings import repoDir,djangoDir,djangoSettings

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import table2csv,stripTableAttributes,htmlWrapperLocal,getFullFinYear,savePanchayatReport
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,PanchayatReport
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will Download the delayed Payment list')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-f', '--finyear', help='Financial year for which data needs to be crawld', required=True)
  parser.add_argument('-s', '--stateCode', help='State for which the delayed payment report needs to be crawld', required=False)

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
  finyear=args['finyear']
  fullfinyear=getFullFinYear(finyear)
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
#  stateCode=args['stateCode']
  stateCodes=['33','34','16','27','24','15','18','35']
  stateCodes=['16','31','05','17']
  stateCodes=['33']
  for stateCode in stateCodes:
    myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__stateCode=stateCode)
    for eachPanchayat in myPanchayats:
      myBlock=eachPanchayat.block
      blockURL='http://%s/netnrega/state_html/delay_comp.aspx?rb_mon=Y&page=B&state_name=%s&state_code=%s&district_name=%s&district_code=%s&block_name=%s&block_code=%s&fin_year=2016-2017&source=national&Digest=N076k7Ek7sFXB+fG7DB+Hg' %(myBlock.district.state.crawlIP,myBlock.district.state.name,myBlock.district.state.stateCode,myBlock.district.name,myBlock.district.fullDistrictCode,myBlock.name,myBlock.fullBlockCode)
      logger.info(blockURL)
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
