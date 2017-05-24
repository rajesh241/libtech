from bs4 import BeautifulSoup
from datetime import datetime,date
import httplib2
from urllib.request import urlopen
from urllib.parse import urlencode
import os
import sys
import re
import time
from customSettings import repoDir,djangoDir,djangoSettings

sys.path.insert(0, repoDir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getjcNumber,correctDateFormat
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import F
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Applicant,Muster,WorkDetail,Wagelist,FTO,PaymentDetail

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This Script is for Processing Muster')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)

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
  stateCode=args['stateCode']
  if stateCode is not None:
    logger.info("StateCode is %s" % stateCode)
    myFTOs=FTO.objects.filter(isDownloaded=1,isProcessed=0,block__district__state__code=stateCode)[:limit] 
  else:
    myFTOs=FTO.objects.filter(isDownloaded=1,isProcessed=0)[:limit]

  for eachFTO in myFTOs:
    logger.info("FTO ID: %s , FTO No: %s " % (str(eachFTO.id),eachFTO.ftoNo))
    myhtml=eachFTO.ftoFile.read()
    stateShortCode=eachFTO.block.district.state.stateShortCode
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    isComplete=True
    allApplicantFound=True
    allWDFound=True
    errorString=""
    mytable=htmlsoup.find('table',id="myTable")
    rows = mytable.findAll('tr')
    for row in rows:
      if "Reference No." in str(row):
        logger.info("This is a header row")
        cols=row.findAll('th')
        header=[]
        for i,col in enumerate(cols):
          header.append(col.text.lstrip().rstrip())
        logger.info(str(header))
        jobcardIndex=header.index("Job Card No.")
        applicantNameIndex=header.index("Applicant Name")
        accountHolderIndex=header.index("Name of primary Account holder")
        wagelistIndex=header.index("Wagelist No")
        referenceNoIndex=header.index("Reference No.")
        amountToBeCreditedIndex=header.index("Amount to be Credit  (In Rs)")
        transactionDateIndex=header.index("Transaction date")
        processedDateIndex=header.index("Processed Date")
        rejectionReasonIndex=header.index("Rejection Reason")
        creditedAmountIndex=header.index("Credit Amount (In Rs)")
        statusIndex=header.index("Status")
      else:
        cols=row.findAll('td')
        jobcard=cols[jobcardIndex].text.lstrip().rstrip()
        applicantName=cols[applicantNameIndex].text.lstrip().rstrip()
        accountHolder=cols[accountHolderIndex].text.lstrip().rstrip()
        wagelistNo=cols[wagelistIndex].text.lstrip().rstrip()
        referenceNo=cols[referenceNoIndex].text.lstrip().rstrip()
        amountToBeCredited=cols[amountToBeCreditedIndex].text.lstrip().rstrip()
        transactionDateString=cols[transactionDateIndex].text.lstrip().rstrip()
        processDateString=cols[processedDateIndex].text.lstrip().rstrip()
        rejectionReason=cols[rejectionReasonIndex].text.lstrip().rstrip()
        status=cols[statusIndex].text.lstrip().rstrip()
        creditedAmount=cols[creditedAmountIndex].text.lstrip().rstrip()
        if creditedAmount=='':
          creditedAmount=None
        processDate=correctDateFormat(processDateString)
        transactionDate=correctDateFormat(transactionDateString)
        logger.info("Jocard: %s, applicantName: %s " % (jobcard,applicantName))

        matchedApplicants=Applicant.objects.filter(jobcard=jobcard,name=applicantName)
        if len(matchedApplicants) == 1:
          logger.info("MatchedApplicant Found")
          applicant=matchedApplicants.first()
        else:
          matchedApplicants=Applicant.objects.filter(jobcard=jobcard,poAccountName=accountHolder)
          if len(matchedApplicants) == 1:
            logger.info("MatchedApplicant Found")
            applicant=matchedApplicants.first()
          else:
            allApplicantFound=False
            applicant=None
        
        myWagelists=Wagelist.objects.filter(wagelistNo=wagelistNo)
        wagelistArray=[]
        for eachWagelist in myWagelists:
           wagelistArray.append(eachWagelist.id)

        myWDRecords=WorkDetail.objects.filter(wagelist__in=wagelistArray,applicant=applicant,totalWage=amountToBeCredited)
        if len(myWDRecords) == 0:
          errorString+="No wdRecords FOUND"
          allWDFound=False
          wdDetail=None
        elif len(myWDRecords) == 1:
          wdDetail=myWDRecords.first()
        if len(myWDRecords) > 1:
          errorString+="Multiple wdRecords Found"
          allWDFound=False
          wdDetail=None


        myPaymentDetail=PaymentDetail.objects.filter(fto=eachFTO,referenceNo=referenceNo).first()
        if myPaymentDetail is None:
          PaymentDetail.objects.create(fto=eachFTO,referenceNo=referenceNo)
          logger.info("Payment Record Created")
        myPaymentDetail=PaymentDetail.objects.filter(fto=eachFTO,referenceNo=referenceNo).first()
        myPaymentDetail.applicant=applicant
        myPaymentDetail.workDetail=wdDetail
        myPaymentDetail.transactionDate=transactionDate
        myPaymentDetail.processDate=processDate
        myPaymentDetail.status=status
        myPaymentDetail.rejectionReason=rejectionReason
        myPaymentDetail.creditedAmount=creditedAmount
        myPaymentDetail.save()
        
          
#if myDistrict is not None:
#  print(myDistrict.code)
    logger.info("isComplete: %s, allApplicantFound: %s allWorkRecordsFound: %s errorString;%s" % (str(isComplete),str(allApplicantFound),str(allWDFound),errorString))
    logger.info("Processed FTO ID: %s , FTO No: %s " % (str(eachFTO.id),eachFTO.ftoNo))
    eachFTO.isComplete=isComplete
    eachFTO.isProcessed=1
    eachFTO.allApplicantFound=allApplicantFound
    eachFTO.allWDFound =allWDFound
    eachFTO.save()

  logger.info("...END PROCESSING") 
  exit(0)

if __name__ == '__main__':
  main()
