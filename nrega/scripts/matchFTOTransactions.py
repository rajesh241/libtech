from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,getjcNumber,getFullFinYear,writeFile
from nregaSettings import nregaWebDir,nregaRawDataDir 
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable

from crawlFunctions import getDistrictParams
from crawlFunctions import alterMusterHTML,getMusterPaymentDate
from crawlFunctions import alterFTOHTML,genHTMLHeader,NICToSQLDate
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script to Populate FTO Details Table')
  parser.add_argument('-t', '--testMode', help='Script will run in TestMode', required=False,action='store_const', const=1)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-af', '--additionalFilters', help='please enter additional filters', required=False)
  parser.add_argument('-f', '--finyear', help='Please enter the finyear', required=True)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)
  args = vars(parser.parse_args())
  return args

def getMaxArrayIndex(myArray):
  curmax=0
  j=0
  for i in myArray:
    if i>curmax:
      curmax=i
      curindex=j
    j=j+1
  return curindex

def matchFunction(cur,logger,matchAlgo,jobcard,wagelistNo,ftoAmount,ftoNo,ftoName,ftoAccountNo):
  query="select id,name,accountNo from workDetails where jobcard='%s' and wagelistNo='%s' and totalWage='%s' and matchInProgress=0" % (jobcard,wagelistNo,ftoAmount)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  matchStatus="Fail"
  matchValueArray=[]
  matchTypeArray=[]
  wdIDArray=[]
  for row1 in results:
    rowid1=row1[0]
    musterName=row1[1]
    musterAccountNo=row1[2]
    matchCount=0
    matchType="noMatch"
    if ftoName.replace(" ","").lower() in musterName.replace(" ","").lower():
      matchCount = matchCount +1
      matchType="nameMatch"
    if ftoAccountNo == musterAccountNo:
      matchCount = matchCount +1
      if matchType=="nameMatch":
        matchType="nameAccountMatch"
      else:
        matchType="accountMatch"
    matchValueArray.append(matchCount)
    matchTypeArray.append(matchType)   
    wdIDArray.append(rowid1)
  #logger.info("Match Value Array: %s " %str(matchValueArray)) 
  #logger.info("Match Type Array: %s " %str(matchTypeArray))
  
  #If there is only one element with 2 or only one element with score 1 then we have a good match
  matchType="noMatch"
  wdID=None
  if len(matchValueArray) > 0:
    if matchAlgo=="single":
      if matchValueArray.count(2) == 1:
        matchIndex=matchValueArray.index(2)
        matchType=matchTypeArray[matchIndex]
        wdID=str(wdIDArray[matchIndex])
      elif matchValueArray.count(1) == 1:
        matchIndex=matchValueArray.index(1)
        matchType=matchTypeArray[matchIndex]
        wdID=str(wdIDArray[matchIndex])   
      elif len(matchValueArray) == 1:
        matchIndex=0
        matchType="nameAccountMismatch"
        wdID=str(wdIDArray[matchIndex])   
    elif matchAlgo=="multiple" and max(matchValueArray) > 0:
      matchIndex=getMaxArrayIndex(matchValueArray)
      matchType=matchTypeArray[matchIndex]
      wdID=str(wdIDArray[matchIndex])    
  
  if matchType != "noMatch":
    query="update workDetails set matchInProgress=1 where id=%s" % (str(wdID))
    cur.execute(query)
  else:
    wdID="NULL" 
  return matchType,wdID


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  
  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString="  "
  additionalFilter=''
  if args['district']:
    districtName=args['district'].lower()
  if args['finyear']:
    finyear=args['finyear'].lower()
  if args['additionalFilters']:
    additionalFilter=" and "+args['additionalFilters']
   
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)

  filepath=nregaRawDataDir.replace("districtName",districtName.lower())
  fullfinyear=getFullFinYear(finyear)
  
  query="select count(*) count, jobcard, applicantName, creditedAmount,wagelistNo,accountNo,ftoNo from ftoTransactionDetails where creditedAmount is not NULL and ((ftoMatchStatus is NULL) or (ftoMatchStatus='noMatch')) %s group by jobcard,applicantName,creditedAmount,wagelistNo,accountNo,ftoNo" % (additionalFilter) 
