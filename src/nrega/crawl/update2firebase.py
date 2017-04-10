import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
from libtechFunctions import singleRowQuery,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from crawlSettings import nregaDB 
from firebase import firebase
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  from firebase import firebase
  firebase = firebase.FirebaseApplication('https://libtech-app.firebaseio.com/', None)
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  args = argsFetch()
  finyear='17'
  fullfinyear=getFullFinYear(finyear)
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  blockCode='005'
  fullBlockCode='0515005'
  panchayatCodes="(panchayatCode = '%s' or panchayatCode='%s')" % ('029','034')
  districtName="muzaffarpur"
  query="SET NAMES utf8"
  cur.execute(query)
  result = firebase.delete('https://libtech-app.firebaseio.com', None)

  query="select blockName,panchayatName from panchayats where rawDistrictName='%s' and blockCode='%s' and %s " %(districtName,blockCode,panchayatCodes)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [blockName,panchayatName]=row
    result = firebase.post('https://libtech-app.firebaseio.com/geo/%s'%(blockName.upper()), {'panchayatName': panchayatName.upper()})

  query="select DISTINCT(jobcard),blockName,panchayatName from workDetails where fullBlockCode='%s' and finyear='17' and %s" %(fullBlockCode,panchayatCodes)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [jobcard1,blockName,panchayatName]=row
    jobcard=jobcard1.replace("/","_")
    logger.info(jobcard)
    result = firebase.post('https://libtech-app.firebaseio.com/jobcard/%s/%s/'%(blockName.upper(),panchayatName.upper()), {'jobcard': jobcard})

  #  print(result)
  query="select  panchayatName, jobcard, name, musterNo, workName, totalWage, wagelistNo, ftoNo, musterStatus, bankNamePostOffice, date_format(dateTo, '%d-%M-%Y') as dateTo, DATE_FORMAT(firstSignatoryDate, '%d-%M-%Y') as firstSignatoryDate, DATE_FORMAT(secondSignatoryDate, '%d-%M-%Y') as secondSignatoryDate, DATE_FORMAT(transactionDate, '%d-%M-%Y') as transactionDate, DATE_FORMAT(bankProcessedDate, '%d-%M-%Y') as bankProcessedDate, DATE_FORMAT(paymentDate, '%d-%M-%Y') as paymentDate, DATE_FORMAT(creditedDate, '%d-%M-%Y') as creditedDate, ftoMatchStatus, rejectionReason, @varMaxDate:=greatest(COALESCE(dateTo, '1900-01-01 00:00:00'),   COALESCE(firstSignatoryDate,    '1900-01-01 00:00:00'),   COALESCE(secondSignatoryDate,    '1900-01-01 00:00:00'),   COALESCE(transactionDate, '1900-01-01 00:00:00'),   COALESCE(bankProcessedDate, '1900-01-01 00:00:00'),   COALESCE(paymentDate, '1900-01-01 00:00:00'),   COALESCE(creditedDate, '1900-01-01 00:00:00')) as maxDate, CASE @varMaxDate WHEN dateTo THEN 'dateTo' WHEN firstSignatoryDate THEN 'firstSignatoryDate' WHEN secondSignatoryDate THEN 'secondSignatoryDate' WHEN transactionDate THEN 'transactionDate' WHEN bankProcessedDate THEN 'bankProcessedDate' WHEN paymentDate THEN 'paymentDate' WHEN creditedDate THEN 'creditedDate' END AS maxDateColName from workDetails  where fullBlockCode='0515005' and finyear='17' and (panchayatCode='029' or panchayatCode='034') order by dateTo "
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    panchayatName = row[0].upper()
    jobcard = row[1]
    jobcard = jobcard.replace('/', '_')
    name = row[2]
    musterNo = row[3]
    workName = row[4]
    totalWage = row[5]
    wagelistNo = row[6]
    ftoNo = row[7]
    musterStatus = row[8]
    bankNameOrPOName = row[9]
    dateTo = row[10]
    firstSignatoryDate = row[11]
    secondSignatoryDate = row[12]
    transactionDate = row[13]
    bankProcessedDate = row[14]
    paymentDate = row[15]
    creditedDate = row[16]
    ftoStatus = row[17]
    rejectionReason = row[18]
    maxDate = row[19]
    maxDateColName = row[20]
    try:
        currentStatusOfNode = firebase.get('/data/%s/%s/%s'%(panchayatName, jobcard, dateTo), None)
        currentNoTransactionsForDate = len(currentStatusOfNode) - 1
        newTransactionNo = currentNoTransactionsForDate + 1
    except: 
        newTransactionNo = 1
    result = firebase.patch('https://libtech-app.firebaseio.com/data/%s/%s/%s/%s'%(panchayatName, jobcard, dateTo, newTransactionNo), {'jobcard': jobcard, 'name': name, 'musterNo': musterNo, 'workName': workName, 'totalWage': totalWage, 'wagelistNo': wagelistNo, 'ftoNo': ftoNo, 'musterStatus': musterStatus, 'bankNameOrPOName': bankNameOrPOName, 'dateTo': dateTo, 'firstSignatoryDate': firstSignatoryDate, 'secondSignatoryDate': secondSignatoryDate, 'transactionDate': transactionDate, 'bankProcessedDate': bankProcessedDate, 'paymentDate': paymentDate, 'creditedDate': creditedDate, 'ftoStatus': ftoStatus, 'rejectionReason': rejectionReason, 'maxDate': maxDate, 'maxDateColName': maxDateColName})
    #print(result)
 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()

