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
  parser.add_argument('-b', '--blockCode', help='StateCode for which the numbster needs to be downloaded', required=False)

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
  blockCode=args['blockCode']  
  myPanchayats=Panchayat.objects.filter(block__code=blockCode)[:limit]
  for eachPanchayat in myPanchayats:
    logger.info(eachPanchayat.name)
    panchayatName=eachPanchayat.name
    blockName=eachPanchayat.block.name
    districtName=eachPanchayat.block.district.name
    myApplicants=Applicant.objects.filter(panchayat=eachPanchayat)
    outcsv=''
    outcsv+="District,Block,Panchayat,Village,nicJobcard,jobcard,ApplicantNo,Name,FatherHusbandName,HeadOfHousehold,Age,Gender,Caste,gropName,groupCode"
    outcsv+="\n"
    for eachApplicant in myApplicants:
      if eachApplicant.tjobcard:
        tjobcard=eachApplicant.tjobcard.tjobcard
        groupName=eachApplicant.tjobcard.groupName
        groupCode=eachApplicant.tjobcard.groupCode
        logger.info(tjobcard)
      else:
        tjobcard=''
        groupName=''
        groupCode=''
        logger.info("not found")
     
      outcsv+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (districtName,blockName,panchayatName,eachApplicant.village,eachApplicant.jobcard,eachApplicant.tjobcard,str(eachApplicant.jcNo),eachApplicant.name,eachApplicant.fatherHusbandName,eachApplicant.headOfHousehold,str(eachApplicant.age),eachApplicant.gender,eachApplicant.caste,groupName,groupCode)
      outcsv+="\n"
    try:
      outcsv=outcsv.encode("UTF-8")
    except:
      outcsv=outcsv
     
    csvfilename=eachPanchayat.slug+"_applicants.csv"
    csvfilepath="/tmp/"+blockName+"/"
    cmd="mkdir -p %s " %(csvfilepath) 
    logger.info(cmd)
    os.system(cmd)
    with open(csvfilepath+csvfilename,"wb") as f:
      f.write(outcsv) 
    
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
