from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
from customSettings import repoDir,djangoDir,djangoSettings,jobCardRegisterTimeThreshold

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat

def alterWorkerList(cur,logger,inhtml,stateName,districtName,blockName,panchayatName):
  status=None
  outhtml=''
  outcsv=''
  with open("/tmp/b.html","wb") as f:
    f.write(inhtml)
  splitHTML=inhtml.split(b"MGNREGA Worker Details") 
  if len(splitHTML) == 2:
    status=1
    logger.info("File Downloaded seeds to be correct")
    m = re.findall ( b'<table(.*?)table>', splitHTML[1], re.DOTALL)
   # logger.info(m)
    myhtml=b"<html><table"+m[0]+b"table></html>"
    htmlsoup = BeautifulSoup(myhtml,"html.parser")
    tables=htmlsoup.findAll('table')
    title="MNREGA Worker List : %s-%s-%s-%s" % (stateName.upper(),districtName.upper(),blockName.upper(),panchayatName.upper())
    #outhtml+=getCenterAligned('<h3 style="color:blue"> %s</h3>' %title )
    for table in tables:
      outhtml+=stripTableAttributes(table,"libtechDetails")
      outcsv+=table2csv(table)
    outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center" style="color:blue">'+title+'</h1>', body=outhtml)
  return status,outhtml,outcsv


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)

  args = vars(parser.parse_args())
  return args

def getStateValidation(myhtml):
  bs = BeautifulSoup(myhtml, "html.parser")
  state = bs.find(id='__VIEWSTATE').get('value')
  validation = bs.find(id='__EVENTVALIDATION').get('value')
  return state,validation
def getPostData(state,validation,stateCode=None,fullDistrictCode=None,fullBlockCode=None,fullPanchayatCode=None,submit=None):
  if stateCode is None:
    stateCode=''
  if fullDistrictCode is None:
    fullDistrictCode=''
  if fullBlockCode is None:
    fullBlockCode=''
  if fullPanchayatCode is None:
    fullPanchayatCode=''

  data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE': state,
'__VIEWSTATEENCRYPTED':'',
'__VIEWSTATEENCRYPTED':'',
'ctl00$ContentPlaceHolder1$ddl_state': stateCode,
'ctl00$ContentPlaceHolder1$ddl_dist': fullDistrictCode,
'ctl00$ContentPlaceHolder1$ddl_blk': fullBlockCode,
'ctl00$ContentPlaceHolder1$ddl_pan': fullPanchayatCode,
'ctl00$ContentPlaceHolder1$ddlactive':'ALL',
'ctl00$ContentPlaceHolder1$ddlfreez':'ALL',
'ctl00$ContentPlaceHolder1$ddltype':'All',
'ctl00$ContentPlaceHolder1$ddlgender':'ALL',
'ctl00$ContentPlaceHolder1$ddlage':'ALL',
'ctl00$ContentPlaceHolder1$ddlcast':'ALL',
'ctl00$ContentPlaceHolder1$DdID':'ALL',
'ctl00$ContentPlaceHolder1$ddlvulnerable':'ALL',
'ctl00$ContentPlaceHolder1$ddlworkers':'ALL',
    }
 
  return data 
def getWorkerList(logger,url,stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode):
  httplib2.debuglevel = 1
  h = httplib2.Http('.cache')
  print("URL %s " % url)
  try:
    response = urlopen(url)
    html_source = response.read()
    bs = BeautifulSoup(html_source, "html.parser")
    state = bs.find(id='__VIEWSTATE').get('value')
    validation = bs.find(id='__EVENTVALIDATION').get('value')

#    logger.info("State: %s " % state)
#    logger.info("Validation: %s " % validation)

    data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE': state,
'__VIEWSTATEENCRYPTED':'',
'__EVENTVALIDATION':validation,
'ctl00$ContentPlaceHolder1$ddl_state': stateCode,

    }   #data=getPostData(state,validation,stateCode=stateCode)
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    state,validation=getStateValidation(content)
#    logger.info("After putting State: %s " % state)
#    logger.info("After Putting State Validation: %s " % validation)
    data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE': state,
'__VIEWSTATEENCRYPTED':'',
'__EVENTVALIDATION':validation,
'ctl00$ContentPlaceHolder1$ddl_state': stateCode,
'ctl00$ContentPlaceHolder1$ddl_dist': fullDistrictCode,

    }
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    state,validation=getStateValidation(content)


    data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE': state,
