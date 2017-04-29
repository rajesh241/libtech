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
def validateDCReport(panchayat,myhtml):
  error=None
  dcTable=None
  jobcardPrefix=panchayat.block.district.state.stateShortCode+"-"
  if (jobcardPrefix in myhtml):
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if jobcardPrefix in str(table):
        dcTable=table
    if dcTable is None:
      error="Delay Compensation Table nout found"
  else:
    error="Jobcard Prefix not found"
  return error,dcTable


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
  stateCodes=['34']
  for stateCode in stateCodes:
    myPanchayats=Panchayat.objects.filter(crawlRequirement='FULL',block__district__state__stateCode=stateCode)
    for eachPanchayat in myPanchayats:
      logger.info("Processing : panchayat: %s " % (eachPanchayat.name))
      stateCode=eachPanchayat.block.district.state.stateCode
      fullDistrictCode=eachPanchayat.block.district.fullDistrictCode
      fullBlockCode=eachPanchayat.block.fullBlockCode
      fullPanchayatCode=eachPanchayat.fullPanchayatCode
      districtName=eachPanchayat.block.district.name
      blockName=eachPanchayat.block.name
      stateName=eachPanchayat.block.district.state.name
      crawlIP=eachPanchayat.block.district.state.crawlIP
      panchayatName=eachPanchayat.name
      url="http://%s/netnrega/state_html/delay_comp_dtl.aspx?page=p&state_name=%s&state_code=%s&fin_year=%s&district_name=%s&district_code=%s&block_name=%s&block_code=%s&panchayat_name=%s&panchayat_code=%s&source=national&" %(crawlIP,stateName,stateCode,fullfinyear,districtName,fullDistrictCode,blockName,fullBlockCode,panchayatName,fullPanchayatCode)
      logger.info(url)
      try:
        r  = requests.get(url)
        error=0
      except requests.exceptions.RequestException as e:  # This is the correct syntax
        logger.info(e) 
        error=1
      if error==0:
        curtime = time.strftime('%Y-%m-%d %H:%M:%S')
        htmlsource=r.text
        htmlsource1=re.sub(regex,"",htmlsource)
        error,dcTable=validateDCReport(eachPanchayat,htmlsource1)
        if error is None:
          outhtml=''
          outcsv=''
          outhtml+=stripTableAttributes(dcTable,"dcTable")
          outcsv+=table2csv(dcTable)
          title="Delay Compensation report state:%s District:%s block:%s panchayat: %s finyear:%s " % (stateName,districtName,blockName,panchayatName,fullfinyear)
          outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
          try:
            outhtml=outhtml.encode("UTF-8")
          except:
            outhtml=outhtml
   
          try:
            outcsv=outcsv.encode("UTF-8")
          except:
            outcsv=outcsv
          filename="dc_%s_%s.html" % (eachPanchayat.slug,finyear)
          csvfilename="dc_%s_%s.csv" % (eachPanchayat.slug,finyear)
          reportType="delayedCompensationHTML"
          savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
          reportType="delayCompensationCSV"
          savePanchayatReport(logger,eachPanchayat,finyear,reportType,csvfilename,outcsv)
   
        else:
          logger.info(error)
   
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()

