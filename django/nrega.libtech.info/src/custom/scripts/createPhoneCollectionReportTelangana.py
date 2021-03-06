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

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear,savePanchayatReport
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport,Applicant

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-nbc', '--nicBlockCode', help='NIC BlockCode for which the numbster needs to be downloaded', required=True)

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
  blockCode=args['nicBlockCode']
  myPanchayats=Panchayat.objects.filter(block__code=blockCode)[:limit]
  for eachPanchayat in myPanchayats:
    logger.info(eachPanchayat.name)  
    blockName=eachPanchayat.block.slug 
    myApplicants=Applicant.objects.filter(panchayat=eachPanchayat).order_by("tjobcard__group__groupCode","tjobcard__tjobcard")
    outcsv=''
    outcsv+=",GroupCode,GropName,Jobcard,name,headofhousehold,age,gender\n"
    outcsv+="Village,GroupCode,GropName,Jobcard,name\n"
    for eachApplicant in myApplicants:
      if eachApplicant.tjobcard is not None:
        if eachApplicant.tjobcard.group  :
          villageName=eachApplicant.tjobcard.group.village.name
          groupName=eachApplicant.tjobcard.group.groupName
          groupCode=eachApplicant.tjobcard.group.groupCode
        else:
          villageName=''
          groupName=''
          groupCode=''
        #groupCode=eachApplicant.tjobcard.group.groupCode
        outcsv+="%s,%s,%s,%s,%s\n" % (villageName,groupCode,groupName,"~"+eachApplicant.tjobcard.tjobcard,eachApplicant.name)
    filepath="/tmp/chakri/%s/a.csv" % (blockName)
    csvfilename=eachPanchayat.slug+"_phone.csv"
    cmd="mkdir -p %s" %(filepath) 
    logger.info(cmd)
    os.system(cmd)
    with open("/tmp/chakri/"+blockName+"/"+csvfilename,"w") as f:
      f.write(outcsv)
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
