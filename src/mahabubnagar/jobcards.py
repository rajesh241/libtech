#! /usr/bin/env python

import time
import re

from bs4 import BeautifulSoup
from MySQLdb import IntegrityError

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize
from wrappers.db import dbInitialize,dbFinalize


#######################
# Global Declarations
#######################

delay = 5

class Context():
  def __init__(self):
    self.url = "http://www.nrega.telangana.gov.in/"
    self.logger = None
    self.display = None
    self.driver = None


#############
# Functions
#############

def jobcardList(logger, db, filter=None):
  if filter:
    filter = ' ' + filter
  else:
    filter = ' '

  query = "select jobcard from jobcardRegister" + filter
  logger.info('Executing query: [%s]', query)
  cur = db.cursor()
  cur.execute(query)
  jobcard_array = list(cur.fetchall())
  jobcards = [ x[0] for x in jobcard_array ]
  return jobcards
  
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Jobcard script for crawling, downloading & parsing')
  parser.add_argument('-c', '--crawl', help='Crawl the jobcards numbers and populate database', required=False, action='store_const', const=True)
  parser.add_argument('-d', '--download', help='Download the jobcards & musters for each jobcard ID', required=False, action='store_const', const=True)
  parser.add_argument('-p', '--parse', help='Parse the jobcards & musters downloaded', required=False, action='store_const', const=True)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)

  args = vars(parser.parse_args())
  return args


def wdFetch(driver, logger, url):
  driver.get(url)

  driver.find_element_by_link_text("Wage Seekers").click()
  driver.find_element_by_link_text("Job Card Holders Information").click()

  elem = driver.find_element_by_name("District")
  elem.send_keys("Mahabubnagar")
  elem.click()
  time.sleep(delay)

  elem = driver.find_element_by_name("Mandal")
  elem.send_keys("Ghattu")
  elem.click()
  time.sleep(delay)

  return driver


def wdFetchPanchayat(driver, cur, logger, panchayatName):
  elem = driver.find_element_by_name("Go")
  elem.click()

  curtime = time.strftime('%Y-%m-%d %H:%M:%S')
  html_source = driver.page_source
  htmlsoup=BeautifulSoup(html_source)
  try:
    table=htmlsoup.find('table',id="sortable")
    rows = table.findAll('tr')
    td = table.find('td')
    logger.info("DATA[", td.text, "]")
    logger.debug(rows)
    status=1
  except:
    status=0

  jcDownloaded = os.listdir('./musters')
  
  if status==1:
    for tr in rows:
      td = tr.findNext('td')
      logger.debgu("DATA1[" + td.text + "]")
      td = td.findNext('td')
      logger.debug("DATA2[" + td.text + "]")
      jcno = td.text.strip()
      logger.info("jcno [%s]", jcno)
      if jcno+'.csv' in jcDownloaded:
        continue
      
      if True:
        elem = driver.find_element_by_link_text(jcno)
        elem.click()
        time.sleep(1)

      parent_handle = driver.current_window_handle
      print "Handles : ", driver.window_handles, "Number : ", len(driver.window_handles)

      

      if len(driver.window_handles) == 2:
        driver.switch_to_window(driver.window_handles[-1])
      else:
        logger.error("Handlers gone wrong [" + str(driver.window_handles) + "]")
        driver.save_screenshot('./logs/button_'+jcno+'.png')
        continue

      # Download the muster details
      try:
        elem = WebDriverWait(driver, timeout).until(
          EC.presence_of_element_located((By.ID, "sortable"))
        )
        driver.find_element_by_name("Go").click()
      except NoSuchElementException, TimeoutException:
          logger.error("Failed to locate Muster Roll Button")
          driver.save_screenshot('./logs/button_'+jcno+'.png')
          driver.close()
          driver.switch_to_window(parent_handle)
          continue

      if False:
        # Download the html file for parsing later
        html_file = open('./musters/'+jcno+'.html', 'w')
        html_file.write(jc_html)
        html_file.close

      retries = 0
      while not os.path.isfile('Muster'):
        time.sleep(delay)
        retries += 1
        if retries > 10:
          logger.error("Timed out waiting for Muster excel")
          driver.save_screenshot('./logs/download_wait_'+jcno+'.png')
          driver.close()
          driver.switch_to_window(parent_handle)
          continue

      if False:
        cmd = 'libreoffice --headless --convert-to csv Muster --outdir musters'
        os.system(cmd)
        os.rename('./musters/Muster.csv', './musters/'+jcno+'.xls')
        os.system('rm Muster')
      else:
        cmd = 'ssconvert Muster ./musters/'+jcno+'.csv'
        os.system(cmd)
        os.system('rm Muster')
      
      driver.close()
      driver.switch_to_window(parent_handle)
      query="update jobcardRegister set isProcessed=1 where jobcard='"+jcno+"'"
      cur.execute(query)

