from bs4 import BeautifulSoup
from queue import Queue
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
from threading import Thread
import threading
from datetime import datetime,date,time
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,jobCardRegisterTimeThreshold,telanganaThresholdDate,telanganaJobcardTimeThreshold,postalWebsite,telanganaStateCode
from crawlFunctions import getNumberProcesses
from lxml import etree
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear,getCenterAlignedHeading,getTelanganaDate,getjcNumber
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q
from django.db.models import Count,Sum

reportType="postalAccountStatus"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,PanchayatReport,Jobcard,Applicant,Stat,FTO,PaymentDetail,Village,LibtechTag,Worker,PendingPostalPayment


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will download jobcard list for Telangana')
  parser.add_argument('-d', '--download', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-e', '--enumerate', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-p', '--process', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-pc', '--panchayatCode', help='Panchayat for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-bc', '--blockCode', help='Block for which the numbster needs to be downloaded', required=False)

  args = vars(parser.parse_args())
  return args


def getResponse(logger,url,oldResponse,districtCode,blockCode,panchayatCode,eventTarget,isSubmit=None):
  html_source = oldResponse.content
  bs = BeautifulSoup(html_source, "html.parser")
  state = bs.find(id='__VIEWSTATE').get('value')
  validation = bs.find(id='__EVENTVALIDATION').get('value')
  stateGenerator = bs.find(id='__VIEWSTATEGENERATOR').get('value')
  cookies = oldResponse.cookies
  #logger.info(cookies)
  headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'bdp.tsonline.gov.in',
    'Referer': 'http://bdp.tsonline.gov.in/NeFMS_TS/NeFMS/Reports/NeFMS/PaymentPendingAccountsMandal.aspx',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
}
  if isSubmit is not  None:
    data = [
    ('__EVENTTARGET', eventTarget),
    ('__EVENTARGUMENT', ''),
    ('__LASTFOCUS', ''),
    ('__VIEWSTATE', state),
    ('__VIEWSTATEGENERATOR', stateGenerator),
    ('__EVENTVALIDATION', validation),
    ('ctl00$MainContent$btnDisplayReport',''),
    ('ctl00$MainContent$ddldistrictname', districtCode),
    ('ctl00$MainContent$ddlMandalName', blockCode),
    ('ctl00$MainContent$ddlGPName', panchayatCode),
     ]
  else:
    data = [
    ('__EVENTTARGET', eventTarget),
    ('__EVENTARGUMENT', ''),
    ('__LASTFOCUS', ''),
    ('__VIEWSTATE', state),
    ('__VIEWSTATEGENERATOR', stateGenerator),
    ('__EVENTVALIDATION', validation),
    ('ctl00$MainContent$ddldistrictname', districtCode),
    ('ctl00$MainContent$ddlMandalName', blockCode),
    ('ctl00$MainContent$ddlGPName', panchayatCode),
     ]
  response=requests.post(url, headers=headers, cookies=cookies, data=data)
  #logger.info(response)
  return response
