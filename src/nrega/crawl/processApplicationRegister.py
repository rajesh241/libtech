from bs4 import BeautifulSoup
import multiprocessing, time
import requests
import MySQLdb
import os
import os.path
import time
import re
import sys
from MySQLdb import OperationalError
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
import datetime
from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from crawlSettings import nregaDB 
from crawlSettings import nregaWebDir,nregaRawDataDir,tempDir
from crawlFunctions import alterHTMLTables,writeFile,getjcNumber,NICToSQLDate,getFullFinYear

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing Jobcards')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  limitString=''
  if args['limit']:
    limitString=" limit %s " % args['limit']
  additionalFilters=" "
  if args['district']:
    additionalFilters+= " and p.districtName='%s' " % args['district']
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

  
  query="select p.stateCode,p.districtCode,p.blockCode,p.panchayatCode,p.stateName,p.districtName,p.rawBlockName,p.panchayatName,p.fullPanchayatCode,p.stateShortCode,p.crawlIP from panchayats p,panchayatStatus ps where p.fullPanchayatCode=ps.fullPanchayatCode and p.isRequired=1 and ps.jobcardCrawlDate is not NULL and ( (ps.jobcardProcessDate is NULL) or (ps.jobcardCrawlDate > ps.jobcardProcessDate) ) %s order by ps.jobcardCrawlDate DESC,fullPanchayatCode %s" % (additionalFilters,limitString)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [stateCode,districtCode,blockCode,panchayatCode,stateName,districtName,blockName,panchayatName,fullPanchayatCode,stateShortCode,crawlIP]=row
    filepath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
    filename=filepath+blockName.upper()+"/%s/%s_jobcardRegister.html" % (panchayatName.upper(),panchayatName.upper())
    logger.info(filename)
    jobcardPrefix="%s-" % (stateShortCode)
    if os.path.isfile(filename):
      logger.info("File Exists: now we should process it")
      f=open(filename,"rb")
      myhtml=f.read()
      htmlsoup=BeautifulSoup(myhtml,"html.parser")
      tables=htmlsoup.findAll('table')
      caste=""
      for table in tables:
        if "IAY/LR" in str(table):
          logger.info("Found the Table")
          rows=table.findAll("tr")
          for row in rows:
            logger.info("I am inside the row")
            cols=row.findAll("td")
            if len(cols) > 10:
              jobcardDate=cols[9].text
              if jobcardPrefix in jobcardDate:
                logger.info(jobcardDate)
                jobcard=cols[9].find("nobr").text
                logger.info("Processing Jobcard: %s " % jobcard)
                issueDate=jobcardDate.replace(jobcard,"")
                applicantName=cols[4].text.strip()
                status=""
                if "*" in applicantName: 
                  applicantName=cols[4].text.replace("*","").strip()
                  status="deleted"
                logger.info(applicantName)
                curCaste=cols[2].text.strip()
                if curCaste!='':
                  caste=curCaste
                gender=cols[6].text.strip() 
                logger.info("Jobcard %s , date %s applicantName %s Caste %s Gender %s " % (jobcard,issueDate,applicantName,caste,gender))
                applicantName=applicantName.replace("'","\\'") 
                query="select id from applicantDetails where jobcard='%s' and name='%s' " % (jobcard,applicantName)
                cur.execute(query)
                if cur.rowcount == 0: 
                  query="insert into applicantDetails (jobcard,name) values ('%s','%s') " % (jobcard,applicantName)
                  cur.execute(query)
                  rowid=cur.lastrowid
                else:
                  row=cur.fetchone()
                  rowid=row[0]
                
                query="update applicantDetails set caste='%s',gender='%s' where id=%s " %(caste,gender,str(rowid))
                cur.execute(query)
      query="update panchayatStatus set jobcardProcessDate=NOW() where fullPanchayatCode='%s' " % (fullPanchayatCode)
      cur.execute(query)
                
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
