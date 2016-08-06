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
from globalSettings import nregaDir,nregaRawDir
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
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)
  args = vars(parser.parse_args())
  return args
  
 
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
  htmlDir=nregaRawDir.replace("districtName",districtName.lower())
  query="select b.blockCode,b.name,p.panchayatCode,p.name from blocks b,panchayats p where b.blockCode=p.blockCode and p.isRequired=1 and jobcardCrawlDate is not NULL  %s %s" % (additionalFilters,limitString)
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    blockCode=row[0]
    blockName=row[1]
    panchayatCode=row[2]
    panchayatName=row[3]
    workerListFile="%s/%s/%s/%s/jobcardRegister/workerList.html" % (htmlDir,districtName.upper(),blockName.upper(),panchayatName.upper())
    logger.info(workerListFile)
    errorflag=1
    if os.path.isfile(workerListFile):
      musterhtml=open(workerListFile,'r').read()
      htmlsoup=BeautifulSoup(musterhtml,"html.parser")
      try:
        table=htmlsoup.find('table',bordercolor="black")
        rows = table.findAll('tr')
        errorflag=0
      except:
        errorflag=1

    if errorflag ==0:
      logger.info("Error Flag is zero")
      for tr in rows:
        if "Registration No" not in str(tr):
          cols = tr.findAll('td')
          if len(cols) > 9:
            jobcard=cols[2].text
            applicantNo=cols[4].text
            applicantName=cols[5].text.replace(",","")
            gender=cols[6].text
            age=cols[7].text
            aadharNo=cols[9].text
            query="select jobcard from jobcardDetails where jobcard='%s' and applicantNo=%s" %(jobcard,applicantNo)
            cur.execute(query)
            if cur.rowcount == 0:
              query="insert into jobcardDetails (jobcard,applicantNo) values ('%s',%s) " %(jobcard,applicantNo)
              cur.execute(query)
            query="update jobcardDetails set applicantName='%s',gender='%s',age=%s,aadharNo='%s' where jobcard='%s' and applicantNo=%s" %(applicantName,gender,age,aadharNo,jobcard,applicantNo)
            logger.info(query)
            cur.execute(query) 
            logger.info(jobcard)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
