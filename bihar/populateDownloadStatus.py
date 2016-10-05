from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
import datetime
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
sys.path.insert(0, fileDir+'/../')
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from biharSettings import pdsDataDir
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from urllib import urlencode
import httplib2
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate PDS Shops DownloadStatus Table')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  #parser.add_argument('-y', '--year', help='Year for which PDS needs to be downloaded', required=True)
  parser.add_argument('-limit', '--limit', help='limit the number of shops that you want to download', required=False)
  parser.add_argument('-d', '--distCode', help='Enter the Dist code of district that you want to download data for', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  httplib2.debuglevel = 1
  monthLabels=['0','JAN','FEB','MAR','APR','MAY','JUNE','JULY','AUG','SEP','OCT','NOV','DEC']
  now = datetime.datetime.now()
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db="biharPDS", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  logger.info("Current Year: %s Current Month: %s " %(str(now.year),str(now.month)))
    

  years=['2015','2016']
 # years=['2016']
  query="select distCode,blockCode,fpsCode from pdsShops where isRequired=1"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    distCode=row[0]
    blockCode=row[1]
    fpsCode=row[2]
    logger.info("distCode %s blockCode %s fpsCode %s " % (distCode,blockCode,fpsCode))
    for inyear in years:
      month=0
      while month < 12:
        month=month+1
        if ( (now.year > int(inyear)) or ((now.year == int(inyear)) and (now.month >= month)) ):
          #logger.info("Year: %s   Month: %s " % (str(inyear),str(month)))
          whereClause=" psd.distCode='%s' and psd.blockCode='%s' and psd.fpsCode='%s' and psd.fpsMonth='%s' and psd.fpsYear='%s' " % (distCode,blockCode,fpsCode,str(month),str(inyear))
          query="select isDownloaded,statusRemark from pdsShopsDownloadStatus psd where %s" %(whereClause)
         # logger.info(query)
          cur.execute(query)
          if cur.rowcount == 0:
            query="insert into pdsShopsDownloadStatus (distCode,blockCode,fpsCode,fpsMonth,fpsYear) values ('%s','%s','%s','%s','%s')" % (distCode,blockCode,fpsCode,str(month),str(inyear))
            #logger.info(query)
            cur.execute(query)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
