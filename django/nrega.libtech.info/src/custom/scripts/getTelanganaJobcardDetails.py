from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
import requests
from customSettings import repoDir,djangoDir,djangoSettings,jobCardRegisterTimeThreshold,telanganaThresholdDate
from lxml import etree
sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getCurrentFinYear,savePanchayatReport,table2csv,getFullFinYear,getCenterAlignedHeading,getTelanganaDate
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import F,Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,PanchayatReport,Jobcard,Applicant,Stat,FTO,PaymentDetail

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
  parser.add_argument('-j', '--jobcard', help='Jobcard for which the numbster needs to be downloaded', required=False)

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
  finyear=getCurrentFinYear()
  fullfinyear=getFullFinYear(finyear)
  if args['process']:
    logger.info("Processing the jobcards")
    myJobcards=Jobcard.objects.filter(panchayat__block__district__state__code=telanganaStateCode,isDownloaded=1,isProcessed=0)[:limit]
    if injobcard is not None:
      myJobcards=Jobcard.objects.filter(jobcard=injobcard)
    else:
      myJobcards=Jobcard.objects.filter(panchayat__block__district__state__code=telanganaStateCode,isDownloaded=1,isProcessed=0)[:limit]
      #myJobcards=Jobcard.objects.filter(panchayat__block__district__state__code=telanganaStateCode,isDownloaded=1,isProcessed=1,isRequired=1,allApplicantFound=0)[:limit]
    for eachJobcard in myJobcards:
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
      #myhtml=eachPanchayat.jobcardRegisterFile.read()
      htmlsoup=BeautifulSoup(myhtml,"lxml")
      myTable=htmlsoup.find('table',id="workerTable")
      rows=myTable.findAll('tr')
      allApplicantFound=True
      for row in rows:
        cols=row.findAll('td')
        if len(cols)>0:
          applicantNo=cols[1].text.lstrip().rstrip()
          if applicantNo.isdigit():
            applicantNo=int(applicantNo)
          else:
        #  if isinstance(applicantNo,int) is False:
            applicantNo=0
          logger.info("applicantNo is %s " % str(applicantNo)) 
          name=cols[2].text.lstrip().rstrip()
          logger.info(str(applicantNo)+name)
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
          myApplicant.save()

      myTable=htmlsoup.find('table',id="paymentTable")
      rows=myTable.findAll('tr')
      for row in rows:
        cols=row.findAll('td')
        if len(cols)>0:
          epayorderNo=cols[0].text.lstrip().rstrip()
          payorderDateString=cols[5].text.lstrip().rstrip()
          applicantNameArray=cols[8].text.lstrip().rstrip().split()
          if epayorderNo != "Total":
            logger.info(epayorderNo+" "+str(applicantNameArray)) 
            #surname=applicantNameArray[0]
            #name=applicantNameArray[1]
            transactionDateString=cols[5].text.lstrip().rstrip()
            transactionDate=getTelanganaDate(transactionDateString,'smallYear')
            #myApplicant=Applicant.objects.filter(jobcard__jobcard=jobcard,name=name,jobcard__surname=surname).first()
            myApplicant=Applicant.objects.filter(jobcard__jobcard=jobcard,name__in=applicantNameArray).first()
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
                logger.info("Date is Greater than Threshold")
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
      eachJobcard.isProcessed=True
      logger.info("Processed Jobcard: %s,allApplicant FOund: %s " % (jobcard,str(allApplicantFound)))
      eachJobcard.save()
     
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
