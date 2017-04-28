from bs4 import BeautifulSoup
from datetime import datetime,date,timedelta
import requests
import os
import sys
import re
import time
from customSettings import repoDir,djangoDir,djangoSettings
from customSettings import musterTimeThreshold
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import Q


os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing Jobcards')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args

def validateMusterHTML(muster,myhtml):
  error=None
  musterTable=None
  musterSummaryTable=None
  jobcardPrefix=muster.block.district.state.stateShortCode+"-"
  if (jobcardPrefix in myhtml):
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if muster.workCode in str(table):
        musterSummaryTable=table
    if musterSummaryTable is None:
      error="Muster Summary Table not found"
    musterTable=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
    if musterTable is None:
      error="Muster Table not found"
  else:
    error="Jobcard Prefix not found"
  return error,musterTable,musterSummaryTable

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])

  url="http://nrega.nic.in/netnrega/sthome.aspx"
  driver.get(url)
  myMusters=Muster.objects.filter( Q(isDownloaded=False) | Q(musterDownloadAttemptDate__lt = musterTimeThreshold,isComplete=0) )[:limit]
  for eachMuster in myMusters:
    logger.info(eachMuster.musterURL)  
    logger.info("Processing musterNo: %s FullblockCode: %s " % (eachMuster.musterNo,eachMuster.block.fullBlockCode))
    driver.get(eachMuster.musterURL)
    driver.get(eachMuster.musterURL)
    myhtml = driver.page_source
    error,musterTable,musterSummaryTable=validateMusterHTML(eachMuster,myhtml)
    if error is None:  
      outhtml=''
      outhtml+=stripTableAttributes(musterSummaryTable,"musterSummary")
      outhtml+=stripTableAttributes(musterTable,"musterDetails")
      title="Muster: %s state:%s District:%s block:%s finyear:%s " % (eachMuster.musterNo,eachMuster.block.district.state.name,eachMuster.block.district.name,eachMuster.block.name,getFullFinYear(eachMuster.finyear))
      logger.info(title) 
      outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
      try:
        outhtml=outhtml.encode("UTF-8")
      except:
        outhtml=outhtml
      filename="%s.html" % (eachMuster.musterNo)
      eachMuster.musterFile.save(filename, ContentFile(outhtml))
      eachMuster.musterDownloadAttemptDate=datetime.now()
      eachMuster.isDownloaded=True
      eachMuster.save()
    else:
      logger.info("Muster Download Erorr: %s " % (error))
      eachMuster.musterDownloadAttemptDate=datetime.now()
      eachMuster.downloadError=error
      eachMuster.save()
#  myMusters=Muster.objects.filter(

  driverFinalize(driver)
  displayFinalize(display)
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
