from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
import threading
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'includes'))
from customSettings import repoDir,djangoDir,djangoSettings,jobCardRegisterTimeThreshold,telanganaThresholdDate,telanganaJobcardTimeThreshold
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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,PanchayatReport,Jobcard,Applicant,Stat,FTO,PaymentDetail,Village,LibtechTag,Worker

def downloadWorker(logger,q,processType,inputargs):
  while True:
    objID = q.get()  # if there is no url, this will wait
    if objID is None:
      break
    name = threading.currentThread().getName()
    logger.info("Downloading Jobcard ID: %s Thread %s " % (str(objID),name))
    eachJobcard=Jobcard.objects.filter(id=objID).first()
    if processType=='download':
      downloadJobcard(logger,eachJobcard)
    else:
      processJobcard(logger,eachJobcard)
    q.task_done()

def processJobcard(logger,eachJobcard):
  regex=re.compile("^[0-9]{4}-[0-9]{4}$")
  benchMark = datetime.strptime(telanganaThresholdDate, "%Y-%m-%d") 
  telanganaStateCode='36'
  logger.info(eachJobcard.tjobcard+"-"+eachJobcard.jobcard)
  tjobcard=eachJobcard.tjobcard
  jobcard=eachJobcard.jobcard
  eachPanchayat=eachJobcard.panchayat
  myhtml=eachJobcard.jobcardFile.read()  
  #To find teh surname
  m=re.findall ('Surname</td><td>(.*?)</td>',str(myhtml.decode("UTF-8")),re.DOTALL)
  if len(m)>0:
    surname=m[0].lstrip().rstrip()
  else:
    surname=''
  logger.info("surname is %s " % surname)
  m=re.findall ('Head of the Family</td><td>(.*?)</td>',str(myhtml.decode("UTF-8")),re.DOTALL)
  if len(m)>0:
    headOfFamily=m[0].lstrip().rstrip()
  else:
    headOfFamily=''
  logger.info("headOfFamily is %s " % headOfFamily)
  m=re.findall ('Caste</td><td>(.*?)</td>',str(myhtml.decode("UTF-8")),re.DOTALL)
  if len(m)>0:
    caste=m[0].lstrip().rstrip()
  else:
    caste=''
  logger.info("caste is %s " % caste)
  #myhtml=eachPanchayat.jobcardRegisterFile.read()
  htmlsoup=BeautifulSoup(myhtml,"lxml")
  myTable=htmlsoup.find('table',id="workerTable")
  allApplicantFound=True
  if  "Relationship" in str(myTable):
    logger.info("Found the Worker Table")
    rows=myTable.findAll('tr')
    for row in rows:
      cols=row.findAll('td')
      if len(cols)>0:
        logger.info(str(row))
        applicantNo=cols[1].text.lstrip().rstrip()
        if applicantNo.isdigit():
          applicantNo=int(applicantNo)
        else:
      #  if isinstance(applicantNo,int) is False:
          applicantNo=0
        logger.info("applicantNo is %s " % str(applicantNo)) 
        name=cols[2].text.lstrip().rstrip()
        logger.info(str(applicantNo)+name)
        myWorker=Worker.objects.filter(jobcard=eachJobcard,name=name).first()
        if myWorker is None:
           myWorker=Worker.objects.create(jobcard=eachJobcard,name=name,applicantNo=applicantNo)
        myWorker.applicantNo=applicantNo
        myWorker.gender=cols[4].text.lstrip().rstrip()
        myWorker.age=cols[3].text.lstrip().rstrip()
        myWorker.relationship=cols[5].text.lstrip().rstrip()
        myWorker.save()

        myApplicant=Applicant.objects.filter(jobcard=eachJobcard,applicantNo=applicantNo).first()
        if myApplicant is None:
          logger.info("Applicant not Found")
          Applicant.objects.create(jobcard=eachJobcard,applicantNo=applicantNo,panchayat=eachPanchayat)
          myApplicant=Applicant.objects.filter(jobcard=eachJobcard,applicantNo=applicantNo).first()
          myApplicant.source='tel'
          allApplicantFound=False
        else:
          logger.info("Applicant Found")
        myApplicant.panchayat=eachPanchayat
        myApplicant.gender=cols[4].text.lstrip().rstrip()
        myApplicant.age=cols[3].text.lstrip().rstrip()
        myApplicant.relationship=cols[5].text.lstrip().rstrip()
        myApplicant.name=name
        logger.info("Applicant Id is %d" %myApplicant.id)
        myApplicant.save()
  
  myTable=htmlsoup.find('table',id="paymentTable")
  rows=myTable.findAll('tr')
  for row in rows:
    cols=row.findAll('td')
    if len(cols)>0:
      epayorderNo=cols[0].text.lstrip().rstrip()
      payorderDateString=cols[5].text.lstrip().rstrip()
      applicantName=cols[8].text.replace(surname,"").lstrip().rstrip()
      fullApplicantName=cols[8].text.lstrip().rstrip()
      applicantName=re.sub(surname, '', fullApplicantName, flags=re.IGNORECASE).lstrip().rstrip()
      applicantName=cols[8].text.lstrip().lstrip(surname).lstrip().rstrip()
      logger.info("Applicant Name after subtrancting surname is %s " % (applicantName))
      applicantNameArray=cols[8].text.lstrip().rstrip().split()
      if epayorderNo != "Total":
        logger.info(epayorderNo+" "+str(applicantNameArray)) 
        #surname=applicantNameArray[0]
        #name=applicantNameArray[1]
        transactionDateString=cols[5].text.lstrip().rstrip()
        transactionDate=getTelanganaDate(transactionDateString,'smallYear')
        #myApplicant=Applicant.objects.filter(jobcard__jobcard=jobcard,name=name,jobcard__surname=surname).first()
        myApplicant=Applicant.objects.filter(jobcard__jobcard=jobcard,name__in=applicantNameArray).first()
        myApplicant=Applicant.objects.filter(jobcard__jobcard=jobcard,name=applicantName).first()
        if myApplicant is not None:
          ftoNo=cols[1].text.lstrip().rstrip()
          finyear=str(int(ftoNo[5:7])+1)
          myFTO=FTO.objects.filter(ftoNo=ftoNo,finyear=finyear,block=eachPanchayat.block).first()
          if myFTO is None:
            FTO.objects.create(ftoNo=ftoNo,finyear=finyear,block=eachPanchayat.block)
          myFTO=FTO.objects.filter(ftoNo=ftoNo,finyear=finyear,block=eachPanchayat.block).first()
  
          payorderNo=cols[7].text.lstrip().rstrip()
          creditedAmount=cols[11].text.lstrip().rstrip()
          daysWorked=cols[10].text.lstrip().rstrip()
          processedDateString=cols[12].text.lstrip().rstrip()
          disbursedAmount=cols[13].text.lstrip().rstrip()
          disbursedDateString=cols[14].text.lstrip().rstrip()
          processedDate=getTelanganaDate(processedDateString,'smallYear')
          disbursedDate=getTelanganaDate(disbursedDateString,'bigYear')
          myPaymentRecord=PaymentDetail.objects.filter(fto=myFTO,referenceNo=epayorderNo).first()
          if myPaymentRecord is None:
            PaymentDetail.objects.create(fto=myFTO,referenceNo=epayorderNo)
          myPaymentRecord=PaymentDetail.objects.filter(fto=myFTO,referenceNo=epayorderNo).first()
          myPaymentRecord.applicant=myApplicant
          myPaymentRecord.payorderNo=payorderNo
          myPaymentRecord.transactionDate=transactionDate
          myPaymentRecord.processDate=processedDate
          myPaymentRecord.disbursedDate=disbursedDate
          myPaymentRecord.daysWorked=daysWorked
          myPaymentRecord.creditedAmount=creditedAmount
          myPaymentRecord.disbursedAmount=disbursedAmount
          myPaymentRecord.save()
        else:
          logger.info("Applicant Not Found")
          if transactionDate >= benchMark:
            allApplicantFound=False
  
  myTable=htmlsoup.find('table',id="aggregateTable")
  rows=myTable.findAll('tr')
  for row in rows:
    cols=row.findAll('td')
    if len(cols)>0:
      fullfinyear=cols[0].text.lstrip().rstrip()
      if regex.match(fullfinyear):
        totalWorkDays=cols[1].text.lstrip().rstrip()
        totalWage=cols[2].text.lstrip().rstrip()
        finyear=fullfinyear[-2:]
        if totalWorkDays !='':
          myStat=Stat.objects.filter(jobcard=eachJobcard,finyear=finyear,statType="TWD").first()
          if myStat is None:
            Stat.objects.create(jobcard=eachJobcard,finyear=finyear,statType="TWD")
          myStat=Stat.objects.filter(jobcard=eachJobcard,finyear=finyear,statType="TWD").first()
          myStat.value=totalWorkDays
          myStat.save()
        if totalWage !='':
          myStat=Stat.objects.filter(jobcard=eachJobcard,finyear=finyear,statType="TWA").first()
          if myStat is None:
            Stat.objects.create(jobcard=eachJobcard,finyear=finyear,statType="TWA")
          myStat=Stat.objects.filter(jobcard=eachJobcard,finyear=finyear,statType="TWA").first()
          myStat.value=totalWage
          myStat.save()
  
  
  eachJobcard.allApplicantFound=allApplicantFound
  eachJobcard.surname=surname
  eachJobcard.jcNo=getjcNumber(jobcard)
  eachJobcard.headOfHousehold=headOfFamily
  eachJobcard.caste=caste
  eachJobcard.isProcessed=True
  logger.info("Processed Jobcard: %s,allApplicant FOund: %s " % (jobcard,str(allApplicantFound)))
  eachJobcard.save()
  
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
  parser.add_argument('-n', '--numberOfThreads', help='Number of Threads default 5', required=False)
  parser.add_argument('-q', '--queueSize', help='Number of Musters in Queue default 200', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-j', '--jobcard', help='Jobcard for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-pc', '--panchayatCode', help='Panchayat for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-bc', '--blockCode', help='Block for which the numbster needs to be downloaded', required=False)
  parser.add_argument('-c', '--compute', help='Compute Stats', required=False,action='store_const', const=1)

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
  habitation=None
  result = re.search('Habitation(.*)nbsp',myhtml)
  if result is not None:
     logger.info("Found")
     searchText=result.group(1)
     habitation=searchText.replace("&nbsp","").replace(":","").replace(";","").replace("&","").lstrip().rstrip()
     logger.info(habitation)
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
  return error,habitation,jobcardTable,workerTable,aggregateTable,paymentTable

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

def downloadJobcard(logger,eachJobcard):
  logger.info(eachJobcard.tjobcard) 
  tjobcard=eachJobcard.tjobcard
  eachPanchayat=eachJobcard.panchayat
  stateName=eachPanchayat.block.district.state.name
  districtName=eachPanchayat.block.district.name
  blockName=eachPanchayat.block.name
  panchayatName=eachPanchayat.name

  myhtml=fetchJobcard(logger,tjobcard)
#  with open("/tmp/%s.html" % (tjobcard),"w") as f:
#    f.write(myhtml)
 # Kludge because of missing </tr> Tag
#  myhtml=myhtml.replace('<tr  class="alternateRow"','</tr><tr  class="alternateRow"')
#  myhtml=myhtml.replace('</tr></tr><tr  class="alternateRow"','</tr><tr  class="alternateRow"')
  error,villageName,jobcardTable,workerTable,aggregateTable,paymentTable=validateData(logger,myhtml)
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
    if villageName is not None:
      myVillage=Village.objects.filter(panchayat=eachPanchayat,name=villageName).first()
      if myVillage is None:
        Village.objects.create(panchayat=eachPanchayat,name=villageName)
      myVillage=Village.objects.filter(panchayat=eachPanchayat,name=villageName).first()
      eachJobcard.village=myVillage
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
  
def getStat(eachJobcard,statType,finyear):
  myStat=Stat.objects.filter(jobcard=eachJobcard,statType=statType,finyear=finyear).first()
  if myStat is not None:
    myValue=myStat.value
  else:
    myValue=0
  return myValue
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
  injobcard=args['jobcard']
  inpanchayat=args['panchayatCode']
  inblock=args['blockCode']
  finyear=getCurrentFinYear()
  fullfinyear=getFullFinYear(finyear)
  if args['compute']:
    logger.info("Computing Stats")
    outcsv=''
    outcsv+="panchayatCode,panchayatName,Count,Sum\n"
    if inblock is not None:
   #   myobjs=PaymentDetail.objects.filter(transactionDate__isnull=False,processDate__isNULL=True,applicant__jobcard__panchayat__block__code=inblock).value("applicant__jobcard__panchayat__code").annotate(dcount=Count('pk'),dsum=Sum('creditedAmount'))
      myobjs=PaymentDetail.objects.filter(transactionDate__isnull=False,processDate__isnull=True,applicant__jobcard__panchayat__block__code=inblock).values("applicant__jobcard__panchayat__slug","applicant__jobcard__panchayat__code").annotate(dcount=Count('pk'),dsum=Sum('creditedAmount'))
    for obj in myobjs:
      logger.info(str(obj))
      outcsv+="%s,%s,%s,%s\n" % (obj['applicant__jobcard__panchayat__code'],obj['applicant__jobcard__panchayat__slug'],str(obj['dcount']),str(obj['dsum'])) 
    with open("/tmp/tstat.csv","w") as f:
      f.write(outcsv)
    
  if args['generate']:
    logger.info("Generating Report")
    #Generating Payment Report
    outcsv=''
    if inpanchayat is not None:
      myPanchayats=Panchayat.objects.filter(code=inpanchayat)[:limit]
    elif inblock is not None:
      myPanchayats=Panchayat.objects.filter(block__code=inblock)[:limit]
    else:
      myPanchayats=Panchayat.objects.filter(block__district__state__code=telanganaStateCode)[:limit]
    for eachPanchayat in myPanchayats:
      myPaymentDetails=PaymentDetail.objects.filter(applicant__jobcard__panchayat=eachPanchayat) 
      panchayatName=eachPanchayat.slug
      outcsv=''
      outcsv+="Panchayat,name,jobcard,fto,payorderNo,epayorderno,creditedAmount,payOrderDate,creditedDate,disbursedDate,CreditedPayorderDiff,DisbusedCreditedDate,pendingDays\n"
      for eachPayment in myPaymentDetails:
        if eachPayment.processDate is not None and eachPayment.transactionDate is not None:
          creditedPayorderDiff=(eachPayment.processDate-eachPayment.transactionDate).days
        else:
          creditedPayorderDiff=''
        if eachPayment.transactionDate is not None and eachPayment.disbursedDate is None:
          pendingDays=(datetime.now().date()-eachPayment.transactionDate).days
        else:
          pendingDays=''
        if eachPayment.disbursedDate is not None and eachPayment.processDate is not None:
          disbursedCreditedDiff=(eachPayment.disbursedDate-eachPayment.processDate).days
        else:
          disbursedCreditedDiff=''
        outcsv+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (panchayatName,eachPayment.applicant.name,"~"+eachPayment.applicant.jobcard.tjobcard,eachPayment.fto.ftoNo,eachPayment.payorderNo,eachPayment.referenceNo,eachPayment.creditedAmount,str(eachPayment.transactionDate),str(eachPayment.processDate),str(eachPayment.disbursedDate),str(creditedPayorderDiff),str(disbursedCreditedDiff),str(pendingDays))
      logger.info("Processed Panchayat %s " % panchayatName)
      with open("/tmp/t/%s.csv" % panchayatName,"w") as f:
        f.write(outcsv)
    #Generating Jobcard Wise Report
    outcsv=''
    outcsv+="district,block,panchayat,panchayatCode,jobcard,nicJobcard,ifSC,FY12,FY13,FY14,FY15,FY16,FY17,FY18\n"
    if inblock is not None:
      myBlock=Block.objects.filter(code=inblock).first()
      blockName=myBlock.slug
    else:
      blockName="tReport"
    logger.info(blockName)
    if inblock is not None:
      myJobcards=Jobcard.objects.filter(panchayat__block__code=inblock,isDownloaded=1,isProcessed=1)[:limit]
    else:
      myJobcards=Jobcard.objects.filter(panchayat__block__district__state__code=telanganaStateCode,isDownloaded=1,isProcessed=1)[:limit]
    logger.info('Length of Jobcards: %s ' % str(len(myJobcards)))
    i=0
    for eachJobcard in myJobcards:
      i=i+1
      logger.info("Processing %s-%s" % (str(i),eachJobcard.tjobcard))
      districtName=eachJobcard.panchayat.block.district.slug
      blockName=eachJobcard.panchayat.block.slug
      panchayatName=eachJobcard.panchayat.slug
      ifSC=0
      if eachJobcard.caste is not None:
        if "SC" in eachJobcard.caste:
          ifSC=1
      FY12TWD=getStat(eachJobcard,"TWD",12)
      FY13TWD=getStat(eachJobcard,"TWD",13)
      FY14TWD=getStat(eachJobcard,"TWD",14)
      FY15TWD=getStat(eachJobcard,"TWD",15)
      FY16TWD=getStat(eachJobcard,"TWD",16)
      FY17TWD=getStat(eachJobcard,"TWD",17)
      FY18TWD=getStat(eachJobcard,"TWD",18)
      outcsv+="%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s " % (districtName,blockName,panchayatName,eachJobcard.panchayat.code,"~"+eachJobcard.tjobcard,eachJobcard.jobcard,str(ifSC),str(FY12TWD),str(FY13TWD),str(FY14TWD),str(FY15TWD),str(FY16TWD),str(FY17TWD),str(FY18TWD))
      outcsv+="\n"
    with open("/tmp/%s.csv" % (blockName),"w") as f:
      f.write(outcsv)
    
 
  if args['process']:
    logger.info("Processing the jobcards")
    if args['queueSize']:
      queueSize=int(args['queueSize'])
    else:
      queueSize=20
    if args['numberOfThreads']:
      numberOfThreads=int(args['numberOfThreads'])
    else:
      numberOfThreads=1
    logger.info("Starting Muster Download Script with Queue Size: %s and Number of Threads: %s " % (queueSize,numberOfThreads))
    q = Queue(maxsize=queueSize)
    addLimit=queueSize-numberOfThreads-2
    #myJobcards=Jobcard.objects.filter(panchayat__block__district__state__code=telanganaStateCode,isDownloaded=1,isProcessed=0)[:limit]
    if injobcard is not None:
      myJobcards=Jobcard.objects.filter(jobcard=injobcard)
    elif inpanchayat is not None:
      myJobcards=Jobcard.objects.filter(panchayat__code=inpanchayat,isDownloaded=1,isProcessed=0)[:addLimit]
    elif inblock is not None:
      myJobcards=Jobcard.objects.filter(panchayat__block__code=inblock,isDownloaded=1,isProcessed=0)[:addLimit]
    else:
      myJobcards=Jobcard.objects.filter(panchayat__block__district__state__code=telanganaStateCode,isDownloaded=1,isProcessed=0)[:addLimit]
    myJobcards=Jobcard.objects.filter( Q (isBaselineSurvey=True) | Q (isBaselineReplacement=True))[:addLimit]

    for eachJobcard in myJobcards:
      q.put(eachJobcard.id)
    processType='process'
    for i in range(numberOfThreads):
      logger.info("Starting worker Thread %s " % str(i))
      t = Thread(name = 'Thread-' + str(i), target=downloadWorker, args=(logger,q,processType,args, ))
      t.daemon = True
      t.start()

    q.join()       # block until all tasks are done
    for i in range(numberOfThreads):
      q.put(None)


     # myJobcards=Jobcard.objects.filter( Q(isBaselineReplacement = True) | Q (isBaselineSurvey=True))[:limit]
      #myJobcards=Jobcard.objects.filter(panchayat__block__district__state__code=telanganaStateCode,isDownloaded=1,isProcessed=1,isRequired=1,allApplicantFound=0)[:limit]
    
  if args['download']:
    processType='download'
    logger.info("Download Jobcard Details Page")
    if args['limit']:
      limit = int(args['limit'])
    else:
      limit =1
  #if ((args['queueSize']) and ( int(args['queueSize']) > 200)):
    if args['queueSize']:
      queueSize=int(args['queueSize'])
    else:
      queueSize=20
    if args['numberOfThreads']:
      numberOfThreads=int(args['numberOfThreads'])
    else:
      numberOfThreads=1
    logger.info("Starting Muster Download Script with Queue Size: %s and Number of Threads: %s " % (queueSize,numberOfThreads))
    q = Queue(maxsize=queueSize)
    addLimit=queueSize-numberOfThreads-2
    if addLimit <= 0:
      addLimit = 1
   # myJobcards=Jobcard.objects.filter(panchayat__block__district__state__code=telanganaStateCode,panchayat__isnull=False,isDownloaded=False,tjobcard__isnull=False)[:limit]
    if injobcard is not None:
      myJobcards=Jobcard.objects.filter(jobcard=injobcard)
    elif inpanchayat is not None:
      myJobcards=Jobcard.objects.filter(panchayat__code=inpanchayat)[:addLimit]
    elif inblock is not None:
      myJobcards=Jobcard.objects.filter(panchayat__block__code=inblock)[:addLimit]
    else:
      myJobcards=Jobcard.objects.filter( Q(panchayat__block__district__state__code=telanganaStateCode,panchayat__libtechTag__in=alwaysTag) & (Q (downloadAttemptDate__lt = telanganaJobcardTimeThreshold) | Q(isDownloaded= False )  )  ).order_by('downloadAttemptDate')[:addLimit]
    #myJobcards=Jobcard.objects.filter(Q (panchayat__block__district__state__code=telanganaStateCode,panchayat__isnull=False,tjobcard__isnull=False)  &  (Q (downloadAttemptDate__lt = telanganaJobcardTimeThreshold) | Q(isDownloaded= False ) ) ).order_by('downloadAttemptDate')[:addLimit]
    myJobcards=Jobcard.objects.filter( Q (isBaselineSurvey=True) | Q (isBaselineReplacement=True))[:addLimit]
    for eachJobcard in myJobcards:
      q.put(eachJobcard.id)

    for i in range(numberOfThreads):
      logger.info("Starting worker Thread %s " % str(i))
      t = Thread(name = 'Thread-' + str(i), target=downloadWorker, args=(logger,q,processType,args, ))
      t.daemon = True
      t.start()

    q.join()       # block until all tasks are done
    for i in range(numberOfThreads):
      q.put(None)


  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()


