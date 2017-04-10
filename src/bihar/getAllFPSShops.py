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
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
sys.path.insert(0, fileDir+'/../')
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from biharFunctions import cleanFPSName
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
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  
  #Start Program here

  base_url = "http://sfc.bihar.gov.in/"
  verificationErrors = []
  accept_next_alert = True
  driver.get("http://sfc.bihar.gov.in/login.htm")
  driver.get(base_url + "/fpshopsSummaryDetails.htm")
  Select(driver.find_element_by_id("year")).select_by_visible_text(inyear)
  time.sleep(10)
  select_box = driver.find_element_by_id("district_id") # if your select_box has a name.. why use xpath?..... this step could use either xpath or name, but name is sooo much easier.
  options = [x for x in select_box.find_elements_by_tag_name("option")] #this part is cool, because it searches the elements contained inside of select_box and then adds them to the list options if they have the tag name "options"
  for element in options:
    distCode=element.get_attribute("value") #
    distName=element.get_attribute("text") #
    logger.info("District Code: %s   District Name: %s " %(distCode,distName)) 
    Select(driver.find_element_by_id("district_id")).select_by_value(distCode)
    time.sleep(10)
    block_box = driver.find_element_by_id("block_id") # if your select_box has a name.. why use xpath?..... this step could use either xpath or name, but name is sooo much easier.
    blockOptions = [y for y in block_box.find_elements_by_tag_name("option")] #this part is cool, because it searches the elements contained inside of select_box and then adds them to the list options if they have the tag name "options"
    for blockElement in blockOptions:
      blockCode=blockElement.get_attribute("value") #
      blockName=blockElement.get_attribute("text") #
      logger.info("distCode:%s  distName:%s  blockCode:%s  blockName:%s " % (distCode,distName,blockCode,blockName))
      Select(driver.find_element_by_id("block_id")).select_by_value(blockCode)
      time.sleep(10)
      fps_box = driver.find_element_by_id("fpshop_id") # if your select_box has a name.. why use xpath?..... this step could use either xpath or name, but name is sooo much easier.
      fpsOptions = [z for z in fps_box.find_elements_by_tag_name("option")] #this part is cool, because it searches the elements contained inside of select_box and then adds them to the list options if they have the tag name "options"
      for fpsElement in fpsOptions:
        fpsCode=fpsElement.get_attribute("value") #
        fpsName=fpsElement.get_attribute("text") #
        
        myString=distCode+','+distName+','+blockCode+','+blockName+','+fpsCode+','+fpsName
	logger.info(myString)
        if "Select" in myString:
          logger.info("This will not be entered into Database")
        else: 
          fpsName1=cleanFPSName(fpsName)
          whereClause="where fpsCode='%s' and blockCode='%s' and distCode='%s' " % (fpsCode,blockCode,distCode)
          query="select * from pdsShops %s " % (whereClause)
          cur.execute(query)
          if cur.rowcount == 0:
            query="insert into pdsShops (fpsCode,blockCode,distCode) values ('%s','%s','%s') " % (fpsCode,blockCode,distCode)
            cur.execute(query)
          query="update pdsShops set distName='%s',blockName='%s',fpsName='%s' %s " % (distName,blockName,fpsName1,whereClause)
          logger.info(query) 
          cur.execute(query)



  # End program here

  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