def dbFetch(db, logger):
  # Query to get all the blocks
  query="select stateCode,districtCode,blockCode,name from blocks"
  logger.info('query: [%s]', query)
  cur=db.cursor()
  cur.execute(query)
  results = cur.fetchall()
  logger.info('results: [%s]', str(results))

  return results


def crawlJobcards(driver, db, logger, url):
  '''
  Crawl the page for the jobcards and update them in the database
  '''
  driver = wdFetch(driver, logger, url)

  jobcards = jobcardList(logger, db)
  logger.debug("jobcards[%s]" % str(jobcards))

  query="select stateCode,districtCode,blockCode,name from blocks"
  logger.info('Executing query: [%s]', query)
  cur=db.cursor()
  cur.execute(query)
  block_details = cur.fetchall()
  logger.info('block_details: [%s]', str(block_details))

  (stateCode, districtCode, blockCode, blockName) = block_details[0]

  query="select name,panchayatCode,id from panchayats where jobcardCrawlStatus=0 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
  logger.info("Executing query[%s]", query)
  cur.execute(query)
  panchresults = cur.fetchall()
  logger.info("panchresults[%s]", panchresults)

  for panchayat_details in panchresults:
    (panchayatName, panchayatCode, panchID)=panchayat_details
    logger.info("stateCode[%s],districtCode[%s],blockCode[%s],blockName[%s],panchayatCode[%s],panchayatName[%s]" % (stateCode,districtCode,blockCode,blockName,panchayatCode,panchayatName))
    elem = driver.find_element_by_name("Panchayat")
    elem.send_keys(panchayatName)
    elem.click()
    time.sleep(delay)

    elem = driver.find_element_by_name("Go")
    elem.click()
    
    curtime = time.strftime('%Y-%m-%d %H:%M:%S')
    html_source = driver.page_source
    htmlsoup=BeautifulSoup(html_source)
    filename = './panchayats/' + panchayatName + '.html'
    with open(filename, 'w') as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(driver.page_source.encode('utf-8'))
    
    try:
      table=htmlsoup.find('table',id="sortable")
      rows = table.findAll('tr')
      logger.debug(rows)
      status=1
    except:
      logger.warning("There was an exception")
      status=0

    query="update panchayats set jobcardCrawlStatus="+str(status)+", jobcardCrawlDate='"+curtime+"' where id="+str(panchID) 
    logger.info("Executing query[%s]", query)
    cur.execute(query)

    if status==1:
      for tr in rows:
        td = tr.findNext('td')
        logger.info("Sl No[" + td.text + "]")
        td = td.findNext('td')
        logger.debug("Jobcard ID[" + td.text + "]")
        jcno = td.text.strip()
        logger.info("jobcard[%s]" % jcno)
        td = td.findNext('td')
        logger.debug("Govt of India Jobcard ID[" + td.text + "]")
        gjcno = td.text.strip()
        logger.debug("gjcno[%s]", gjcno)
        td = td.findNext('td')
        logger.debug("Head of the family[" + td.text + "]")
        hof = td.text
        logger.debug("HOF[%s]" % hof)
        td = td.findNext('td')
        regDate = td.text
        logger.debug("Registration Date[%s]" % regDate)
        issueDate = "STR_TO_DATE('"+regDate+"','"+"%d/%m/%Y')"
        logger.debug("issueDate[%s]" % issueDate)
        td = td.findNext('td')
        caste = td.text
        logger.debug("Caste[%s]" % caste)
                        
        if jcno in jobcards:
          pass
          query='update jobcardRegister set govtJobcard="%s",stateCode="%s",headOfFamily="%s",issueDate="%s",caste="%s",districtCode="%s",blockCode="%s",panchayatCode="%s" where jobcard="%s")' % (gjcno, stateCode, hof, issueDate, caste, districtCode, blockCode, panchayatCode, jcno)
          logger.warning("Letting pass for now. Need to update with query[%s]" % query)
          continue
        else:          
          query="insert into jobcardRegister (jobcard,govtJobcard,stateCode,headOfFamily,issueDate,caste,districtCode,blockCode,panchayatCode) values ('"+jcno+"','"+gjcno+"','"+stateCode+"','"+hof+"',"+issueDate+",'"+caste+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"')"
          
        logger.info("Executing query[%s]", query)
        try:
          cur.execute(query)
        except IntegrityError,e:
          logger.error("Attempting to insert duplicate [%s]" % e)


