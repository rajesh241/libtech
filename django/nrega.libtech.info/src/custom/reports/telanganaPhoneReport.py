from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
sys.path.insert(0, "./../scripts")
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

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport,Jobcard,LibtechTag,PaymentDetail,Worker,Applicant
from django.db.models import Count,Sum,Q

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-f', '--finyear', help='Financial year for which data needs to be crawld', required=True)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-p', '--panchayatCode', help='panchaytCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-b', '--blockCode', help='panchaytCode for which the numbster needs to be downloaded', required=False)

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
  surveyTag=LibtechTag.objects.filter(name="baseLineSurvey")
  replacementTag=LibtechTag.objects.filter(name="baseLineSurveyReplacement")
  
  inblock=args['blockCode']
  blockCodes=['3614008','3614007','3614006','3614005']
 # if inblock is not None:
  blockCodes=['3614006']
  for inblock in blockCodes:
    myBlock=Block.objects.filter(code=inblock).first()
    blockName=myBlock.slug
    outcsv=''
    jobcardcsv=''
    jobcardcsv+="block,panchayat,nicJobcard,tildaJobcard,tjobcard\n"
    outcsv+="Panchayat,JobcardID,jobcard,type,srNo,applicantName,daysWorked\n"
    myPanchayats=Panchayat.objects.filter(block__code=inblock)[:limit]
    i=0
    for eachPanchayat in myPanchayats:
      i=i+1
      panchayatcsv=""
      panchayatcsv+="Block,%s, ,Panchayat,%s\n\n" % (blockName,eachPanchayat.slug) 
      panchayatcsv+="srNo,habitation,gropName,jobcard,caste,surname,headOfHouseHold,phone\n"
      logger.info(eachPanchayat.name)
      myJobcards=Jobcard.objects.filter( panchayat=eachPanchayat).order_by("-group__groupName")
      j=0
      phone=''
      for eachJobcard in myJobcards:
        j=j+1
        logger.info(j)
        tjobcard="~"+eachJobcard.tjobcard
        surname=eachJobcard.surname
        caste=eachJobcard.caste
        villageName=''
        groupName=''
        headOfHousehold=eachJobcard.headOfHousehold
        if eachJobcard.village is not None:
          villageName=eachJobcard.village.name
        if eachJobcard.group is not None:
          groupName=eachJobcard.group.groupName
        panchayatcsv+="%s,%s,%s,%s,%s,%s,%s,%s\n" % (str(j),villageName,groupName,tjobcard,caste,surname,headOfHousehold,phone)
      with open("/tmp/reports1/%s_%s.csv" % (blockName,eachPanchayat.slug) , "w") as f:
        f.write(panchayatcsv)
#    with open("/tmp/reports/%s.csv" % blockName,"w") as f:
#      f.write(outcsv)
        
          

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
