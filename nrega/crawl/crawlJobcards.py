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
  additionalFilters=''
  if args['district']:
    additionalFilters+= " and p.districtName='%s' " % args['district']
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

  
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])

  url="http://nrega.nic.in/netnrega/sthome.aspx"
  driver.get(url)

  query="select p.stateCode,p.districtCode,p.blockCode,p.panchayatCode,p.stateName,p.districtName,p.rawBlockName,p.panchayatName,p.fullPanchayatCode,p.stateShortCode,p.crawlIP from panchayats p,panchayatStatus ps where p.fullPanchayatCode=ps.fullPanchayatCode and p.isRequired=1 %s order by ps.jobcardCrawlDate,fullPanchayatCode %s" % (additionalFilters,limitString)
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [stateCode,districtCode,blockCode,panchayatCode,stateName,districtName,blockName,panchayatName,fullPanchayatCode,stateShortCode,crawlIP]=row
    filepath=nregaWebDir.replace("stateName",stateName.upper()).replace("districtName",districtName.upper())
    filename=filepath+blockName.upper()+"/%s/%s_jobcardRegister.html" % (panchayatName.upper(),panchayatName.upper())
    logger.info(filename)
    jobcardPrefix="%s-%s" % (stateShortCode,districtCode)
    logger.info("Processing %s-%s-%s-%s " % (stateName,districtName,blockName,panchayatName))
    elem = driver.find_element_by_link_text(stateName)
    elem.send_keys(Keys.RETURN)
    time.sleep(1)
    elem = driver.find_element_by_link_text(districtName.upper())
    elem.send_keys(Keys.RETURN)
    time.sleep(1)
    elem = driver.find_element_by_link_text(blockName)
    elem.send_keys(Keys.RETURN)
    time.sleep(1)
    compareText="Panchayat_Code=%s" % fullPanchayatCode
    elems = driver.find_elements_by_xpath("//a[@href]")
    foundCode=0
    for elem in elems:
      hrefLink=str(elem.get_attribute("href"))
      if compareText in hrefLink:
        logger.info("Found the Code")
        foundCode=1
        break
    #elem = driver.find_element_by_link_text(panchayatName)
    if foundCode==1:
      elem.send_keys(Keys.RETURN)
      time.sleep(1)
      #Before thsi lets download the applicatn Register:
      elem = driver.find_element_by_link_text("Registration Application Register")
      elem.send_keys(Keys.RETURN)
      time.sleep(5)
      html_source = driver.page_source
      #filename="%s/%s.html" % (tempDir,panchayatName)
      writeFile(filename,html_source) 
      driver.back()
      
      elem = driver.find_element_by_link_text("Job card/Employment Register")
      elem.send_keys(Keys.RETURN)
      time.sleep(5)
      curtime = time.strftime('%Y-%m-%d %H:%M:%S')
      html_source = driver.page_source
      htmlsoup=BeautifulSoup(html_source,"html.parser")
      try:
        table=htmlsoup.find('table',align="center")
        rows = table.findAll('tr')
        status=1
      except:
        status=0
      query="update panchayatStatus set jobcardCrawlDate=NOW() where fullPanchayatCode='%s'"%fullPanchayatCode 
      logger.info(query)
      cur.execute(query)
      logger.info("Status is " + str(status))
      if status==1:
        for tr in rows:
          cols = tr.findAll('td')
          jclink=''
          for link in tr.find_all('a'):
            jclink=link.get('href')
          if len(cols) > 2:
            jcno="".join(cols[1].text.split())
            headOfFamily=cols[2].text.replace("'","").lstrip().rstrip()
          logger.info("%s-%s" % (jcno,jobcardPrefix))
          if jobcardPrefix in jcno:
            logger.info(jcno)
            jcNumber=getjcNumber(jcno)
            query="select * from jobcards where jobcard='%s' " % jcno
            cur.execute(query)
            if cur.rowcount == 0:
              query="insert into jobcards (name,jobcard,stateCode,districtCode,blockCode,panchayatCode,fullPanchayatCode) values ('"+headOfFamily+"','"+jcno+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"',"+fullPanchayatCode+")"
              logger.info(query)
              cur.execute(query)

    driver.back()
    driver.back()
    driver.back()
    driver.back()
    driver.back()


  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