def crawlJobcards2(driver, db, logger, url):
  '''
  Crawl the page for the jobcards and update them in the database
  '''

  for panchayat_details in panchresults:
    (panchayatName, panchayatCode, panchID)=panchayat_details
    logger.info("stateCode[%s],districtCode[%s],blockCode[%s],blockName[%s],panchayatCode[%s],panchayatName[%s]" % (stateCode,districtCode,blockCode,blockName,panchayatCode,panchayatName))
    elem = driver.find_element_by_name("Panchayat")
    elem.send_keys(panchayatName)
    elem.click()
    time.sleep(delay)

    elem = driver.find_element_by_name("Go")
    elem.click()
    
    curtime = time.strftime('%Y-%m-%d %H:%M:%S')
    html_source = driver.page_source
    htmlsoup=BeautifulSoup(html_source)
    filename = './panchayats/' + panchayatName + '.html'
    with open(filename, 'w') as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(driver.page_source.encode('utf-8'))
    
    try:
      table=htmlsoup.find('table',id="sortable")
      rows = table.findAll('tr')
      td = table.find('td')
      logger.info("Sl No[" + td.text + "]")
      logger.debug(rows)
      status=1
    except:
      logger.warning("There was an exception")
      status=0

    query="update panchayats set jobcardCrawlStatus="+str(status)+", jobcardCrawlDate='"+curtime+"' where id="+str(panchID) 
    logger.info("Executing query[%s]", query)
    cur.execute(query)

    if status==1:
      for tr in rows:
        td = td.findNext('td')
        logger.debug("Jobcard ID[" + td.text + "]")
        jcno = td.text.strip()
        logger.debug("jobcard[%s]" % jcno)
        td = td.findNext('td')
        logger.debug("Govt of India Jobcard ID[" + td.text + "]")
        gjcno = td.text.strip()
        logger.debug("gjcno[%s]", gjcno)
        td = td.findNext('td')
        logger.debug("Head of the family[" + td.text + "]")
        hof = td.text
        logger.debug("HOF[%s]" % hof)
        td = td.findNext('td')
        regDate = td.text
        logger.debug("Registration Date[%s]" % regDate)
        issueDate = "STR_TO_DATE('"+regDate+"','"+"%d/%m/%Y')"
        logger.debug("issueDate[%s]" % issueDate)
        td = td.findNext('td')
        caste = td.text
        logger.debug("Caste[%s]" % caste)
                        
        if jcno in jobcards:
          pass
          # query='update jobcardRegister set govtJobcard="%s",stateCode="%s",headOfFamily="%s",issueDate="%s",caste="%s",districtCode="%s",blockCode="%s",panchayatCode="%s" where jobcard="%s")' % (gjcno, stateCode, hof, issueDate, caste, districtCode, blockCode, panchayatCode, jcno)
        else:          
          query="insert into jobcardRegister (jobcard,govtJobcard,stateCode,headOfFamily,issueDate,caste,districtCode,blockCode,panchayatCode) values ('"+jcno+"','"+gjcno+"','"+stateCode+"','"+hof+"',"+issueDate+",'"+caste+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"')"
          
        logger.info("Executing query[%s]", query)
        try:
          cur.execute(query)
        except IntegrityError,e:
          logger.error("Attempting to insert duplicate [%s]" % e)

        continue  # Mynk