#  query="select count(*) count, jobcard, applicantName, creditedAmount,wagelistNo,accountNo,ftoNo from ftoTransactionDetails where creditedAmount is not NULL and ( (ftoMatchStatus='noMatch')) %s group by jobcard,applicantName,creditedAmount,wagelistNo,accountNo,ftoNo" % (additionalFilter) 
  query="select count(*) count, jobcard, applicantName, creditedAmount,wagelistNo,accountNo,ftoNo from ftoTransactionDetails where creditedAmount is not NULL and ( (ftoMatchStatus is NULL)) %s group by jobcard,applicantName,creditedAmount,wagelistNo,accountNo,ftoNo" % (additionalFilter) 
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    count = row[0]
    jobcard=row[1]
    ftoName=row[2]
    ftoAmount=str(row[3])
    wagelistNo=row[4]
    ftoAccountNo=row[5]
    ftoNo=row[6]
      
    if count == 1:
      matchAlgo="single"
    else:
      matchAlgo="multiple"

    #Need to make all matchInProgress=0
    query="update workDetails set matchInProgress=0"
    cur.execute(query)
    query="select id,primaryAccountHolder,rejectionReason,paymentMode,status,referenceNo,firstSignatoryDate,secondSignatoryDate,bankProcessedDate,transactionDate,processedDate from ftoTransactionDetails where jobcard='%s' and applicantName='%s' and creditedAmount=%s and wagelistNo='%s' and accountNo='%s' and ftoNo='%s'" % (jobcard,ftoName,ftoAmount,wagelistNo,ftoAccountNo,ftoNo)
    logger.info(query)
    cur.execute(query)
    results1=cur.fetchall()
    for row1 in results1:
      ftID=str(row1[0])
      matchType,wdID=matchFunction(cur,logger,matchAlgo,jobcard,wagelistNo,ftoAmount,ftoNo,ftoName,ftoAccountNo)
      logger.info(" %s : %s : %s : %s : %s" % (ftID,jobcard,str(count),matchType,str(wdID)) )
      query="update ftoTransactionDetails set updateWorkDetails=1,ftoMatchStatus='%s',wdID=%s where id=%s" % (matchType,str(wdID),ftID)
      logger.info(query)
      cur.execute(query)
#     if matchType != "noMatch":
#       primaryAccountHolder=row1[1]
#       rejectionReason=row1[2]
#       paymentMode=row1[3]
#       ftoStatus=row1[4]
#       referenceNo=row1[5]
#       firstSignatoryDateString=str(row1[6])
#       secondSignatoryDateString=str(row1[7])
#       bankProcessedDateString=str(row1[8])
#       transactionDateString=str(row1[9])
#       processedDateString=str(row1[10])
#       query="update workDetails set ftoNo='%s',ftoMatchStatus='%s',primaryAccountHolder='%s',rejectionReason='%s',paymentMode='%s',ftoAccountNo='%s',ftoStatus='%s',ftoAmount='%s',referenceNo='%s',ftoName='%s',updateDate=NOW() where id=%s" % (ftoNo,matchType,primaryAccountHolder,rejectionReason,paymentMode,ftoAccountNo,ftoStatus,ftoAmount,referenceNo,ftoName,wdID)
#       logger.info(query)
#       cur.execute(query)
#       query="update workDetails set firstSignatoryDate='%s',secondSignatoryDate='%s',transactionDate='%s',bankProcessedDate='%s',processedDate='%s',updateDate=NOW() where id=%s" % (firstSignatoryDateString,secondSignatoryDateString,transactionDateString,bankProcessedDateString,processedDateString,wdID)
#       logger.info(query) 
#       cur.execute(query)
        
                
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()


