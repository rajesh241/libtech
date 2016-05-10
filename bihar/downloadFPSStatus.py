from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
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
from globalSettings import datadir,nregaDataDir
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate Pds SHop codes from csv File')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-y', '--year', help='Year for which PDS needs to be downloaded', required=True)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-limit', '--limit', help='limit the number of shops that you want to download', required=False)
  parser.add_argument('-fps', '--fpsCode', help='Enter the FPS code of shop that you want to download data for', required=False)

  args = vars(parser.parse_args())
  return args

def main():
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
  inyear=args['year']
  
  logger.info(inyear)


  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString="  "
  additionalFilters=""
  if args['fpsCode']:
    additionalFilters=" where fpsCode='%s' " % (args['fpsCode'])
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  
  #Start Program here
  base_url = "http://sfc.bihar.gov.in/"
  driver.get("http://sfc.bihar.gov.in/login.htm")
  driver.get(base_url + "/fpshopsSummaryDetails.htm")
  Select(driver.find_element_by_id("year")).select_by_visible_text(inyear)
  time.sleep(5)

  query="select id,distCode,blockCode,fpsCode,distName,blockName,fpsName from pdsShops %s %s " % (additionalFilters,limitString)
  logger.info(query)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    distCode=row[1]
    blockCode=row[2]
    fpsCode=row[3]
    distName=row[4]
    blockName=row[5]
    fpsName=row[6]
    logger.info("disCode:%s   blockCode:%s  fpsCode:%s  distName:%s  blockName:%s  shopName:%s " % (distCode,blockCode,fpsCode,distName,blockName,fpsName))
  #myhtml=driver.page_source
  #print myhtml
  # End program here

  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
