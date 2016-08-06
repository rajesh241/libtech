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
  parser.add_argument('-urr', '--updateRejectionReason', help='updates rejectionReason on workDetails', required=False,action='store_const', const=1)
  parser.add_argument('-ujc', '--updateJCNumber', help='updates JCNumber in jobcardRegister', required=False,action='store_const', const=1)
  parser.add_argument('-ufn', '--updateFtoNo', help='Updates FTONo to Work Details', required=False,action='store_const', const=1)
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
  query="select id,jobcard,name,accountNo,wagelistNo,totalWage,finyear from workDetails where finyear='%s'  and status !='' %s " % (finyear,limitString)
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
      for row1 in results1:
        ftoNo=row1[0]
        ftoName=row1[1]
        ftoAccountNo=row1[2]
        primaryAccountHolder=row1[3]
        referenceNo=row1[4]
        rejectionReason=row1[5]
        if ftoAccountNo == accountNo:
          accountMatch=1
          if applicantName==ftoName:
            nameMatch=1
      if nameMatch == 1 and accountMatch==1:
         status='allMatch'
      elif accountMatch == 1:
         status='nameMismatchAccountMatch'
      elif nameMatch == 1:
         status='nameMatchAccountMismatch'
      else:
         status='nameMisMatchAccountMisMatch'
    logger.info("%s %s" % (rowid,status))
    query="update workDetails set ftoMatchStatus='%s' where id=%s" % (status,rowid)
    cur.execute(query)
    if status != 'error':
      query="update workDetails set rejectionReason='%s',primaryAccountHolder='%s',ftoNo='%s',referenceNo='%s',creditedAccountNo='%s' where id=%s" % (rejectionReason,primaryAccountHolder,ftoNo,referenceNo,ftoAccountNo,rowid)
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
  if args['updateFtoNo']:
    logger.info("This loop will update FTONo")
    updateFtoNo(cur,logger,districtName,finyear,limitString)
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


