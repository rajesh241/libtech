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
from django.db.models import F,Q
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Applicant,PanchayatReport,Village,VillageReport,TelanganaJobcard

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
  myVillages=Village.objects.all()[:limit]
  for eachVillage in myVillages:
    logger.info(eachVillage.name)
    stateName=eachVillage.panchayat.block.district.state.name
    districtName=eachVillage.panchayat.block.district.name
    blockName=eachVillage.panchayat.block.name
    blockTCode=eachVillage.panchayat.block.tcode
    logger.info(blockTCode)
    panchayatName=eachVillage.panchayat.name
    villageName=eachVillage.name
    eachPanchayat=eachVillage.panchayat
    reportType="telJobcardRegisterHTML"
    curfinyear=getCurrentFinYear()
     
    villageReport=VillageReport.objects.filter(reportType=reportType,finyear=curfinyear,village=eachVillage).first()
    if villageReport is not None:
      logger.info("Panchayat Report Exists")
      myhtml=villageReport.reportFile.read()  
      htmlsoup=BeautifulSoup(myhtml,"html.parser")
      myTable=htmlsoup.find('table',id="myTable")
      if myTable is not None:
        logger.info("Table FOund")
        rows=myTable.findAll('tr')
        for row in rows:
          cols=row.findAll('td')
          if len(cols) > 0:
            tjobcard=cols[2].text.lstrip().rstrip()
            if len(tjobcard) == 18 and tjobcard.isdigit():
              applicantNo=int(cols[3].text.lstrip().rstrip())
              allNamesArray=cols[4].text.lstrip().rstrip().split("-")
              groupArray=cols[1].text.lstrip().rstrip().split("-")
              applicantName=allNamesArray[1]
              jcNumber=int(tjobcard[-6:])
              groupName=groupArray[0]
              groupCode=groupArray[1]

              myTJobcard=TelanganaJobcard.objects.filter(tjobcard=tjobcard).first()
              if myTJobcard is None:
                TelanganaJobcard.objects.create(tjobcard=tjobcard,groupName=groupName,groupCode=groupCode)
              myTJobcard=TelanganaJobcard.objects.filter(tjobcard=tjobcard).first()

              myApplicant=Applicant.objects.filter(panchayat=eachPanchayat,jcNo=jcNumber,applicantNo=applicantNo,name=applicantName)
              if len(myApplicant) != 1:
                logger.info(str(applicantNo)+applicantName+tjobcard+"-"+str(jcNumber)) 
              else:
                eachApplicant=myApplicant.first()
                eachApplicant.tjobcard=myTJobcard
                eachApplicant.save()

    logger.info(eachVillage.name)
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
