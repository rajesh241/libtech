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
from libtechFunctions import singleRowQuery
from globalSettings import datadir,nregaDataDir
def updatePrimaryAccountHolder(cur,logger,districtName):
  logger.info("Update Primary Account Holder")
  query="use %s " % districtName.lower()
  cur.execute(query)
  
  
def copyPhones(cur,logger):
  logger.info("Copy Start")
  query="use libtech"
  cur.execute(query)
  query="select jobcard,phone from jobcardPhone where jobcard like '%CH-05-%'" 
  cur.execute(query)
  results = cur.fetchall()
  query="use surguja"
  cur.execute(query)
  query="update jobcardRegister set phone='' "
  cur.execute(query)
  for row in results:
    jobcard=row[0]
    phone=row[1]
    logger.info(jobcard+phone)
    query="update jobcardRegister set phone='%s' where jobcard='%s' " % (phone,jobcard)
    cur.execute(query)

def updateRejectionReason(cur,logger,districtName):
  logger.info("Updating Rejection Reason")
  query="use %s " % districtName.lower()
  cur.execute(query)
  query="select wd.id,ft.rejectionReason from workDetails wd, ftoTransactionDetails ft where (wd.status='Rejected' or wd.status='InvalidAccount') and wd.jobcard=ft.jobcard and wd.accountNo=ft.accountNo and wd.wagelistNo=ft.wagelistNo and wd.totalWage=ft.creditedAmount"
  cur.execute(query)
  logger.info("NUMBERS OF RECORDS THAT WILL BE PROCESSED:" + str(cur.rowcount))
  results=cur.fetchall()
  for row in results:
    wdID=str(row[0])
    rejectionReason=row[1]
    query="update workDetails set updateDate=NOW(),rejectionReason='%s' where id=%s" % (rejectionReason,wdID)
    logger.info(query)

def updateFtoNo(cur,logger,districtName): 
  logger.info("Updating Rejection Reason")
  query="use %s " % districtName.lower()
  cur.execute(query)
  infinyear='16'
  query="select wd.id,ft.ftoNo,wd.status  from workDetails wd, ftoTransactionDetails ft  where wd.jobcard=ft.jobcard and wd.accountNo=ft.accountNo and wd.wagelistNo=ft.wagelistNo and wd.totalWage=ft.creditedAmount  and wd.ftoNoUpdated=0 and wd.finyear='%s' " %(infinyear)
  query="select wd.id,ft.ftoNo,wd.status  from workDetails wd, ftoTransactionDetails ft  where wd.jobcard=ft.jobcard and wd.name=ft.applicantName and wd.wagelistNo=ft.wagelistNo and wd.totalWage=ft.creditedAmount  and wd.ftoNoUpdated=0 and wd.finyear='%s' " %(infinyear)
  logger.info(query)
  cur.execute(query)
  logger.info("NUMBERS OF RECORDS THAT WILL BE PROCESSED:" + str(cur.rowcount))
  results=cur.fetchall()
  for row in results:
    wdID=str(row[0])
    ftoNo=row[1]
    status=row[2]
    ftoMonth=ftoNo[12:14]
    ftoYear=ftoNo[14:16]
    error=1
    if (int(infinyear) == int(ftoYear)) and (int(ftoMonth) <= 3):
      error=0
    if ((int(infinyear)-1) == int(ftoYear)) and ((int(ftoMonth) <= 12) and (int(ftoMonth)>3)):
      error=0
    if(error == 1):
      logger.info(str(wdID)+"   "+ftoNo+"   "+ftoMonth+"   "+ftoYear+"   "+str(error))
    if error==0:
      if(status.lower() == 'credited'):
        query="update workDetails set updateDate=NOW(),ftoNo='%s',ftoNoUpdated=1 where id=%s" % (ftoNo,wdID)
      else:
        query="update workDetails set updateDate=NOW(),ftoNo='%s' where id=%s" % (ftoNo,wdID)
      #logger.info(query) 
      cur.execute(query) 
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='HouseKeeping Script for SurGUJA Database')
  parser.add_argument('-cp', '--copyPhones', help='Copies the phones from Libtech Addressbook to Surguja JobCardRegister', required=False,action='store_const', const=1)
  parser.add_argument('-urr', '--updateRejectionReason', help='updates rejectionReason on workDetails', required=False,action='store_const', const=1)
  parser.add_argument('-ufn', '--updateFtoNo', help='Updates FTONo to Work Details', required=False,action='store_const', const=1)
  parser.add_argument('-upa', '--updatePrimaryAccountHolder', help='Updates Primary Account HOlder', required=False,action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  if args['district']:
    districtName=args['district'].lower()

  query="select state from crawlDistricts where name='%s'" % districtName.lower()
  cur.execute(query)
  if cur.rowcount == 0:
    logger.info("INVALID DISTRICT ENTERED")
  else:
    stateName=singleRowQuery(cur,query)
    query="use %s " % districtName.lower()
    cur.execute(query)
   
  if args['copyPhones']:
    logger.info("Copying Phones from libtech to Surguja Database")
    copyPhones(cur,logger)
  if args['updateRejectionReason']:
    logger.info("This loop will update RejectionReason")
    updateRejectionReason(cur,logger,districtName)
  if args['updateFtoNo']:
    logger.info("This loop will update FTONo")
    updateFtoNo(cur,logger,districtName)
  if args['updatePrimaryAccountHolder']:
    logger.info("This loop will update Primary Account Holder")
    updatePrimaryAccountHolder(cur,logger,districtName)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
