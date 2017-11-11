from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getjcNumber,getCurrentFinYear,correctDateFormat
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import F,Q
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Applicant,PanchayatReport,Jobcard,LibtechTag,Worker,Village

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This script would parse the worker list from MIS')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-s', '--stateCode', help='State for which the delayed payment report needs to be crawld', required=False)
  parser.add_argument('-p', '--panchayatCode', help='Panchayat for which the delayed payment report needs to be crawld', required=False)
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
  reportType="applicationRegister"
  alwaysTag=LibtechTag.objects.filter(name="Always")
  curfinyear=getCurrentFinYear() 
  stateCode=args['stateCode']
  panchayatCode=args['panchayatCode']
  if panchayatCode is not None:
    myPanchayats=Panchayat.objects.filter(code=panchayatCode)
  elif stateCode is not None:
    myPanchayats=Panchayat.objects.filter(block__district__state__code=stateCode,libtechTag__in=alwaysTag)
    #myPanchayats=Panchayat.objects.filter( Q(applicationRegisterCrawlDate__gt = F('applicationRegisterProcessDate')) | Q(applicationRegisterCrawlDate__isnull=False,applicationRegisterProcessDate__isnull=True,block__district__state__code=stateCode)   ).order_by("-code")[:limit]
  else:
    myPanchayats=Panchayat.objects.filter( Q  (  libtechTag__in=alwaysTag ) & (Q(applicationRegisterCrawlDate__gt = F('applicationRegisterProcessDate')) | Q(applicationRegisterCrawlDate__isnull=False,applicationRegisterProcessDate__isnull=True) )  ).order_by("-code")[:limit]
  for eachPanchayat in myPanchayats:
    logger.info(eachPanchayat.name+","+eachPanchayat.code)
    panchayatReport=PanchayatReport.objects.filter(reportType=reportType,finyear=curfinyear,panchayat=eachPanchayat).first()
    if panchayatReport is not None:
      logger.info("Panchayat Report Exists")
      myhtml=panchayatReport.reportFile.read()  
      logger.info("Read the HTML")
      htmlsoup=BeautifulSoup(myhtml,"lxml")
      myTable=htmlsoup.find('table',id="myTable")
      jobcardPrefix=eachPanchayat.block.district.state.stateShortCode+"-"
      logger.info(jobcardPrefix)
      if myTable is not None:
        logger.info("Found the table")
        rows=myTable.findAll('tr')
        headOfHousehold=''
        applicantNo=0
        fatherHusbandName=''
        village=''
        for row in rows:
          if "Villages : " in str(row):
            logger.info("Village Name Found")
            cols=row.findAll('td')
            villagestr=cols[0].text.lstrip().rstrip()
            villageName=villagestr.replace("Villages :" ,"").lstrip().rstrip()
            logger.info(villageName)
            myVillage=Village.objects.filter(panchayat=eachPanchayat,name=villageName).first()
            if myVillage is None:
              Village.objects.create(panchayat=eachPanchayat,name=villageName)
            myVillage=Village.objects.filter(panchayat=eachPanchayat,name=villageName).first()

          if jobcardPrefix in str(row):
            isDeleted=False
            isDisabled=False
            isMinority=False
            cols=row.findAll('td')
            rowIndex=cols[0].text.lstrip().rstrip()
            jobcard=cols[9].text.lstrip().rstrip().split(",")[0]
            if len(cols[9].text.lstrip().rstrip().split(",")) > 1:
              issueDateString=cols[9].text.lstrip().rstrip().split(",")[1]
            else:
              issueDateString=''
            gender=cols[6].text.lstrip().rstrip()
            age=cols[7].text.lstrip().rstrip()
            applicationDateString=cols[8].text.lstrip().rstrip()
            remarks=cols[10].text.lstrip().rstrip()
            disabledString=cols[11].text.lstrip().rstrip()
            minorityString=cols[12].text.lstrip().rstrip()
            name=cols[4].text.lstrip().rstrip()
            logger.info("Processing %s - %s " % (jobcard,name))
            issueDate=correctDateFormat(issueDateString)
            applicationDate=correctDateFormat(applicationDateString)
            if cols[1].text.lstrip().rstrip() != '':
              headOfHousehold=cols[1].text.lstrip().rstrip()
              caste=cols[2].text.lstrip().rstrip()
              applicantNo=1
              fatherHusbandName=cols[5].text.lstrip().rstrip()
              #Gather Jobcard Replated Info
              myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
              if myJobcard is None:
                Jobcard.objects.create(jobcard=jobcard,panchayat=eachPanchayat)
              myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
              myJobcard.jcNo=getjcNumber(jobcard)
              myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
              myJobcard.caste=caste
              myJobcard.headOfHousehold=headOfHousehold
              myJobcard.village=myVillage
              myJobcard.issueDate=issueDate
              myJobcard.applicantDate=applicationDate
              myJobcard.save()  
            else:
              applicantNo=applicantNo+1
            if '*' in name:
              isDeleted=True
            if disabledString == 'Y':
              isDisabled=True
            if minorityString == 'Y':
              isMinority=True
            name=name.rstrip('*')
            myWorker=Worker.objects.filter(jobcard=myJobcard,name=name).first()
            if myWorker is None:
              Worker.objects.create(jobcard=myJobcard,name=name,applicantNo=applicantNo)
            myWorker=Worker.objects.filter(jobcard=myJobcard,name=name).first()
            logger.info(applicantNo)
            myWorker.applicantNo=applicantNo
            myWorker.gender=gender
            myWorker.age=age
            myWorker.fatherHusbandName=fatherHusbandName
            myWorker.isDeleted=isDeleted
            myWorker.isDisabled=isDisabled
            myWorker.isMinority=isMinority
            myWorker.remarks=remarks
            myWorker.save() 
           
            
          
              #logger.info("Jobcard Deleted")
              #logger.info("%s-%s" % (str(applicantNo),headOfHousehold))
 
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
