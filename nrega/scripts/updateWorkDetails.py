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
def formatDate(indate):
  if indate is None:
    outdate="NULL"
  else:
    outdate="'%s'" % (str(indate))
  return outdate
 
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

  query="select id,primaryAccountHolder,rejectionReason,paymentMode,status,referenceNo,firstSignatoryDate,secondSignatoryDate,bankProcessedDate,transactionDate,processedDate,applicantName,accountNo,ftoNo,creditedAmount,ftoMatchStatus,wdID from ftoTransactionDetails where ftoMatchStatus is not NULL and ftoMatchStatus != 'noMatch' and updateWorkDetails=1 and finyear='%s' %s %s" % (finyear,additionalFilter,limitString)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row1 in results:
    rowid=str(row1[0])
    wdID=str(row1[16])
    primaryAccountHolder=row1[1]
    rejectionReason=row1[2]
    paymentMode=row1[3]
    ftoStatus=row1[4]
    referenceNo=row1[5]
    firstSignatoryDateString=formatDate(row1[6])
    secondSignatoryDateString=formatDate(row1[7])
    bankProcessedDateString=formatDate(row1[8])
    transactionDateString=formatDate(row1[9])
    processedDateString=formatDate(row1[10])
    ftoName=row1[11]
    ftoAccountNo=row1[12]
    ftoNo=row1[13]
    ftoAmount=str(row1[14])
    matchType=row1[15]
    query="update workDetails set ftoNo='%s',ftoMatchStatus='%s',primaryAccountHolder='%s',rejectionReason='%s',paymentMode='%s',ftoAccountNo='%s',ftoStatus='%s',ftoAmount='%s',referenceNo='%s',ftoName='%s',updateDate=NOW() where id=%s" % (ftoNo,matchType,primaryAccountHolder,rejectionReason,paymentMode,ftoAccountNo,ftoStatus,ftoAmount,referenceNo,ftoName,wdID)
    logger.info(query)
    cur.execute(query)
    query="update workDetails set firstSignatoryDate=%s,secondSignatoryDate=%s,transactionDate=%s,bankProcessedDate=%s,processedDate=%s,updateDate=NOW() where id=%s" % (firstSignatoryDateString,secondSignatoryDateString,transactionDateString,bankProcessedDateString,processedDateString,wdID)
    logger.info(query) 
    cur.execute(query)
    query="update ftoTransactionDetails set updateWorkDetails=0 where id=%s " % rowid
    logger.info(query) 
    cur.execute(query)
    

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