def enumerateCodes(logger):
  dict={}
  dict['MAHABUBNAGAR']='MAHBUBNAGAR'
  dict['ALL']='All'
  dict['Burugupalle']='BURGUPALLE'
  eventTarget='ctl00$MainContent$ddlGPName'
  url=postalWebsite
  response = requests.get(url)
  bs = BeautifulSoup(response.content, "html.parser")
  selectOptions=bs.findAll("select")
  for eachSelect in selectOptions:
    if "ddldistrictname" in str(eachSelect):
      myOptions=eachSelect.findAll("option")
      logger.info(len(myOptions))
      for eachOption in myOptions:
        name=eachOption.text
        code=eachOption['value']
        myDistrict=District.objects.filter(name=name,state__code=telanganaStateCode).first()
        if myDistrict is None:
          logger.info("Distrct: %s not found" % (name))
          
          name=dict[name]
          myDistrict=District.objects.filter(name=name,state__code=telanganaStateCode).first()
        if myDistrict is not None:
          myDistrict.tcode=code
          myDistrict.save()
          logger.info("Update Distrct %s with code %s " % (name,code))
          if code=='14': 
            response=getResponse(logger,url,response,code,"-1","-1",eventTarget,1)
            bs = BeautifulSoup(response.content, "html.parser")
            blockSelectOptions=bs.findAll("select")
            for eachBlockSelect in blockSelectOptions:
              if 'ddlMandalName' in str(eachBlockSelect):
                blockOptions=eachBlockSelect.findAll("option")
                logger.info(len(blockOptions))
                for eachBlockOption in blockOptions:
                  blockName=eachBlockOption.text
                  blockCode=eachBlockOption['value']
                  myBlock=Block.objects.filter(district=myDistrict,name=blockName).first()
                  if myBlock is None:
                     logger.info("District %s Block %s not found" % (name,blockName))
                  if myBlock is not None:
                    myBlock.tcode=blockCode
                    myBlock.save()
                    response=getResponse(logger,url,response,code,blockCode,-1,eventTarget,1)
                    bs = BeautifulSoup(response.content, "html.parser")
                    panchayatSelectOptions=bs.findAll("select")
                    for eachPanchayatSelect in panchayatSelectOptions:
                      if 'ddlGPName' in str(eachPanchayatSelect):
                        panchayatOptions=eachPanchayatSelect.findAll("option")
                        logger.info(len(panchayatOptions))
                        for eachPanchayatOption in panchayatOptions:
                          panchayatName=eachPanchayatOption.text
                          panchayatCode=eachPanchayatOption['value']
                          myPanchayat=Panchayat.objects.filter(block=myBlock,name=panchayatName).first()
                          if myPanchayat is None:
                            logger.info("Block %s Panchyat %s " % (blockName,panchayatName))
                            if panchayatName in dict:
                              panchayatName=dict[panchayatName]
                              myPanchayat=Panchayat.objects.filter(block=myBlock,name=panchayatName).first()
                          if myPanchayat is not None:
                            myPanchayat.tcode=panchayatCode
                            myPanchayat.save()
                     
          
def processPostalReport(logger,panchayatReport):
  eachPanchayat=panchayatReport.panchayat
  logger.info(eachPanchayat.name+","+eachPanchayat.code)
  if panchayatReport is not None:
    logger.info("Panchayat Report Exists")
    myhtml=panchayatReport.reportFile.read()  
    logger.info("Read the HTML")
    htmlsoup=BeautifulSoup(myhtml,"lxml")
    tableIDs=["table015","table1630","table3060","table6090"]
    for eachTable in tableIDs:
      myTable=htmlsoup.find('table',id=eachTable)
      if myTable is not None:
        #logger.info("Found %s " % (eachTable))
        rows=myTable.findAll("tr")
        for row in rows:
          cols=row.findAll('td')
          if len(cols) > 5:
            if "-" in cols[3].text:
              tjobcard=cols[3].text.lstrip().rstrip().split("-")[0]
              applicantName=cols[2].text.lstrip().rstrip()
              
              applicantNo=int(cols[3].text.lstrip().rstrip().split("-")[1])
              myWorker=Worker.objects.filter(jobcard__tjobcard=tjobcard,applicantNo=applicantNo).first()
              errorString="WorkerMissing"
              if myWorker is not None:
                errorString=''
                transactionDateString=cols[5].text.lstrip().rstrip()
                transactionDate=datetime.strptime(transactionDateString, '%d/%m/%Y')
                #logger.info(transactionDate)
                balance=cols[4].text.lstrip().rstrip().replace(",","")
                lastPostalStatus=PendingPostalPayment.objects.filter(worker=myWorker,lastTransactionDate=transactionDate,balance=balance).first()
                if lastPostalStatus is not None:
                  #logger.info("Postal Status Exists")
                  e=1
                else:
                  PendingPostalPayment.objects.create(worker=myWorker,lastTransactionDate=transactionDate,balance=balance,statusDate=timezone.now())
              logger.info("%s Jobcard %s Appliatnat %s panchayatName %s BlockName %s panchayatCode %s " % (errorString,tjobcard,str(applicantNo),eachPanchayat.slug,eachPanchayat.block.slug,eachPanchayat.code))        
               

