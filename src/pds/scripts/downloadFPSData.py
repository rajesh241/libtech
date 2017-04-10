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
from urllib.parse import urlencode
import httplib2
import datetime
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
from pdsFunctions import cleanFPSName,writeFile,writeFile3

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
  now = datetime.datetime.now()
  fpsYear=args['year']
  logger.info(fpsYear+str(now.year))
  if (str(fpsYear) == str(now.year)):
    maxMonth=now.month
  else:
    maxMonth=12
  logger.info("The Maximum Month is %s " % str(maxMonth))

  if args['month']:
    monthArray=[args['month']]
  else:
    monthArray=[1,2,3,4,5,6,7,8,9,10,11,12]
  fpsFilter=''
  if args['fpsCode']:
    fpsFilter=" and fpsCode='%s'" % args['fpsCode']
  additionalFilter=" and districtCode != '1001' "
  logger.info(fpsYear)
  query="select id,stateCode,districtCode,blockCode,fpsCode,stateName,districtName,blockName,fpsName from fpsShops where isRequired=1 %s %s" % (additionalFilter,fpsFilter)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [rowid,stateCode,districtCode,blockCode,fpsCode,stateName,districtName,blockName,fpsName] = row
    logger.info("Processing state: %s fpsCode: %s district: %s, block: %s ShopName : %s " % (stateName,fpsCode,districtName,blockName,fpsName))
    fpsNameFiltered=cleanFPSName(fpsName)
    i=0
    while i < maxMonth:
      i=i+1 
      fpsMonthName=monthLabels[int(i)]   
      rawfilename="%s/%s/%s/%s/%s/%s/%s.html" % (pdsRawDataDir,stateName,districtName,blockName,fpsYear,fpsMonthName,fpsNameFiltered)
      filename="%s/%s/%s/%s/%s/%s/%s.html" % (pdsWebDirRoot,stateName,districtName,blockName,fpsYear,fpsMonthName,fpsNameFiltered)
      #filename1="%s/%s/%s/%s/%s/%s/a.html" % (pdsWebDirRoot,stateName,districtName,blockName,fpsYear,fpsMonthName)

      hlib = httplib2.Http('.cache')
      url = 'http://sfc.bihar.gov.in/fpshopsSummaryDetails.htm'
 
      data = {
       'mode':'searchFPShopDetails',
       'dyna(state_id)':'10',
       'dyna(fpsCode)':'',
       'dyna(scheme_code)':'',
       'dyna(year)':fpsYear,
       'dyna(month)':str(i),
       'dyna(district_id)':districtCode,
       'dyna(block_id)':blockCode,
       'dyna(fpshop_id)':fpsCode,
       }
 
      #print(urlencode(data))
      response, fpsHtml = hlib.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})
      logger.info("Download Response : %s" % response)
      logger.info("File Name : %s " % filename)
      title="%s_%s-%s" % (str(fpsYear),fpsMonthName,fpsNameFiltered)
      fpsHtml=fpsHtml.decode("UTF-8").replace(searchText,replaceText)
      fpsHtml=fpsHtml.encode("UTF-8")
      tableID=['newFormTheme']
      fpsHtmlWeb=alterHTMLTables(fpsHtml,title,tableID)
      logger.info(filename)
      mpa = dict.fromkeys(range(32))
      filename=filename.translate(mpa)
      writeFile3(filename,fpsHtmlWeb.encode("UTF-8"))
 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