'__VIEWSTATEENCRYPTED':'',
'__EVENTVALIDATION':validation,
'ctl00$ContentPlaceHolder1$ddl_state': stateCode,
'ctl00$ContentPlaceHolder1$ddl_dist': fullDistrictCode,
'ctl00$ContentPlaceHolder1$ddl_blk': fullBlockCode,

    }
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    state,validation=getStateValidation(content)

    data = {
'__EVENTTARGET':'',
'__EVENTARGUMENT':'',
'__LASTFOCUS':'',
'__VIEWSTATE': state,
'__VIEWSTATEENCRYPTED':'',
'__EVENTVALIDATION':validation,
'ctl00$ContentPlaceHolder1$ddl_state': stateCode,
'ctl00$ContentPlaceHolder1$ddl_dist': fullDistrictCode,
'ctl00$ContentPlaceHolder1$ddl_blk': fullBlockCode,
'ctl00$ContentPlaceHolder1$ddl_pan': fullPanchayatCode,
'ctl00$ContentPlaceHolder1$Button1':'submit',

    } 
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    state,validation=getStateValidation(content)

  except:
    response={'status': '404'}
    content=''

  return response,content


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  url = "http://164.100.129.6/netnrega/dynamic_account_details.aspx"
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  stateCode=args['stateCode']
  if stateCode is not None:
    myPanchayats=Panchayat.objects.filter(Q (crawlRequirement="FULL")  &  (Q (jobcardCrawlDate__lt = jobCardRegisterTimeThreshold) | Q(jobcardCrawlDate__isnull = True ) ) & Q (block__district__state__code=stateCode)).order_by('jobcardCrawlDate')[:limit]
  else:
    myPanchayats=Panchayat.objects.filter(Q (crawlRequirement="FULL")  &  (Q (jobcardCrawlDate__lt = jobCardRegisterTimeThreshold) | Q(jobcardCrawlDate__isnull = True ) ) ).order_by('jobcardCrawlDate')[:limit]
#  myPanchayats=Panchayat.objects.filter(fullPanchayatCode='3405003010').order_by('jobcardCrawlDate')[:limit]
  for eachPanchayat in myPanchayats:
    logger.info("Processing : panchayat: %s " % (eachPanchayat.name))
    stateCode=eachPanchayat.block.district.state.code
    fullDistrictCode=eachPanchayat.block.district.code
    fullBlockCode=eachPanchayat.block.code
    fullPanchayatCode=eachPanchayat.code
    districtName=eachPanchayat.block.district.name
    blockName=eachPanchayat.block.name
    stateName=eachPanchayat.block.district.state.name

    logger.info("Processing StateCode %s, fullDistrictCode : %s, fullBlockCode : %s, fullPanchayatCode: %s " % (stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode))
    cur='' 
    htmlresponse,myhtml=getWorkerList(logger,url,stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode)
    if htmlresponse['status'] == '200':
      logger.info("File Downloaded SuccessFully")
      status,outhtml,outcsv=alterWorkerList(cur,logger,myhtml,stateName,districtName,blockName,eachPanchayat.name)
      if status is not None:
        filename=eachPanchayat.slug+"_jr.html"
        filenamecsv=eachPanchayat.slug+"_jr.csv"
        try:
          outhtml=outhtml.encode("UTF-8")
        except:
          outhtml=outhtml
        try:
          outcsv=outcsv.encode("UTF-8")
        except:
          outcsv=outcsv
        logger.info("Processing StateCode %s, fullDistrictCode : %s, fullBlockCode : %s, fullPanchayatCode: %s " % (stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode))
        finyear=getCurrentFinYear()
        reportType="jobcardRegisterHTML"
        savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
        reportType="jobcardRegisterCSV"
        savePanchayatReport(logger,eachPanchayat,finyear,reportType,filenamecsv,outcsv)
      #  eachPanchayat.jobcardRegisterFile.save(filename, ContentFile(outhtml))
        eachPanchayat.jobcardCrawlDate=timezone.now()
        eachPanchayat.save()
    logger.info("Processing StateCode %s, fullDistrictCode : %s, fullBlockCode : %s, fullPanchayatCode: %s " % (stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode))

  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
