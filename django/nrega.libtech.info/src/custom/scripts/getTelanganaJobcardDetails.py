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
from lxml import etree
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear,getCenterAlignedHeading
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,PanchayatReport,Jobcard,Applicant

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will download jobcard list for Telangana')
  parser.add_argument('-d', '--download', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-p', '--process', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)

  args = vars(parser.parse_args())
  return args


def fetchJobcard(logger,tjobcard):
  headers = {
    'Host': 'www.nrega.telangana.gov.in',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=HouseholdInf_engRH&actionVal=SearchJOB&JOB_No=152003910014010001',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

  params = (
    ('requestType', 'HouseholdInf_engRH'),
    ('actionVal', 'SearchJOB'),
    ('JOB_No', tjobcard),
)
  url='http://www.nrega.telangana.gov.in/Nregs/FrontServlet'
  response=requests.get(url, headers=headers, params=params)
  cookies = response.cookies
  logger.info(cookies)
  logger.info(response.cookies)
  response=requests.get(url, headers=headers, params=params, cookies=cookies)
  return response.text
def validateData(logger,myhtml):
  error=None
  jobcardTable=None
  workerTable=None
  aggregateTable=None
  paymentTable=None
  error="noError"
  bs = BeautifulSoup(myhtml, "html.parser")
  bs = BeautifulSoup(myhtml, "lxml")
  main1 = bs.find('div',id='main1')
  logger.debug("Main1[%s]" % main1)

  if main1 != None:
    table1 = main1.find('table')
    logger.debug("Table1[%s]" % table1)

    jobcardTable = table1.find('table', id='sortable')

    workerTable = jobcardTable.findNext('table', id='sortable')
  main2 = bs.find(id='main2')
  if main2 is not  None:
    aggregateTable = main2.find('table')
  main3 = bs.find(id='main3')
  if main3 is not  None:
    paymentTable = main3.find('table')
  if jobcardTable is None:
    error+="jobcardTable not found"
  if workerTable is None:
    error+="WorkerTable not found     " 
  if aggregateTable is None:
    error+="Aggregate Table not found"
  if paymentTable is None:
    error+="Payment Table not found"
  if error == "noError":
    error=None
  return error,jobcardTable,workerTable,aggregateTable,paymentTable

def validateDatai1(logger,myhtml):
  error=None
  jobcardTable=None
  workerTable=None
  aggregateTable=None
  paymentTable=None
  html = etree.HTML(myhtml)
  tr_nodes = html.xpath('//html/body/div/form/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[4]/td/table/tbody/tr[2]/td/div/table/tbody/tr[1]/td/table')
  mytable=html.xpath('/html/body/div/form/table')
  mytable=html.xpath('/html/body/div/form/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[4]/td/table/tbody/tr[2]/td/div/table/tbody/tr[1]/td/table')
  for eachtable in mytable:
    logger.info(etree.tostring(eachtable, pretty_print=True))
  logger.info(str(tr_nodes))
  htmlsoup=BeautifulSoup(myhtml,"html.parser")
  myTables=htmlsoup.find('table',id='sortable')
  i=0
  for eachTable in myTables:
    logger.info("Found table %d" % i)
    if "Land Owned in Acres" in str(eachTable):
      logger.info("Found Jobcard Table")
      jobcardTable=eachTable
    if "Relationship" in str(eachTable):
      logger.info("Found Relationship Table")
      workerTable=eachTable
    if "No Of Balance Days" in str(eachTable):
      logger.info("Found Aggregate Table")
    i=i+1
  return error,jobcardTable,workerTable,aggregateTable,paymentTable
  
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
  if args['process']:
    logger.info("Processing the jobcards")
    myJobcards=Jobcard.objects.filter(panchayat__block__district__state__code=telanganaStateCode,isDownloaded=1,isProcessed=0)[:limit]
    for eachJobcard in myJobcards:
      logger.info(eachJobcard.tjobcard+"-"+eachJobcard.jobcard)
      tjobcard=eachJobcard.tjobcard
      jobcard=eachJobcard.jobcard
      myhtml=eachJobcard.jobcardFile.read()  
      #myhtml=eachPanchayat.jobcardRegisterFile.read()
      htmlsoup=BeautifulSoup(myhtml,"lxml")
      myTable=htmlsoup.find('table',id="workerTable")
      rows=myTable.findAll('tr')
      for row in rows:
        cols=row.findAll('td')
        if len(cols)>0:
          applicantNo=cols[1].text.lstrip().rstrip()
          name=cols[2].text.lstrip().rstrip()
          logger.info(applicantNo+name)
          myApplicant=Applicant.objects.filter(jobcard1=jobcard,applicantNo=applicantNo).first()
          if myApplicant is None:
            logger.info(myApplicant)
     
  if args['download']:
    logger.info("Download Jobcard Details Page")
    myJobcards=Jobcard.objects.filter(panchayat__block__district__state__code=telanganaStateCode,panchayat__isnull=False,isDownloaded=False,tjobcard__isnull=False)[:limit]
    for eachJobcard in myJobcards:
      logger.info(eachJobcard.tjobcard) 
      tjobcard=eachJobcard.tjobcard
      eachPanchayat=eachJobcard.panchayat
      stateName=eachPanchayat.block.district.state.name
      districtName=eachPanchayat.block.district.name
      blockName=eachPanchayat.block.name
      panchayatName=eachPanchayat.name

      myhtml=fetchJobcard(logger,tjobcard)
     # Kludge because of missing </tr> Tag
    #  myhtml=myhtml.replace('<tr  class="alternateRow"','</tr><tr  class="alternateRow"')
    #  myhtml=myhtml.replace('</tr></tr><tr  class="alternateRow"','</tr><tr  class="alternateRow"')
      error,jobcardTable,workerTable,aggregateTable,paymentTable=validateData(logger,myhtml)
      if error is None:
        logger.info("Yipee no Error")
        outhtml=''
        outhtml+=getCenterAlignedHeading("Jobcard Details")      
        outhtml+=stripTableAttributes(jobcardTable,"jobcardTable")
        outhtml+=getCenterAlignedHeading("Worker Details")      
        outhtml+=stripTableAttributes(workerTable,"workerTable")
        outhtml+=getCenterAlignedHeading("Aggregate Work Details")      
        outhtml+=stripTableAttributes(aggregateTable,"aggregateTable")
        outhtml+=getCenterAlignedHeading("Payment Details")      
        outhtml+=stripTableAttributes(paymentTable,"paymentTable")
        title="Jobcard Details state:%s District:%s block:%s panchayat: %s jobcard:%s " % (stateName,districtName,blockName,panchayatName,tjobcard)
        outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
        try:
          outhtml=outhtml.encode("UTF-8")
        except:
          outhtml=outhtml
   
        filename="%s.html" % (tjobcard)
        eachJobcard.jobcardFile.save(filename, ContentFile(outhtml))
        eachJobcard.isDownloaded=True
        eachJobcard.isProcessed=False
        eachJobcard.downloadAttemptCount=eachJobcard.downloadAttemptCount+1
        eachJobcard.downloadCount=eachJobcard.downloadCount+1
        eachJobcard.downloadAttemptDate=timezone.now()
        eachJobcard.downloadDate=timezone.now()
        eachJobcard.downloadError=None
      else:
        logger.info("Error: %s " % error)
        eachJobcard.downloadAttemptDate=timezone.now()
        eachJobcard.downloadAttemptCount=eachJobcard.downloadAttemptCount+1
        #eachJobcard.downloadError=error
      eachJobcard.save()
      with open('/tmp/%s.html' % tjobcard,"w") as f:
        f.write(myhtml) 
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
