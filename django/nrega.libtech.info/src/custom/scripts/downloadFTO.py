from bs4 import BeautifulSoup
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
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

from nrega.models import State,District,Block,Panchayat,Muster,PanchayatReport,Wagelist,FTO
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

def validateFTO(block,myhtml):
  error=None
  myTable=None
  summaryTable=None
  jobcardPrefix=block.district.state.stateShortCode+"-"
  if (jobcardPrefix in str(myhtml)):
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if"FTO_Acc_signed_dt_p2w"  in str(table):
        summaryTable=table
      elif "Reference No" in str(table):
        myTable=table
    if myTable is None:
      error="FTO Details Table Not Found"
    if summaryTable is None:
      error="Summary Table not found"
  else:
    error="Jobcard Prefix not found"
  return error,myTable,summaryTable

def getFTO(logger,fullfinyear,stateCode,ftoNo,districtName):
  httplib2.debuglevel = 1
  h = httplib2.Http('.cache')
  url = "http://164.100.129.6/netnrega/fto/fto_status_dtl.aspx?fto_no=%s&fin_year=%s&state_code=%s" % (ftoNo, fullfinyear, stateCode)
  logger.info("FTO URL %s " % url)
  logger.info("finyear: %s, stateCode: %s, ftoNo: %s, districtName: %s " % (fullfinyear,stateCode,ftoNo,districtName))
  try:
    response = urlopen(url)
    html_source = response.read()
    bs = BeautifulSoup(html_source, "html.parser")
    state = bs.find(id='__VIEWSTATE').get('value')
#    logger.info('state[%s]' % state)
    validation = bs.find(id='__EVENTVALIDATION').get('value')
#    logger.info('value[%s]' % validation)
    data = {
      '__EVENTTARGET':'ctl00$ContentPlaceHolder1$Ddfto',
      '__EVENTARGUMENT':'',
      '__LASTFOCUS':'',
      '__VIEWSTATE': state,
      '__VIEWSTATEENCRYPTED':'',
      '__EVENTVALIDATION': validation,
      'ctl00$ContentPlaceHolder1$Ddfin': fullfinyear,
      'ctl00$ContentPlaceHolder1$Ddstate': stateCode,
      'ctl00$ContentPlaceHolder1$Txtfto': ftoNo,
      'ctl00$ContentPlaceHolder1$Ddfto': ftoNo,
    }
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
  except:
    response={'status': '404'}
    content=''

  return response,content


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
    myFTOs=FTO.objects.filter( Q(isDownloaded=False,block__district__state__code=stateCode) | Q(downloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isProcessed=1,block__district__state__code=stateCode) ).order_by("downloadAttemptDate")[:limit]
  else:
    myFTOs=FTO.objects.filter( Q(isDownloaded=False) | Q(downloadAttemptDate__lt = musterTimeThreshold,isComplete=0,isProcessed=1) ).order_by("downloadAttemptDate")[:limit]
  for eachFTO in myFTOs:
    logger.info("FTO ID: %s FTO No: %s " % (str(eachFTO.id),eachFTO.ftoNo)) 
    stateCode=eachFTO.block.district.state.code
    ftoNo=eachFTO.ftoNo
    splitFTO=ftoNo.split("_")
    ftoyear=splitFTO[1][4:6]
    ftomonth=splitFTO[1][2:4]
    if int(ftomonth) > 3:
      ftofinyear=str(int(ftoyear)+1)
    else:
      ftofinyear=ftoyear
    finyear=eachFTO.finyear
    logger.info("FTO Finyear is %s finyear is %s " % (ftofinyear,finyear))
    fullfinyear=getFullFinYear(ftofinyear)
    block=eachFTO.block
    blockName=block.name
    districtName=block.district.name
    stateName=block.district.state.name
    htmlresponse,htmlsource = getFTO(logger,fullfinyear,stateCode,ftoNo,districtName)
    logger.info("Response = %s " % htmlresponse)
    if htmlresponse['status'] == '200':
      logger.info("Status is 200")
      error,myTable,summaryTable=validateFTO(block,htmlsource)
      if error is None:
        logger.info("No error")
        outhtml=''
        outhtml+=stripTableAttributes(summaryTable,"summaryTable")
        outhtml+=stripTableAttributes(myTable,"myTable")
        #outcsv+=table2csv(dcTable)
        title="FTO state:%s District:%s block:%s FTO No: %s finyear:%s " % (stateName,districtName,blockName,ftoNo,fullfinyear)
        outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
        try:
          outhtml=outhtml.encode("UTF-8")
        except:
          outhtml=outhtml
        filename="%s.html" % (ftoNo)
        eachFTO.ftoFile.save(filename, ContentFile(outhtml))
        eachFTO.downloadAttemptDate=timezone.now()
        eachFTO.isDownloaded=True
        eachFTO.isProcessed=False
        eachFTO.ftofinyear=ftofinyear
        eachFTO.save()
      else:
        logger.info(error)
        eachFTO.downloadAttemptDate=timezone.now()
        eachFTO.ftofinyear=ftofinyear
        eachFTO.downloadError=error
        eachFTO.save()

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
