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

from nregaFunctions import stripTableAttributes,htmlWrapperLocal,getjcNumber
from wrappers.logger import loggerFetch

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.db.models import F
from django.db.models import Count
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from nrega.models import State,District,Block,Panchayat,Applicant,Muster,WorkDetail,Wagelist

from firebase import firebase
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This Script is to update Firebase Database')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-s', '--stateCode', help='StateCode for which the numbster needs to be downloaded', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  from firebase import firebase
  firebase = firebase.FirebaseApplication('https://libtech-app.firebaseio.com/', None)
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  stateCode=args['stateCode']
  myPanchayats=Panchayat.objects.filter(crawlRequirement="FULL",block__district__state__code=stateCode)
#  myPanchayats=Panchayat.objects.filter(crawlRequirement="FULL",block__district__state__code=stateCode,code='3401020001')
  for eachPanchayat in myPanchayats:
    panchayatName=eachPanchayat.name
    blockName=eachPanchayat.block.name
    logger.info("Block: %s, Panchayat: %s " % (blockName,panchayatName))
#    result = firebase.post('https://libtech-app.firebaseio.com/geo/%s'%(blockName.upper()), {'panchayatName': panchayatName.upper()})
    
    workObjs=WorkDetail.objects.filter(applicant__panchayat=eachPanchayat).values('applicant__jobcard').annotate(dcount=Count('applicant__jobcard'))
    for obj in workObjs:
      jobcard=obj['applicant__jobcard']
      jobcard=jobcard.replace("/","_")
#      logger.info(jobcard)
#      result = firebase.post('https://libtech-app.firebaseio.com/jobcard/%s/%s/'%(blockName.upper(),panchayatName.upper()), {'jobcard': jobcard})
        
    workObjs=WorkDetail.objects.filter(applicant__panchayat=eachPanchayat)
    for wd in workObjs:
      jobcard = wd.applicant.jobcard
      jobcard = jobcard.replace('/', '_')
      name = wd.applicant.name
      musterNo = wd.muster.musterNo
      workName = wd.muster.workName
      totalWage = wd.totalWage
      wagelistNo = wd.wagelist.wagelistNo 
      ftoNo = None
      musterStatus = wd.musterStatus
      bankNameOrPOName = wd.applicant.bankName + wd.applicant.poName
      dateTo = str(wd.muster.dateTo)
      firstSignatoryDate = None
      secondSignatoryDate = str(wd.muster.paymentDate)
      transactionDate = None
      bankProcessedDate = None
      paymentDate = str(wd.muster.paymentDate)
      creditedDate = str(wd.creditedDate)
      ftoStatus = None
      rejectionReason = None
      dateArray=[wd.creditedDate,wd.muster.paymentDate,wd.muster.dateTo]
      dateLabels=['creditedDate','paymentDate','dateTo']
      maxDate = max(x for x in dateArray if x is not None)
      maxDateIndex=dateArray.index(maxDate)
      maxDateColName = dateLabels[maxDateIndex]
      try:
          currentStatusOfNode = firebase.get('/data/%s/%s/%s'%(panchayatName, jobcard, dateTo), None)
          currentNoTransactionsForDate = len(currentStatusOfNode) - 1
  #        logger.info(str(currentStatusofNode))
          newTransactionNo = currentNoTransactionsForDate + 1
      except: 
          newTransactionNo = 1
      logger.info("Jobcard: %s, dateTo: %s newTransactionNo: %s " %(jobcard,dateTo,str(newTransactionNo)))
      result = firebase.patch('https://libtech-app.firebaseio.com/data/%s/%s/%s/%s'%(panchayatName, jobcard, dateTo, newTransactionNo), {'jobcard': jobcard, 'name': name, 'musterNo': musterNo, 'workName': workName, 'totalWage': totalWage, 'wagelistNo': wagelistNo, 'ftoNo': ftoNo, 'musterStatus': musterStatus, 'bankNameOrPOName': bankNameOrPOName, 'dateTo': dateTo, 'firstSignatoryDate': firstSignatoryDate, 'secondSignatoryDate': secondSignatoryDate, 'transactionDate': transactionDate, 'bankProcessedDate': bankProcessedDate, 'paymentDate': paymentDate, 'creditedDate': creditedDate, 'ftoStatus': ftoStatus, 'rejectionReason': rejectionReason, 'maxDate': maxDate, 'maxDateColName': maxDateColName})
    #print(result)
 

  logger.info("...END PROCESSING") 
  exit(0)

if __name__ == '__main__':
  main()
