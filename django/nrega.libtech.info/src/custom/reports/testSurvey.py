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
  parser.add_argument('-r', '--readJobcards', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-g', '--generate', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-d', '--deleteTag', help='Make the browser visible', required=False, action='store_const', const=1)

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
  surveyDoneTag=LibtechTag.objects.filter(name="Base Line Survey Main Done").first()
  surveyDoneTagArray=LibtechTag.objects.filter(name="Base Line Survey Main Done")
  q5Tag=LibtechTag.objects.filter(name="Base Line Survey Q5 Q64").first()
  if args['deleteTag']:
    blockCodes=['3614008','3614007','3614006','3614005'] 
    blockCodes=['3614006','3614005'] 
    for inblock in blockCodes:
      myBlock=Block.objects.filter(code=inblock).first()
      blockName=myBlock.slug
      i=0
      total=0
      myPanchayats=Panchayat.objects.filter(block=myBlock)
      for eachPanchayat in myPanchayats:
        logger.info(i)
        i=i+1
        myJobcards=Jobcard.objects.filter(panchayat=eachPanchayat,libtechTag__in=surveyDoneTagArray)
        for eachJobcard in myJobcards:
          eachJobcard.libtechTag.remove(surveyDoneTag)
          eachJobcard.save()

  if args['generate']:
    blockCodes=['3614008','3614007','3614006','3614005'] 
    blockCodes=['3614006','3614005'] 
    outcsv=''
    outcsv+="blockName,panchayatName,toBeSurveyed,mainDone,Q5Done\n"
    for inblock in blockCodes:
      myBlock=Block.objects.filter(code=inblock).first()
      blockName=myBlock.slug
      i=0
      total=0
      myPanchayats=Panchayat.objects.filter(block=myBlock)
      for eachPanchayat in myPanchayats:
        logger.info(i)
        i=i+1
        myJobcards=Jobcard.objects.filter(panchayat=eachPanchayat,libtechTag__in=surveyDoneTagArray)
        totalSurveyDone=str(len(myJobcards))
        outcsv+="%s,%s,%s,%s,%s\n" % (blockName,eachPanchayat.slug,str(total),totalSurveyDone,"")
    with open("/tmp/surveyReport.csv","w") as f:
      f.write(outcsv)  


  if args['readJobcards']:  
    with open('response_jobcards.csv') as fp:
      for line in fp:
        line=line.lstrip().rstrip()
        if line != '':
          print(line)
          lineArray=line.split(",")
          jobcard=lineArray[0]
          jobcard1=lineArray[1]
          myJobcard=Jobcard.objects.filter(tjobcard=jobcard).first()
          if myJobcard is not None:
            logger.info("Found the Jobcard")
            myJobcard.libtechTag.add(surveyDoneTag)
            myJobcard.save() 
          myJobcard=Jobcard.objects.filter(tjobcard=jobcard1).first()
          if myJobcard is not None:
            logger.info("Found the Jobcard")
            myJobcard.libtechTag.add(surveyDoneTag)
            myJobcard.save() 
 
    
  
          

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
