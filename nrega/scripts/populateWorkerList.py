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
from nregaSettings import nregaRawDataDir
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable

from crawlFunctions import getDistrictParams
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script to Populate WorkerDetails')
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-af', '--additionalFilters', help='Please enter any additional Filters', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)
  args = vars(parser.parse_args())
  return args
  
def populateWorkerList(cur,logger,filename,eachFileType):
  if os.path.isfile(filename):
    myhtml=open(filename,'r').read()
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    if "No Record Found !!!" in str(myhtml):
      logger.info("No Records Found !!!")
    else:
      try:
        tables=htmlsoup.findAll('table')
        errorflag=0
      except:
        errorflag=1
      logger.info("Error flag is %s " % str(errorflag))
      for table in tables:
        if "Registration No." in str(table):
          logger.info("Found the table with Registration Number")
          rows=table.findAll('tr')
          for row in rows:
            if "Registration No." in str(row):
              logger.info("This is a header Row")
            else:
              cols=row.findAll('td')
              if eachFileType=='workerList':
                jobcard=cols[2].text
                applicantNo=cols[4].text
                applicantName=cols[5].text
                gender=cols[6].text
                age=cols[7].text
                aadharNo=cols[9].text
              elif eachFileType=='workerListPO':
                jobcard=cols[5].text
                applicantNo=cols[6].text
                applicantName=cols[7].text
                accountType='post'
                accountNo=cols[11].text
                primaryAccountHolder=cols[12].text
                bankCode=''
                bankNameOrPOName=cols[9].text
                branchCodeOrPOCode=cols[8].text
                branchNameOrPOAddress=cols[10].text
                IFSCCodeOrEMOCode=cols[14].text
                MICRCodeOrSanchayCode=cols[15].text
                accountFrozen=cols[18].text
              elif eachFileType=="workerListBank":
                jobcard=cols[5].text
                applicantNo=cols[6].text
                applicantName=cols[7].text
                accountType='bank'
                accountNo=cols[12].text
                primaryAccountHolder=cols[15].text
                bankCode=cols[8].text
                bankNameOrPOName=cols[9].text
                branchCodeOrPOCode=cols[10].text
                branchNameOrPOAddress=cols[11].text
                IFSCCodeOrEMOCode=cols[13].text
                MICRCodeOrSanchayCode=cols[14].text
                accountFrozen=cols[21].text
              elif eachFileType=="workerListCoBank":
                jobcard=cols[5].text
                applicantNo=cols[6].text
                applicantName=cols[7].text
                accountType='coBank'
                accountNo=cols[12].text
                primaryAccountHolder=cols[14].text
                bankCode=cols[8].text
                bankNameOrPOName=cols[9].text
                branchCodeOrPOCode=cols[10].text
                branchNameOrPOAddress=cols[11].text
                IFSCCodeOrEMOCode=''
                MICRCodeOrSanchayCode=cols[13].text
                accountFrozen=cols[20].text
              
              logger.info(jobcard)
              query="select * from jobcardDetails where jobcard='%s' and applicantNo=%s" % (jobcard,applicantNo)
              logger.info(query)
              cur.execute(query)
              if cur.rowcount == 0:
                logger.info("Need to create entry")
                query="insert into jobcardDetails (jobcard,applicantNo) values ('%s',%s) " % (jobcard,applicantNo)
                logger.info(query)
                cur.execute(query)
              if eachFileType=="workerList":
                query="update jobcardDetails set applicantName='%s',gender='%s',age=%s,aadharNo='%s' where jobcard='%s' and applicantNo=%s " % (applicantName,gender,age,aadharNo,jobcard,applicantNo)
              else:
                query="update jobcardDetails set applicantName='%s',accountNo='%s',primaryAccountHolder='%s',bankCode='%s',bankNameOrPOName='%s',branchCodeOrPOCode='%s',branchNameOrPOAddress='%s',IFSCCodeOrEMOCode='%s',MICRCodeOrSanchayCode='%s',accountFrozen='%s',accountType='%s' where jobcard='%s' and applicantNo=%s " % (applicantName,accountNo,primaryAccountHolder,bankCode,bankNameOrPOName,branchCodeOrPOCode,branchNameOrPOAddress,IFSCCodeOrEMOCode,MICRCodeOrSanchayCode,accountFrozen,accountType,jobcard,applicantNo)
              logger.info(query)
              cur.execute(query) 
              
            
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  
  limitSetting=''
  additionalFilter=''
  if args['district']:
    districtName=args['district'].lower()
  additionalFilters='' 
  if args['additionalFilters']:
    additionalFilters=args['additionalFilters']
  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString="  "
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
  htmlDir=nregaRawDataDir.replace("districtName",districtName.lower())
  query="select b.blockCode,b.name,p.panchayatCode,p.name,p.id from blocks b,panchayats p where b.blockCode=p.blockCode and p.isRequired=1 and (accountProcessDate is NULL or accountProcessDate < accountCrawlDate) and accountCrawlDate is not NULL  %s %s" % (additionalFilters,limitString)
  logger.info(query)
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    blockCode=row[0]
    blockName=row[1]
    panchayatCode=row[2]
    panchayatName=row[3]
    rowid=str(row[4])
    filenames=["workerList","workerListBank","workerListCoBank","workerListPO"]
    filenames=["workerListPO"]
    for eachFileType in filenames:
      filename="%s/%s/%s/jobcardRegister/%s.html" % (htmlDir,blockName.upper(),panchayatName.upper(),eachFileType)
      logger.info(filename)
      populateWorkerList(cur,logger,filename,eachFileType)
    
    query="update panchayats set accountProcessDate=NOW() where id=%s" % rowid
    logger.info(query)
    cur.execute(query)

    errorflag=1

#   if errorflag ==0:
#     logger.info("Error Flag is zero")
#     for tr in rows:
#       if "Registration No" not in str(tr):
#         cols = tr.findAll('td')
#         if len(cols) > 9:
#           jobcard=cols[2].text
#           applicantNo=cols[4].text
#           applicantName=cols[5].text.replace(",","")
#           gender=cols[6].text
#           age=cols[7].text
#           aadharNo=cols[9].text
#           query="select jobcard from jobcardDetails where jobcard='%s' and applicantNo=%s" %(jobcard,applicantNo)
#           cur.execute(query)
#           if cur.rowcount == 0:
#             query="insert into jobcardDetails (jobcard,applicantNo) values ('%s',%s) " %(jobcard,applicantNo)
#             cur.execute(query)
#           query="update jobcardDetails set applicantName='%s',gender='%s',age=%s,aadharNo='%s' where jobcard='%s' and applicantNo=%s" %(applicantName,gender,age,aadharNo,jobcard,applicantNo)
#           logger.info(query)
#           cur.execute(query) 
#           logger.info(jobcard)
#
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
