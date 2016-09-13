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
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,writeFile
from nregaSettings import nregaRawDataDir
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from crawlFunctions import getDistrictParams
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Crawl Jobcard Register')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-blockCode', '--blockCode', help='BlockCode for  which you need to Download', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of panchayats to be processed', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  districtName=args['district']
  logger.info("DistrictName "+districtName)
  limitString=''
  if args['limit']:
    limitString=" limit %s " % args['limit']
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  additionalFilters = ''
  if args['blockCode']:
    additionalFilters=" and b.blockCode='%s' " % args['blockCode']
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  jobcardPrefix="%s-%s" % (stateShortCode,districtCode)
  logger.info("crawlIP "+crawlIP)
  logger.info("State Name "+stateName)
  jcReportRawFilePath=nregaRawDataDir.replace("districtName",districtName.lower())
  #Start Program here
  url="http://nrega.nic.in/netnrega/sthome.aspx"
  driver.get(url)
  elem = driver.find_element_by_link_text(stateName)
  elem.send_keys(Keys.RETURN)
  time.sleep(1)
  elem = driver.find_element_by_link_text(districtName.upper())
  elem.send_keys(Keys.RETURN)
  time.sleep(1)
  #Query to get all the blocks
  query="select b.blockCode,b.name,p.panchayatCode,p.name from blocks b,panchayats p where b.blockCode=p.blockCode and p.isRequired=1 and p.jobcardCrawlDate is not NULL and TIMESTAMPDIFF(HOUR, p.accountCrawlDate, now()) > 10  order by p.accountCrawlDate %s %s" % (additionalFilters,limitString)
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    blockCode=row[0]
    blockName=row[1]
    panchayatCode=row[2]
    panchayatName=row[3]
    panchayatNameOnlyLetters=re.sub(r"[^A-Za-z]+", '', panchayatName)
    elem = driver.find_element_by_link_text(blockName)
    elem.send_keys(Keys.RETURN)
    elem = driver.find_element_by_link_text(panchayatName)
    elem.send_keys(Keys.RETURN)
#    elem = driver.find_element_by_link_text("List of Worker with Aadhar No.(UID No.)")
    elem = driver.find_element_by_link_text("List of Worker with Aadhar No.(UID No.)")
    elem.send_keys(Keys.RETURN)
    time.sleep(15)
    jcsource = driver.page_source
    rawhtml=jcsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    jcfilename=jcReportRawFilePath+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/jobcardRegister/workerList.html"
    logger.info(jcfilename)
    writeFile(jcfilename,rawhtml)
    driver.back()

    elem = driver.find_element_by_link_text("Download Panchayatwise MGNREGA Bank A/C Detail")
    elem.send_keys(Keys.RETURN)
    time.sleep(15)
    jcsource = driver.page_source
    rawhtml=jcsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    jcfilename=jcReportRawFilePath+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/jobcardRegister/workerListBank.html"
    logger.info(jcfilename)
    writeFile(jcfilename,rawhtml)
    driver.back()
    
    elem = driver.find_element_by_link_text("Download Panchayatwise MGNREGA Post Office Account Detail")
    elem.send_keys(Keys.RETURN)
    time.sleep(15)
    jcsource = driver.page_source
    rawhtml=jcsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    jcfilename=jcReportRawFilePath+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/jobcardRegister/workerListPO.html"
    logger.info(jcfilename)
    writeFile(jcfilename,rawhtml)
    driver.back()
    
    elem = driver.find_element_by_link_text("Download Panchayat Wise MGNREGA Co-operative Bank A/C Detail")
    elem.send_keys(Keys.RETURN)
    time.sleep(15)
    jcsource = driver.page_source
    rawhtml=jcsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    jcfilename=jcReportRawFilePath+blockName.upper()+"/"+panchayatNameOnlyLetters.upper()+"/jobcardRegister/workerListCoBank.html"
    logger.info(jcfilename)
    writeFile(jcfilename,rawhtml)
    driver.back()
    
    


    time.sleep(5)
    driver.back()
    time.sleep(5)
    driver.back()
    query="update panchayats set accountCrawlDate=now() where blockCode='%s' and panchayatCode='%s' " % (blockCode,panchayatCode)
    cur.execute(query)
    



  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()

