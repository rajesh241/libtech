from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from urllib import urlencode
import httplib2
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../nrega/crawl/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from crawlFunctions import alterHTMLTables
from pdsFunctions import cleanFPSName,writeFile
from globalSettings import datadir,nregaDataDir
from pdsSettings import pdsDB,pdsRawDataDir,pdsWebDirRoot
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate Pds SHop codes from csv File')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-y', '--year', help='Year for which PDS needs to be downloaded', required=True)
  parser.add_argument('-m', '--month', help='Month for which PDS needs to be downloaded', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-f', '--fpsCode', help='FPS shop for which data needs to be donwloaded', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  httplib2.debuglevel = 1
  monthLabels=['0','JAN','FEB','MAR','APR','MAY','JUNE','JULY','AUG','SEP','OCT','NOV','DEC']
  searchText='class="newFormTheme"'
  replaceText='class="newFormTheme" id="newFormTheme"'
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db=pdsDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  fpsYear=args['year']
  if args['month']:
    monthArray=[args['month']]
  else:
    monthArray=[1,2,3,4,5,6,7,8,9,10,11,12]
  fpsFilter=''
  if args['fpsCode']:
    fpsFilter=" and fpsCode='%s'" % args['fpsCode']

  logger.info(fpsYear)
  additionalFilter=" and districtCode != '1001' "
  query="select id,stateCode,districtCode,blockCode,fpsCode,stateName,districtName,blockName,fpsName from fpsShops where isRequired=1 %s %s" % (additionalFilter,fpsFilter)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [rowid,stateCode,districtCode,blockCode,fpsCode,stateName,districtName,blockName,fpsName] = row
    logger.info("Processing state: %s district: %s, block: %s ShopName : %s " % (stateName,districtName,blockName,fpsName))
    fpsNameFiltered=cleanFPSName(fpsName)
    for fpsMonth in monthArray: 
      fpsMonthName=monthLabels[int(fpsMonth)]   
      rawfilename="%s/%s/%s/%s/%s/%s/%s.html" % (pdsRawDataDir,stateName,districtName,blockName,fpsYear,fpsMonthName,fpsNameFiltered)
      filename="%s/%s/%s/%s/%s/%s/%s.html" % (pdsWebDirRoot,stateName,districtName,blockName,fpsYear,fpsMonthName,fpsNameFiltered)
      logger.info("filename %s " % filename)
      if os.path.isfile(filename):
        f=open(filename,'r')
        fpsHtml=f.read()
        fpsArray=fpsHtml.split('Date of Delivered. : ')
        if len(fpsArray) > 1:
          dateOfDelivery=fpsArray[1][0:10]
          logger.info("Date of Delivery %s " % (dateOfDelivery))
          dateFormat="%d-%m-%Y"
          dateString="STR_TO_DATE('%s', '%s')" % (dateOfDelivery,dateFormat)
          query="select id from fpsStatus where fpsCode='%s' and year=%s and month=%s " % (fpsCode,str(fpsYear),str(fpsMonth))
          logger.info(query)
          cur.execute(query)
          if cur.rowcount ==0:
            query="insert into fpsStatus (fpsCode,year,month) values ('%s',%s,%s)" % (fpsCode,str(fpsYear),str(fpsMonth))
            logger.info(query)
            cur.execute(query)
          query="update fpsStatus set deliveryDate=%s where fpsCode='%s' and year=%s and month=%s " % (dateString,fpsCode,str(fpsYear),str(fpsMonth)) 
          logger.info(query)
          cur.execute(query)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
