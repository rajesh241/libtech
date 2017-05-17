from bs4 import BeautifulSoup
from datetime import datetime,date
import requests
import os
import sys
import re
import time
from customSettings import repoDir,djangoDir,djangoSettings
from customSettings import musterTimeThreshold,searchIP

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import table2csv,stripTableAttributes,htmlWrapperLocal,getFullFinYear,savePanchayatReport
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import Q
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Muster,PanchayatReport,Wagelist
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will Download the delayed Payment list')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-f', '--finyear', help='Financial year for which data needs to be crawld', required=False)
  parser.add_argument('-s', '--stateCode', help='State for which the delayed payment report needs to be crawld', required=False)

  args = vars(parser.parse_args())
  return args

def validateWagelist(block,myhtml):
  error=None
  myTable=None
  jobcardPrefix=block.district.state.stateShortCode+"-"
  if (jobcardPrefix in myhtml):
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if jobcardPrefix in str(table):
        myTable=table
    if myTable is None:
      error="Wagelist Table Not Found"
  else:
    error="Jobcard Prefix not found"
  return error,myTable


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  stateCode=args['stateCode'] 
  if stateCode is not None:
    myWagelists=Wagelist.objects.filter( Q(isDownloaded=False,block__district__state__code=stateCode) | Q(downloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isProcessed=1,block__district__state__code=stateCode) ).order_by("downloadAttemptDate")[:limit]
  else:
    myWagelists=Wagelist.objects.filter( Q(isDownloaded=False) | Q(downloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isRequired=1,isProcessed=1) ).order_by("downloadAttemptDate")[:limit]
  
  for eachWagelist in myWagelists:
    wagelistNo=eachWagelist.wagelistNo
    fullfinyear=getFullFinYear(eachWagelist.finyear)
    fullDistrictCode=eachWagelist.block.district.code
    stateName=eachWagelist.block.district.state.name
    districtName=eachWagelist.block.district.name
    fullBlockCode=eachWagelist.block.code
    stateShortCode=eachWagelist.block.district.state.stateShortCode
    blockName=eachWagelist.block.name
    eachBlock=eachWagelist.block
    logger.info(wagelistNo)
    url="http://%s/netnrega/srch_wg_dtl.aspx?state_code=&district_code=%s&state_name=%s&district_name=%s&block_code=%s&wg_no=%s&short_name=%s&fin_year=%s&mode=wg" % (searchIP,fullDistrictCode,stateName.upper(),districtName.upper(),fullBlockCode,wagelistNo,stateShortCode,fullfinyear)
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
      error,myTable=validateWagelist(eachBlock,htmlsource1)
      if error is None:
        logger.info("Error is None, Saving Wagelist File")
        outhtml=''
        outcsv=''
        outhtml+=stripTableAttributes(myTable,"myTable")
        #outcsv+=table2csv(dcTable)
        title="WageList : state:%s District:%s block:%s Wagelist: %s finyear:%s " % (stateName,districtName,blockName,wagelistNo,fullfinyear)
        outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
        try:
          outhtml=outhtml.encode("UTF-8")
        except:
          outhtml=outhtml
        filename="%s.html" % (wagelistNo)
        eachWagelist.wagelistFile.save(filename, ContentFile(outhtml))
        eachWagelist.downloadAttemptDate=timezone.now()
        eachWagelist.isDownloaded=True
        eachWagelist.isProcessed=False
        eachWagelist.save()
      else:
        eachWagelist.downloadAttemptDate=timezone.now()
        eachWagelist.downloadError=error
        eachWagelist.save()
 


  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
