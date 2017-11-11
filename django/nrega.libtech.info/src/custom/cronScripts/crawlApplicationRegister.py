from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
import requests
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,jobCardRegisterTimeThreshold

sys.path.insert(0, repoDir)
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,LibtechTag

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
  parser.add_argument('-p', '--panchayatCode', help='PanchayatCode for which the numbster needs to be downloaded', required=False)

  args = vars(parser.parse_args())
  return args
def validateApplicationRegister(logger,myhtml,block):
  error=None
  myTable=None
  jobcardPrefix=block.district.state.stateShortCode+"-"
  if (jobcardPrefix in str(myhtml)):
    htmlsoup=BeautifulSoup(myhtml,"lxml")
    tables=htmlsoup.findAll('table')
    for table in tables:
      if "Head of HouseHold"  in str(table):
        myTable=table
  else:
    error="job card Prefix not found"
  if myTable is None:
    error="Table not found"
  return error,myTable
def getJobcardRegister(logger,eachPanchayat):
  logger.info("Processing : panchayat: %s " % (eachPanchayat.name))
  stateCode=eachPanchayat.block.district.state.code
  fullDistrictCode=eachPanchayat.block.district.code
  fullBlockCode=eachPanchayat.block.code
  fullPanchayatCode=eachPanchayat.code
  districtName=eachPanchayat.block.district.name
  blockName=eachPanchayat.block.name
  stateName=eachPanchayat.block.district.state.name
  panchayatName=eachPanchayat.name
  crawlIP=eachPanchayat.block.district.state.crawlIP
  finyear=getCurrentFinYear()
  fullfinyear=getFullFinYear(finyear) 
  logger.info("Processing StateCode %s, fullDistrictCode : %s, fullBlockCode : %s, fullPanchayatCode: %s " % (stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode))
  panchayatPageURL="http://%s/netnrega/IndexFrame.aspx?lflag=local&District_Code=%s&district_name=%s&state_name=%s&state_Code=%s&block_name=%s&block_code=%s&fin_year=%s&check=1&Panchayat_name=%s&Panchayat_Code=%s" % (crawlIP,fullDistrictCode,districtName,stateName,stateCode,blockName,fullBlockCode,fullfinyear,panchayatName,fullPanchayatCode)
  logger.info(panchayatPageURL)
  #Starting the Download Process
  url="http://nrega.nic.in/netnrega/home.aspx"
  #response = requests.get(url, headers=headers, params=params)
  response = requests.get(panchayatPageURL)
  cookies = response.cookies
  logger.info(cookies)
  headers = {
    'Host': 'nregasp2.nic.in',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': panchayatPageURL,
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

  params = (
    ('lflag', 'eng'),
    ('fin_year', fullfinyear),
    ('Panchayat_Code', fullPanchayatCode),
    ('type', 'a'),
  )

  response=requests.get('http://nregasp2.nic.in/netnrega/Citizen_html/Panchregpeople.aspx', headers=headers, params=params, cookies=cookies)
  logger.info("Downloaded StateCode %s, fullDistrictCode : %s, fullBlockCode : %s, fullPanchayatCode: %s " % (stateCode,fullDistrictCode,fullBlockCode,fullPanchayatCode))
  return response.text
# with open("/tmp/y.html", "w") as f:
#   f.write(response.text)
# headers = {
#   'Host': 'nregasp2.nic.in',
#   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0',
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en-US,en;q=0.5',
#   'Accept-Encoding': 'gzip, deflate',
#   'Referer': panchayatPageURL,
#   'Connection': 'keep-alive',
#   'Upgrade-Insecure-Requests': '1',
#
# url="http://nregasp2.nic.in/netnrega/writereaddata/citizen_out/panchregpeople_%s_eng1718.html" % (fullPanchayatCode)
# logger.info(url)
# response=requests.get(url, headers=headers, cookies=cookies)
#
# myhtml=response.text 
# with open ('/tmp/abcd.html','w') as f:
#   f.write(myhtml)

def main():
  alwaysTag=LibtechTag.objects.filter(name="Always")
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  finyear=getCurrentFinYear()
  fullfinyear=getFullFinYear(finyear) 
  url = "http://164.100.129.6/netnrega/dynamic_account_details.aspx"
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  stateCode=args['stateCode']
  panchayatCode=args['panchayatCode']
  if panchayatCode is not None:
    myPanchayats=Panchayat.objects.filter(code=panchayatCode)
  elif stateCode is not None:
    myPanchayats=Panchayat.objects.filter(Q (crawlRequirement="FULL")  &  (Q (applicationRegisterCrawlDate__lt = jobCardRegisterTimeThreshold) | Q(applicationRegisterCrawlDate__isnull = True ) ) & Q (block__district__state__code=stateCode)).order_by('applicationRegisterCrawlDate')[:limit]
  else:
    myPanchayats=Panchayat.objects.filter(Q (crawlRequirement="FULL")  & Q(block__district__state__isNIC=True) & (Q (applicationRegisterCrawlDate__lt = jobCardRegisterTimeThreshold) | Q(applicationRegisterCrawlDate__isnull = True ) ) ).order_by('applicationRegisterCrawlDate')[:limit]
#  myPanchayats=Panchayat.objects.filter(fullPanchayatCode='3405003010').order_by('applicationRegisterCrawlDate')[:limit]
  for eachPanchayat in myPanchayats:
    myhtml=getJobcardRegister(logger,eachPanchayat)
    myhtml=str(myhtml).replace("</nobr><br>",",")
    myhtml=myhtml.replace("bordercolor='#111111'>","bordercolor='#111111'><tr>")
#    myhtml = myhtml.replace('\n', ' ').replace('\r', '')
#    myhtml=str(myhtml).replace("</td> <tr>","</td></tr><tr>")
#   driver.get(panchayatPageURL)
#   elem = driver.find_element_by_link_text("Registration Application Register")
#   elem.click()
#   myhtml = driver.page_source
#    logger.info(myhtml)
  #  with open("/tmp/abcd.html","w") as f:
  #    f.write(myhtml)
    error,myTable=validateApplicationRegister(logger,myhtml,eachPanchayat.block)
    if error is None:
      logger.info("No error")
      outhtml=''
      outhtml+=stripTableAttributes(myTable,"myTable")
      title="Jobcard Register: state:%s District:%s block:%s panchayat: %s finyear:%s " % (eachPanchayat.block.district.state.name,eachPanchayat.block.district.name,eachPanchayat.block.name,eachPanchayat.name,fullfinyear)
      outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
      try:
        outhtml=outhtml.encode("UTF-8")
      except:
        outhtml=outhtml
      filename="applicationRegister_%s_%s.html" % (eachPanchayat.slug,finyear)
      reportType="applicationRegister"
      savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
      eachPanchayat.applicationRegisterCrawlDate=timezone.now()
      eachPanchayat.save() 
    else:
      logger.info("Error")
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
