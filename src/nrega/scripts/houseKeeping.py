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
from libtechFunctions import singleRowQuery,getjcNumber
from globalSettings import datadir,nregaDataDir

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='HouseKeeping Script for SurGUJA Database')
  parser.add_argument('-cp', '--copyPhones', help='Copies the phones from Libtech Addressbook to Surguja JobCardRegister', required=False,action='store_const', const=1)
  parser.add_argument('-rfi', '--revertFTOInformation', help='Revert back FTO information, if rfiID is give it will revert back only for that ID', required=False,action='store_const', const=1)
  parser.add_argument('-ujc', '--updateJCNumber', help='updates JCNumber in jobcardRegister', required=False,action='store_const', const=1)
  parser.add_argument('-rfiID', '--revertWorkID', help='revert FTO Information for Work Details ID', required=False)
  parser.add_argument('-upa', '--updatePrimaryAccountHolder', help='Updates Primary Account HOlder', required=False,action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of log entries', required=False)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-f', '--finyear', help='Please enter the Financial Year', required=True)

  args = vars(parser.parse_args())
  return args

def updateJCNumber(cur,logger,districtName,finyear,limitString):
  query="select id,jobcard from jobcardRegister %s " % limitString
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    jobcard=row[1]
    jcNumber=getjcNumber(jobcard) 
    query=" update jobcardRegister set jcNumber='%s' where id=%s " % (jcNumber,rowid)
    logger.info(query)
    cur.execute(query)

def updateFtoNo(cur,logger,districtName,finyear,limitString):
  #match objects jobcard,name,accountNo,amount,wagelistNo
  query="select id,jobcard,name,accountNo,wagelistNo,totalWage,finyear from workDetails where finyear='%s'  and ftoMatchStatus is NULL and musterStatus !='' %s " % (finyear,limitString)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    jobcard=row[1]
    applicantName=row[2]
    accountNo=row[3]
    wagelistNo=row[4]
    totalWage=row[5]
    finyear=row[6]
    logger.info("rowid %s " % rowid)
    query="select ftoNo,applicantName,accountNo,primaryAccountHolder,referenceNo,rejectionReason from ftoTransactionDetails where jobcard='%s'   and wagelistNo='%s' and creditedAmount='%s' and finyear='%s'" % (jobcard,wagelistNo,totalWage,finyear)
    logger.info(query)
    cur.execute(query)
    status='error'
    if cur.rowcount >= 1:
      results1=cur.fetchall()
      nameMatch=0
      accountMatch=0
      matchStrengthLatched=0
      for row1 in results1:
        matchStrength=0
        ftoAccountNo=row1[2]
        ftoName=row1[1]
        if ftoAccountNo == accountNo:
          accountMatch=1
          matchStrength = 1
        if applicantName==ftoName:
          nameMatch=1
          matchStrength = 2
        if nameMatch == 1 and accountMatch==1:
          matchStrength = 3
        if matchStrength > matchStrengthLatched:
          matchStrengthLatched = matchStrength
          rejectionReason=row1[5]
          primaryAccountHolder=row1[3]
          ftoAccountNoLatched=ftoAccountNo
          ftoNameLatched=ftoName
          ftoNo=row1[0]
          referenceNo=row1[4]
       
      matchArray=["nameMisMatchAccountMisMatch","nameMismatchAccountMatch","nameMatchAccountMismatch","allMatch"]
      status=matchArray[matchStrengthLatched]
    logger.info("%s %s" % (rowid,status))
    query="update workDetails set ftoMatchStatus='%s' where id=%s" % (status,rowid)
    cur.execute(query)
    #if status != 'error':
    #  query="update workDetails set rejectionReason='%s',primaryAccountHolder='%s',ftoNo='%s',referenceNo='%s',creditedAccountNo='%s' where id=%s" % (rejectionReason,primaryAccountHolder,ftoNo,referenceNo,ftoAccountNo,rowid)
      #cur.execute(query)
 
def revertFTOInformation(cur,logger,wdID):
  query="update workDetails set ftoNo=NULL,ftoMatchStatus=NULL,primaryAccountHolder=NULL,rejectionReason=NULL,paymentMode=NULL,ftoAccountNo=NULL,ftoStatus=NULL,ftoAmount=NULL,referenceNo=NULL,ftoName=NULL,firstSignatoryDate=NULL,secondSignatoryDate=NULL,transactionDate=NULL,bankProcessedDate=NULL,processedDate=NULL,updateDate=NOW() where id=%s" % (str(wdID))
  #logger.info(query)
  cur.execute(query)

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  if args['district']:
    districtName=args['district'].lower()
  finyear=args['finyear']
  db = dbInitialize(db=districtName, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  limitString=''
  if args['limit']:
    limitString="limit "+str(args['limit'])
   
# if args['copyPhones']:
#   logger.info("Copying Phones from libtech to Surguja Database")
#   copyPhones(cur,logger)
# if args['updateRejectionReason']:
#   logger.info("This loop will update RejectionReason")
#   updateRejectionReason(cur,logger,districtName)
# if args['updateFinYear']:
#   logger.info("This loop will update financial year in workDetails")
#   updateFinYear(cur,logger,districtName,limitString)
  if args['revertFTOInformation']:
    logger.info("This loop will update FTO Information")
    if args['revertWorkID']:
      wdID=args['revertWorkID']
      revertFTOInformation(cur,logger,wdID)
    else:
      query="select id from workDetails where finyear='%s' order by id DESC %s" % (finyear,limitString)
      cur.execute(query)
      results=cur.fetchall()
      for row in results:
        wdID=row[0]
        revertFTOInformation(cur,logger,wdID)
  if args['updateJCNumber']:
    logger.info("This will update jcNumber")
    updateJCNumber(cur,logger,districtName,finyear,limitString)
# if args['updatePrimaryAccountHolder']:
#   logger.info("This loop will update Primary Account Holder")
#   updatePrimaryAccountHolder(cur,logger,districtName)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()


