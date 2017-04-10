from bs4 import BeautifulSoup
import multiprocessing, time
import requests
import os
import os.path
import time
import re
import sys
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
  parser.add_argument('-j', '--jobcard', help='Jobcard for which HTMl needs tobe downloaded', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args

def downloadJobcardHTML(logger, driver, jobcard):
  '''
  Download the Jobcard HTML with payment info (Muster Details)
  '''
  
  jobcard_url = 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=HouseholdInf_engRH&actionVal=SearchJOB&JOB_No='
  url = jobcard_url + jobcard

  logger.info("Fetching...[%s]" % url)
  driver.get(url)
  logger.info("Fetched [%s]" % driver.title)

  if driver.title != ':: Job Card Holders Information ::':
    logger.info("Refreshing...[%s]" % url)
    driver.get(url)    # A double refresh required for the page to load
    logger.info("Refreshed [%s]" % driver.title) 

  html_source = driver.page_source.replace('<head>',
                                         '<head><meta http-equiv="Content-Type" '
                                          'content="text/html; charset=utf-8"/>').encode('utf-8')
  logger.debug("HTML Fetched [%s]" % html_source)

  bs = BeautifulSoup(html_source, "html.parser")
  span = bs.find('span',attrs={'class':'rpt-hd-txt'})
  if not span:
    logger.error("Span not found for jobcard[%s]" % (jobcard))
    return None

  """
  query = None
  ''' Update Only if there is a change for Google Drive will sync '''
  if os.path.exists(filename):
    with open(filename, 'r+') as html_file:
      cur_source = html_file.read()
      bs2 = BeautifulSoup(cur_source, "html.parser")
      
      if (bs.find(id='main3') != bs2.find(id='main3')):
        html_file.seek(0)
        html_file.write(html_source.decode('utf-8'))
        html_file.truncate()
        logger.info("Updating [%s]" % filename)
      else:
        logger.info("Skipping as no update")
        query = 'update jobcardRegister set downloadDate="%s", isDownloaded=1 where jobcard="%s"' % (strftime('%Y-%m-%d %H:%M:%S'), jobcard)
  else:
    with open(filename, 'w') as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(html_source.decode('utf-8'))

  if not query:
    query = 'update jobcardRegister set downloadDate="%s", isDownloaded=1, isProcessed=0 where jobcard="%s"' % (strftime('%Y-%m-%d %H:%M:%S'), jobcard)
  logger.info('Executing query: [%s]', query)
  cur = db.cursor()
  cur.execute(query)
  """
  return html_source


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  
  if args['jobcard']:
    jobcard=args['jobcard']
  else:
    jobcard='141975701001010679'

  logger.info("Fetching Jobcard[%s]..." % jobcard)

  html = downloadJobcardHTML(logger, driver, jobcard)
  logger.info(html)

  driverFinalize(driver)
  displayFinalize(display)
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
