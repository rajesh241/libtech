from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.parse import urlparse,parse_qs
import os
import requests
import sys
import re
from customSettings import repoDir,djangoDir,djangoSettings,jobCardRegisterTimeThreshold
import lxml.html
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,saveVillageReport,table2csv
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Village

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)

  args = vars(parser.parse_args())
  return args

def validateWorkerList(myhtml):
  error=None
  myTable=None
  htmlsoup=BeautifulSoup(myhtml,"html.parser")
  myTable=htmlsoup.find('table',id="sortable")
  if myTable is None:
      error="Table not Found"
      print("Table not FOund")
  return error,myTable



def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
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
    panchayatName=eachVillage.panchayat.name
    villageName=eachVillage.name
    eachPanchayat=eachVillage.panchayat
    url="http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=SmartCardreport_engRH&actionVal=MobnumberStatus&id=%s&Retype=null&type=null&file=%s" % (eachVillage.tcode,eachVillage.name) 
    logger.info(url)
    try:
      driver.get(url)
      driver.get(url)
      myhtml = driver.page_source
      error=0
    except:
      error=1

    if error==0:
      logger.info("No Error")
      error1,myTable=validateWorkerList(myhtml)
      if error1 is  None:
        logger.info("Worker List found") 
        outhtml=''
        outcsv=''
        outhtml+=stripTableAttributes(myTable,"myTable")
        outcsv+=table2csv(myTable)
        title="WorkerList  state:%s District:%s block:%s panchayat: %s vilage:%s " % (stateName,districtName,blockName,panchayatName,villageName)
        outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
        try:
          outhtml=outhtml.encode("UTF-8")
        except:
          outhtml=outhtml
   
        try:
          outcsv=outcsv.encode("UTF-8")
        except:
          outcsv=outcsv

        filename=eachVillage.slug+"_tjr.html"
        filenamecsv=eachVillage.slug+"_tjr.csv"
        finyear=getCurrentFinYear()
        reportType="telJobcardRegisterHTML"
        saveVillageReport(logger,eachVillage,finyear,reportType,filename,outhtml)
        reportType="telJobcardRegisterCSV"
        saveVillageReport(logger,eachVillage,finyear,reportType,filenamecsv,outcsv)

  driverFinalize(driver)
  displayFinalize(display)
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