def downloadPage(logger,eachPanchayat):
  logger.info("Starting to crawl Code %s Panchayat %s Block %s District %s State %s" % (eachPanchayat.code,eachPanchayat.name,eachPanchayat.block.name,eachPanchayat.block.district.name,eachPanchayat.block.district.state.name))
  districtCode=eachPanchayat.block.district.tcode
  blockCode=eachPanchayat.block.tcode
  panchayatCode=eachPanchayat.tcode
  outhtml=''
  title="Postal Payment Details: state:%s District:%s block:%s panchayat: %s " % (eachPanchayat.block.district.state.name,eachPanchayat.block.district.name,eachPanchayat.block.name,eachPanchayat.name)
  url=postalWebsite
  response = requests.get(url)
  
  eventTarget='ctl00$MainContent$ddlGPName'
  response=getResponse(logger,url,response,districtCode,"-1","-1",eventTarget,1)
  response=getResponse(logger,url,response,districtCode,blockCode,"-1",eventTarget,1)
  response=getResponse(logger,url,response,districtCode,blockCode,panchayatCode,eventTarget,1)
  responsePanchayat=getResponse(logger,url,response,districtCode,blockCode,panchayatCode,eventTarget,1)
  
  outhtml+='<h1 aling="center">0-15 Days </h1>' 
  eventTarget="ctl00$MainContent$dgDistrictWise$ctl02$lnk015"
  response=getResponse(logger,url,responsePanchayat,districtCode,blockCode,panchayatCode,eventTarget)
  bs = BeautifulSoup(response.content, "html.parser")
  myTable=bs.find("table",id="ctl00_MainContent_dgPaymentPendingActsDrillDown")
  if myTable is not None:
    outhtml+=stripTableAttributes(myTable,"table015")

  
  outhtml+='<h1 aling="center">16-30 Days </h1>' 
  eventTarget="ctl00$MainContent$dgDistrictWise$ctl02$lnk1630"
  response=getResponse(logger,url,responsePanchayat,districtCode,blockCode,panchayatCode,eventTarget)
  bs = BeautifulSoup(response.content, "html.parser")
  myTable=bs.find("table",id="ctl00_MainContent_dgPaymentPendingActsDrillDown")
  if myTable is not None:
    outhtml+=stripTableAttributes(myTable,"table1630")

  outhtml+='<h1 aling="center">30-60 Days </h1>' 
  eventTarget="ctl00$MainContent$dgDistrictWise$ctl02$lnk3060"
  response=getResponse(logger,url,responsePanchayat,districtCode,blockCode,panchayatCode,eventTarget)
  bs = BeautifulSoup(response.content, "html.parser")
  myTable=bs.find("table",id="ctl00_MainContent_dgPaymentPendingActsDrillDown")
  if myTable is not None:
    outhtml+=stripTableAttributes(myTable,"table3060")
  
  outhtml+='<h1 aling="center">60-90 Days </h1>' 
  eventTarget="ctl00$MainContent$dgDistrictWise$ctl02$lnk6090"
  response=getResponse(logger,url,responsePanchayat,districtCode,blockCode,panchayatCode,eventTarget)
  bs = BeautifulSoup(response.content, "html.parser")
  myTable=bs.find("table",id="ctl00_MainContent_dgPaymentPendingActsDrillDown")
  if myTable is not None:
    outhtml+=stripTableAttributes(myTable,"table6090")
  
  outhtml=htmlWrapperLocal(title=title, head='<h1 aling="center">'+title+'</h1>', body=outhtml)
  try:
    outhtml=outhtml.encode("UTF-8")
  except:
    outhtml=outhtml
  finyear=getCurrentFinYear()
  filename="postalAccountStatus_%s.html" % (eachPanchayat.slug)
  savePanchayatReport(logger,eachPanchayat,finyear,reportType,filename,outhtml)
