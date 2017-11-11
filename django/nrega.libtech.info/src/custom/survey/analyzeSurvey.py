from bs4 import BeautifulSoup
import csv
from datetime import datetime,date
import requests
import os
import sys
import re
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
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

from nrega.models import State,District,Block,Panchayat,Muster,WorkDetail,PanchayatReport,Jobcard,LibtechTag,PaymentDetail,Worker,Applicant,SurveyJobcard
from django.db.models import Count,Sum,Q

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-e', '--enumerate', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-r', '--report', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-d', '--deleteTag', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-m', '--mark', help='Mark that the survey is done', required=False, action='store_const', const=1)
  parser.add_argument('-o', '--reportTag', help='Mark that the survey is done', required=False, action='store_const', const=1)

  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
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

  if args['enumerate']:
    myJobcards=Jobcard.objects.filter(isBaselineSurvey=True)
    for eachJobcard in myJobcards:
      logger.info(eachJobcard.tjobcard)
      mySurveyJobcard=SurveyJobcard.objects.filter(jobcard=eachJobcard,isBaselineSurvey=True).first()
      if mySurveyJobcard is None:
        logger.info("Does not Exists")
        SurveyJobcard.objects.create(jobcard=eachJobcard,isBaselineSurvey=True)
    myJobcards=Jobcard.objects.filter(isBaselineReplacement=True)
    for eachJobcard in myJobcards:
      logger.info(eachJobcard.tjobcard)
      mySurveyJobcard=SurveyJobcard.objects.filter(jobcard=eachJobcard,isBaselineReplacement=True).first()
      if mySurveyJobcard is None:
        logger.info("Does not Exists")
        SurveyJobcard.objects.create(jobcard=eachJobcard,isBaselineReplacement=True)

  if args['mark']:
    filename="/tmp/surveyAnanlysis_main_8oct.csv"
    with open(filename, 'r') as f:
       reader = csv.reader(f, delimiter=',')
       j=0
       for row in reader:
        j=j+1
        status=row[8]
        logger.info(row[1])
        logger.info(status)
        if (status != "incorrectJobcard") and (status != 'dummy'):
          try:
            dateObject = datetime.strptime(row[1], '%m/%d/%y %H:%M')
          except:
            dateObject = datetime.strptime(row[1], '%m/%d/%Y %H:%M:%S')
          tjobcard=row[5]
          logger.info(tjobcard)
          mySurveyJobcard=SurveyJobcard.objects.filter(jobcard__tjobcard=tjobcard).first()
          mySurveyJobcard.isMainSurveyDone=True
          mySurveyJobcard.mainSurveyIndex=row[0]
          mySurveyJobcard.mainTimeStamp=dateObject
          mySurveyJobcard.save()

  if args['report']:
    outcsv=''
    outcsv+="blockName,panchayatName,tjobcard,surveyType,blank,mainSurveyDone,mainIndex,mainTimeStamp,q5SurveyDone,q5Index,q5TimeStamp\n"
    surveyJobcards=SurveyJobcard.objects.all()
    for eachJobcard in surveyJobcards:
      blockName=eachJobcard.jobcard.panchayat.block.slug
      panchayatName=eachJobcard.jobcard.panchayat.slug
      tjobcard=eachJobcard.jobcard.tjobcard
      if eachJobcard.isBaselineSurvey is True:
        surveyType='Survey'
      else:
        surveyType='Replacement'
      mainSurveyDone=eachJobcard.isMainSurveyDone
      mainSurveyIndex=eachJobcard.mainSurveyIndex
      mainSurveyTimeStamp=eachJobcard.mainTimeStamp 
      q5SurveyDone=eachJobcard.isQ5SurveyDone
      q5SurveyIndex=eachJobcard.q5SurveyIndex
      q5SurveyTimeStamp=eachJobcard.q5TimeStamp 
      outcsv+="%s,%s,%s,%s,,%s,%s,%s,%s,%s,%s\n" % (blockName,panchayatName,tjobcard,surveyType,str(mainSurveyDone),str(mainSurveyIndex),str(mainSurveyTimeStamp),str(q5SurveyDone),str(q5SurveyIndex),str(q5SurveyTimeStamp))
    with open("/tmp/surveReport.csv","w") as f:
      f.write(outcsv)

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