def downloadJobcards(driver, db, logger):
  '''
  Crawl the page for the jobcards and update them in the database
  '''
  wdFetch(driver, logger)

  if False:
    results = dbFetch(db, logger)
    cur=db.cursor()

  cur=db.cursor()

  query="select j.stateCode,j.districtCode,j.blockCode,j.panchayatCode,p.name,b.name from jobcardRegister j, panchayats p, blocks b where j.blockCode=p.blockCode and j.panchayatCode=p.panchayatCode and j.blockCode=b.blockCode and j.isProcessed=0 group by j.blockCode,j.panchayatCode"  # Mynk
  print query
  cur.execute(query)
  print "count: ", cur.rowcount
  if cur.rowcount:
    results = cur.fetchall()
    print "Data:", results
    for row in results:
      stateCode=row[0]
      districtCode=row[1]
      blockCode=row[2]
      panchayatCode=row[3]
      panchayatName=row[4]
      blockName=row[5]
      print panchayatName, blockName 

      wdFetchPanchayat(driver, cur, logger, panchayatName)

  if False:
      query="select jobcard from jobcardRegister where isDownloaded=0 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' and panchayatCode='"+panchayatCode+"' limit 50"
      cur.execute(query)
      jcresults = cur.fetchall()
      for jcrow in jcresults:
        jobcard=jcrow[0]
        i=i+1
        print str(i)+"  "+jobcard
        elem = driver.find_element_by_link_text(jobcard)
        elem.click()
        time.sleep(5)
        jcsource = driver.page_source
        driver.back()
        time.sleep(2)
        myhtml=jcsource.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
        jcfilename=jcfilepath+blockName+"/"+panchayatName.upper()+"/jobcardRegister/"+jobcard.replace("/","_")+".html"
        if not os.path.exists(os.path.dirname(jcfilename)):
          os.makedirs(os.path.dirname(jcfilename))
        myfile = open(jcfilename, "w")
        myfile.write(myhtml.encode("UTF-8"))
        query="update jobcardRegister set isDownloaded=1 where jobcard='"+jobcard+"'"
        cur.execute(query)
        # End of Dead IF

      time.sleep(delay)
  time.sleep(delay)


def downloadJobcardsViaBruteForce(driver, db, logger):
  '''
  Crawl the page for the jobcards and update them in the database
  '''
  wdFetch(driver, logger)

  results = dbFetch(db, logger)
  cur=db.cursor()

  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    blockName=row[3]

  query="select name,panchayatCode,id from panchayats where stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
  #print query
  cur.execute(query)
  panchresults = cur.fetchall()
  #print panchresults

  for panchrow in panchresults:
    panchayatName=panchrow[0]
    panchayatCode=panchrow[1]
    panchID=panchrow[2]
    #print stateCode+districtCode+blockCode+blockName+panchayatCode+panchayatName

    wdFetchPanchayat(driver, cur, logger, panchayatName)

    time.sleep(delay)
  time.sleep(delay)

def extractJobcards(db):
  jobcards = jobcardList(db, "where panchayatCode=003")
  #print jobcards

  for jc in jobcards:
    cmd = 'cp -v ./musters/'+jc+'.* ./musters/Thumalacheruvu/'
    print cmd
    os.system(cmd)

def contextFinalize(self):
  logger = self.logger
  if self.db:
    dbFinalize(self.db)
    self.db = None
    
  if self.display:
    displayFinalize(self.display)
    self.display = None
    
  if self.driver:
    #driverFinalize(self.driver)
    self.driver.quit() # Mynk
    self.driver = None
  logger.info("Context Finalized")

def contextCleanup(context):
  logger = context.logger
  logger.info("Context Cleanup...")
  contextFinalize(context)
  logger.info("Context Cleanup...")


def contextRegister(context):
  import atexit
  atexit.register(contextCleanup, context)
  context.logger.info("Context Initialized")  

def contextInitialize(self, logger, args):
  self.logger = logger
  self.db = dbInitialize(db="mahabubnagar")
  self.display = displayInitialize(args['visible'])
  if args['visible']:
    delay=5
  else:
    delay=1
  self.driver = driverInitialize(args['browser'])
  # contextRegister(self)
  logger.info("Context Initialized")


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")

  context = Context()
  contextInitialize(context, logger, args)

  if args['crawl']:
    crawlJobcards(context.driver, context.db, context.logger, context.url)
  else:
    downloadJobcards(context.driver, context.db, context.logger)
    # extractJobcards(driver, db, logger)

  contextFinalize(context)

  logger.info("...END PROCESSING")

  exit(0)

if __name__ == '__main__':
  main()