#  eachPanchayat.applicationRegisterCrawlDate=timezone.now()
#  eachPanchayat.save() 
    
#  logger.info(response.content)
  #with open("/tmp/a.html","wb") as f:
  #  f.write(response.content)
def queueManager(logger,myobjs,processType):
  logger.info("Number of Instances that needs to be download processed %s " % str(len(myobjs)))
  if len(myobjs) > 0:
    n=getNumberProcesses(len(myobjs))
    queueSize=n+len(myobjs)+10
    q = Queue(maxsize=queueSize)
    logger.info("Queue Size %s Numbe of Threads %s " % (str(queueSize),str(n)))
    for obj in myobjs:
      q.put(obj.id)

    for i in range(n):
      logger.info("Starting worker Thread %s " % str(i))
      t = Thread(name = 'Thread-' + str(i), target=workerProcess, args=(logger,q,processType ))
      t.daemon = True  
      t.start()


    q.join()       # block until all tasks are done
    for i in range(n):
      q.put(None)

def workerProcess(logger,q,processType):
  while True:
    objID = q.get()  # if there is no url, this will wait
    if objID is None:
      break
    name = threading.currentThread().getName()

    errorString='' 
    if processType=='download':
      eachPanchayat=Panchayat.objects.filter(id=objID).first()
      logger.info("Current Queue: %s Thread : %s objID: %s PanchayatName: %sBlockName: %s status: %s" % (str(q.qsize()),name,str(eachPanchayat.id),eachPanchayat.slug,eachPanchayat.block.slug,errorString))
      downloadPage(logger,eachPanchayat)
    elif processType=='process':
      eachReport=PanchayatReport.objects.filter(id=objID).first()
      logger.info("Current Queue: %s Thread : %s objID: %s PanchayatName: %sBlockName: %s status: %s" % (str(q.qsize()),name,str(eachReport.id),eachReport.panchayat.slug,eachReport.panchayat.block.slug,errorString))
      processPostalReport(logger,eachReport)
    else:
      logger.info("Nothing to be done") 

    q.task_done()
 

def main():
  alwaysTag=LibtechTag.objects.filter(name="Always")
  regex=re.compile("^[0-9]{4}-[0-9]{4}$")
  benchMark = datetime.strptime(telanganaThresholdDate, "%Y-%m-%d") 
  telanganaStateCode='36'
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  if args['enumerate']:
    logger.info("Will enumerate and put all the District and Block Codes in place") 
    enumerateCodes(logger)
  if args['download']:
    logger.info("Attempting to Download Postal P ayments")
    myPanchayats=Panchayat.objects.filter(crawlRequirement="FULL",block__district__state__code=telanganaStateCode)[:limit]
   # for eachPanchayat in myPanchayats:
   #   downloadPage(logger,eachPanchayat)
    queueManager(logger,myPanchayats,'download')
  if args['process']:
    logger.info("Attempting to Process Postal P ayments")
    curfinyear=getCurrentFinYear()
    today_min = datetime.combine(date.today(), time.min)
    today_max = datetime.combine(date.today(), time.max)
    myPanchayatReports=PanchayatReport.objects.filter(finyear=curfinyear,panchayat__crawlRequirement="FULL",panchayat__block__district__state__code=telanganaStateCode,reportType=reportType,updateDate__range=(today_min, today_max))
    queueManager(logger,myPanchayatReports,'process')
  #  for eachReport in myPanchayatReports:
  #    logger.info(eachReport.panchayat.code)
  #    processPostalReport(logger,eachReport)
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
