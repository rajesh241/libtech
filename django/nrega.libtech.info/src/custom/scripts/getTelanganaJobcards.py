from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
import requests
from customSettings import repoDir,djangoDir,djangoSettings,jobCardRegisterTimeThreshold

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,PanchayatReport,Jobcard

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will download jobcard list for Telangana')
  parser.add_argument('-d', '--download', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-p', '--process', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-g', '--generate', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-pc', '--panchayatCode', help='Panchayat Code', required=False)

  args = vars(parser.parse_args())
  return args
def fetchData(logger,fullPanchayatCode,eachPanchayat):
  stateCode='02'
  districtCode=eachPanchayat.block.district.code[-2:]
  blockCode=eachPanchayat.block.tcode[-2:]
  #districtCode=fullPanchayatCode[2:4]
  #blockCode=fullPanchayatCode[5:7]
  panchayatCode=fullPanchayatCode[8:10]
  logger.info("DistrictCode: %s, blockCode : %s , panchayatCode: %s " % (districtCode,blockCode,panchayatCode))
  headers = {
    'Host': 'www.nrega.telangana.gov.in',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=Common_Ajax_engRH&actionVal=Display&page=commondetails_eng',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

  params = (
    ('requestType', 'Household_engRH'),
    ('actionVal', 'view'),
)

  data = [
  ('State', '02'),
  ('District', districtCode),
  ('Mandal', blockCode),
  ('Panchayat', panchayatCode),
  ('Village', '-1'),
  ('HouseHoldId', ''),
  ('Go', ''),
  ('spl', 'Select'),
  ('input2', ''),
]
  url='http://www.nrega.telangana.gov.in/Nregs/FrontServlet'
  response = requests.post(url, headers=headers, params=params, data=data)
  cookies = response.cookies
  logger.info(cookies)
      
  logger.info(response.cookies)
  response=requests.post('http://www.nrega.telangana.gov.in/Nregs/FrontServlet', headers=headers, params=params, cookies=cookies, data=data)
  return response.text

def fetchData1(logger,fullPanchayatCode):
  url="http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=Household_engRH&actionVal=view HTTP/1.1"
  logger.info("Printing Muster URl %s" % url)
  stateCode='02'
  districtCode=fullPanchayatCode[2:4]
  blockCode=fullPanchayatCode[5:7]
  panchayatCode=fullPanchayatCode[8:10]
  headers = {
      'Accept-Encoding': 'gzip, deflate',
      'Accept-Language': 'en-US,en;q=0.5',
      'Upgrade-Insecure-Requests': '1',
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36 Vivaldi/1.91.867.42',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
  }

  params = (
      ('State', stateCode),
      ('District', districtCode),
      ('Mandal', blockCode),
      ('Panchayat', panchayatCode),
      ('Village', '-1'),
      ('HouseHoldId', ''),
      ('Go', ''),
      ('input2', ''),
      ('spl', 'Select'),
  )

  response = requests.get(url, headers=headers, params=params)
  cookies = response.cookies
  logger.info(cookies)
      
  response = requests.get(url, headers=headers, params=params, cookies=cookies)
  logger.info(response.cookies)
  return response.text


def validateData(logger,myhtml):
  error=None
  myTable=None
  htmlsoup=BeautifulSoup(myhtml,"html.parser")
  myTable=htmlsoup.find('table',id='sortable')
  if myTable is None:
    logger.info("Table not found")
    error="Table not found"
  return error,myTable

def main():
  telanganaStateCode='36'
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  finyear=getCurrentFinYear()
  fullfinyear=getFullFinYear(finyear)
  reportType="telanganaJobcardRegister"
  if args['process']:
    logger.info("Processing the jobcards")
    inPanchayatCode=args['panchayatCode']
    if inPanchayatCode is not None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement="FULL",block__district__state__code=telanganaStateCode,code=inPanchayatCode)[:limit]
    else:
      myPanchayats=Panchayat.objects.filter(crawlRequirement="FULL",block__district__state__code=telanganaStateCode)[:limit]
    for eachPanchayat in myPanchayats:
      logger.info(eachPanchayat.block.name+eachPanchayat.code+eachPanchayat.name) 
      panchayatReport=PanchayatReport.objects.filter(reportType=reportType,finyear=finyear,panchayat=eachPanchayat).first()
      fullPanchayatCode=eachPanchayat.code
      districtCode=eachPanchayat.block.district.code[-2:]
      #jobcardPrefix="TS-%s-" %(districtCode)
      jobcardPrefix="TS-" 
      if panchayatReport is not None:
        logger.info("Panchayat Report Exists")
        myhtml=panchayatReport.reportFile.read()  
        #myhtml=eachPanchayat.jobcardRegisterFile.read()
        htmlsoup=BeautifulSoup(myhtml,"html.parser")
        myTable=htmlsoup.find('table',id="myTable")
        rows=myTable.findAll("tr")
        for row in rows:
          if jobcardPrefix in str(row):
            cols=row.findAll('td')
            tjobcard=cols[1].text.lstrip().rstrip()
            jobcard=cols[2].text.lstrip().rstrip()
            myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
            if myJobcard is None:
              Jobcard.objects.create(jobcard=jobcard)
            myJobcard=Jobcard.objects.filter(jobcard=jobcard).first()
            myJobcard.panchayat=eachPanchayat
            myJobcard.tjobcard=tjobcard
            myJobcard.isRequired=1
            logger.info(tjobcard+jobcard)
            myJobcard.save()
           
  if args['generate']:
    logger.info("Generating panchayatwise stat")
    myPanchayats=Panchayat.objects.filter(crawlRequirement="FULL",block__district__state__code=telanganaStateCode)[:limit]
    outcsv=''
    for eachPanchayat in myPanchayats:
      logger.info(eachPanchayat.block.name+eachPanchayat.code+eachPanchayat.name) 
      districtName=eachPanchayat.block.district.slug
      blockName=eachPanchayat.block.slug
      panchayatName=eachPanchayat.slug
      allJobcards=Jobcard.objects.filter(panchayat=eachPanchayat,isRequired=True)
      totalJobcards=str(len(allJobcards))
      scJobcards=Jobcard.objects.filter(panchayat=eachPanchayat,caste__contains="SC",isRequired=True)
      totalSC=str(len(scJobcards))
      outcsv+="%s,%s,%s,%s,%s\n" % (districtName,blockName,panchayatName,totalJobcards,totalSC)
    with open("/tmp/tpanchayatReport.csv","w") as f:
      f.write(outcsv)
       
  if args['download']:
    logger.info("This script will download Jobcards")
    inPanchayatCode=args['panchayatCode']
    if inPanchayatCode is not None:
      myPanchayats=Panchayat.objects.filter(crawlRequirement="FULL",block__district__state__code=telanganaStateCode,code=inPanchayatCode)[:limit]
    else:
      myPanchayats=Panchayat.objects.filter(crawlRequirement="FULL",block__district__state__code=telanganaStateCode)[:limit]
    for eachPanchayat in myPanchayats:
      logger.info(eachPanchayat.block.name+eachPanchayat.code+eachPanchayat.name) 
      panchayatReport=PanchayatReport.objects.filter(reportType=reportType,finyear=finyear,panchayat=eachPanchayat).first()
      if panchayatReport is None:
        fullPanchayatCode=eachPanchayat.code
        stateName=eachPanchayat.block.district.state.name
        districtName=eachPanchayat.block.district.name
        blockName=eachPanchayat.block.name
        panchayatName=eachPanchayat.name

        myhtml=fetchData(logger,fullPanchayatCode,eachPanchayat)
        myhtml=myhtml.replace("<tbody>","")
        myhtml=myhtml.replace("</tbody>","")
        error,myTable=validateData(logger,myhtml) 
        if error is  None:
          logger.info('No Error')
          outhtml=''
          outhtml+=stripTableAttributes(myTable,"myTable")
          title="jobcards state:%s District:%s block:%s panchayat: %s finyear:%s " % (stateName,districtName,blockName,panchayatName,fullfinyear)
          outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
          try:
            outhtml=outhtml.encode("UTF-8")
          except:
            outhtml=outhtml
          filename="jr_%s_%s.html" % (eachPanchayat.slug,finyear)
          savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
  
 
#       filename="/tmp/%s.html" % (fullPanchayatCode) 
#       with open(filename, 'wb') as html_file:
#           logger.info('Writing [%s]' % filename)
#           html_file.write(myhtml.encode('utf-8'))
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
