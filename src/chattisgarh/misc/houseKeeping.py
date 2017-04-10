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
def updateFinYear(cur,logger,districtName,limitString):
  logger.info("Updating Financial Year in ftoTransactionDetails")
  query="select ftd.ftoNo,f.finyear from ftoTransactionDetails ftd,ftoDetails f where f.ftoNo=ftd.ftoNo group by ftd.ftoNo %s " %(limitString)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    ftoNo=row[0]
    finyear=row[1]
    query="update ftoTransactionDetails set finyear='%s' where ftoNo='%s' " % (finyear,ftoNo)
    logger.info(query)
    cur.execute(query)

def updateFtoNo(cur,logger,districtName,limitString):
  #match objects jobcard,name,accountNo,amount,wagelistNo
  query="select id,jobcard,name,accountNo,wagelistNo,totalWage,finyear from workDetails where finyear='17' and blockCode='003' and status='Rejected' %s " % (limitString)
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
    query="select ftoNo,applicantName from ftoTransactionDetails where jobcard='%s'  and accountNo='%s' and wagelistNo='%s' and creditedAmount='%s' and finyear='%s'" % (jobcard,accountNo,wagelistNo,totalWage,finyear)
    logger.info(query)
    cur.execute(query)
    status='error'
    if cur.rowcount >= 1:
      results1=cur.fetchall()
      nameMatch=0
      for row1 in results1:
        ftoNo=row1[0]
        ftoName=row1[1]
        if applicantName==ftoName:
          nameMatch=1
      if nameMatch == 1:
         status='allMatch'
      else:
         status='nameMismatch'
    logger.info("%s %s" % (rowid,status))
    query="update workDetails set ftoMatchStatus='%s' where id=%s" % (status,rowid)
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
  parser.add_argument('-ufy', '--updateFinYear', help='Update Financial Year in ftoTransactionDetails', required=False,action='store_const', const=1)
  parser.add_argument('-upa', '--updatePrimaryAccountHolder', help='Updates Primary Account HOlder', required=False,action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of log entries', required=False)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  if args['district']:
    districtName=args['district'].lower()
  db = dbInitialize(db=districtName, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  limitString=''
  if args['limit']:
    limitString="limit "+str(args['limit'])
   
  if args['copyPhones']:
    logger.info("Copying Phones from libtech to Surguja Database")
    copyPhones(cur,logger)
  if args['updateRejectionReason']:
    logger.info("This loop will update RejectionReason")
    updateRejectionReason(cur,logger,districtName)
  if args['updateFinYear']:
    logger.info("This loop will update financial year in workDetails")
    updateFinYear(cur,logger,districtName,limitString)
  if args['updateFtoNo']:
    logger.info("This loop will update FTONo")
    updateFtoNo(cur,logger,districtName,limitString)
  if args['updatePrimaryAccountHolder']:
    logger.info("This loop will update Primary Account Holder")
    updatePrimaryAccountHolder(cur,logger,districtName)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()


#def updateFtoNo(cur,logger,districtName): 
#  logger.info("Updating Rejection Reason")
#  query="use %s " % districtName.lower()
#  cur.execute(query)
#  infinyear='16'
#  query="select wd.id,ft.ftoNo,wd.status  from workDetails wd, ftoTransactionDetails ft  where wd.jobcard=ft.jobcard and wd.accountNo=ft.accountNo and wd.wagelistNo=ft.wagelistNo and wd.totalWage=ft.creditedAmount  and wd.ftoNoUpdated=0 and wd.finyear='%s' " %(infinyear)
#  query="select wd.id,ft.ftoNo,wd.status  from workDetails wd, ftoTransactionDetails ft  where wd.jobcard=ft.jobcard and wd.name=ft.applicantName and wd.wagelistNo=ft.wagelistNo and wd.totalWage=ft.creditedAmount  and wd.ftoNoUpdated=0 and wd.finyear='%s' " %(infinyear)
#  logger.info(query)
#  cur.execute(query)
#  logger.info("NUMBERS OF RECORDS THAT WILL BE PROCESSED:" + str(cur.rowcount))
#  results=cur.fetchall()
#  for row in results:
#    wdID=str(row[0])
#    ftoNo=row[1]
#    status=row[2]
#    ftoMonth=ftoNo[12:14]
#    ftoYear=ftoNo[14:16]
#    error=1
#    if (int(infinyear) == int(ftoYear)) and (int(ftoMonth) <= 3):
#      error=0
#    if ((int(infinyear)-1) == int(ftoYear)) and ((int(ftoMonth) <= 12) and (int(ftoMonth)>3)):
#      error=0
#    if(error == 1):
#      logger.info(str(wdID)+"   "+ftoNo+"   "+ftoMonth+"   "+ftoYear+"   "+str(error))
#    if error==0:
#      if(status.lower() == 'credited'):
#        query="update workDetails set updateDate=NOW(),ftoNo='%s',ftoNoUpdated=1 where id=%s" % (ftoNo,wdID)
#      else:
#        query="update workDetails set updateDate=NOW(),ftoNo='%s' where id=%s" % (ftoNo,wdID)
#      #logger.info(query) 
#      cur.execute(query) 
# 
