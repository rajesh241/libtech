#! /usr/bin/env python

import os
import time
from bs4 import BeautifulSoup

import sys
sys.path.insert(0, '../../')

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize
from wrappers.db import dbInitialize,dbFinalize


#######################
# Global Declarations
#######################

delay = 0
url="http://khadya.cg.nic.in/pdsonline/cgfsa/Report/FrmRation_Patra_Allot_VerificationDistWise_Aug14.aspx"


#############
# Functions
#############

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Jobcard script for crawling, downloading & parsing')
  parser.add_argument('-c', '--crawl', help='Crawl the pds reports', required=False, action='store_const', const=True)
  parser.add_argument('-p', '--prev', help='Parse the jobcards & musters downloaded', required=False, action='store_const', const=True)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)
  parser.add_argument('-d', '--directory', help='Specify directory to download html file to', required=False)

  args = vars(parser.parse_args())
  return args

def pdsFetch(driver, db, logger, url=None):
  '''
  Crawl the page for the khadya site and fecth the latest reports
  '''
  query="select b.pdsBlockCode,b.name,s.shopCode,m.panchayat from pdsShops s,blocks b, shopMapping m where b.blockCode=s.blockCode and s.shopcode = m.shopcode"
  logger.info('query: [%s]', query)
  cur=db.cursor()
  cur.execute(query)
  results = cur.fetchall()
  logger.debug('results: [%s]', str(results))

  for row in results:
    (pdsBlockCode, blockName, shopCode, panchayat) = row
    logger.info('pdsBlockCode[%s], blockName[%s], shopCode[%s], panchayat[%s]' % (pdsBlockCode, blockName, shopCode, panchayat))
    filename = './reports/'+ blockName + '_' + panchayat + '_' + shopCode + '.html'
    
    if os.path.exists(filename):
      logger.info("Skipped [%s] as alread downloaded" % filename)
      continue
    logger.info('Block Name:[%s] Panchayat Name:[%s] Shop Code:[%s]' % (blockName, panchayat, shopCode))

    if not url:
      url="http://khadya.cg.nic.in/pdsonline/cgfsa/Report/FrmRation_Patra_Allot_VerificationDistWise_Aug14.aspx"
    logger.info('URL: [%s]', url)
    
    driver.get(url)
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='drpdist']/option[@value='39']").click()
    driver.find_element_by_xpath("//select[@id='ddlUrban_Rural']/option[@value='R']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='ddlNNN_Block']/option[@value='"+pdsBlockCode+"']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='ddlShopName']/option[@value='"+shopCode+"']").click()
    time.sleep(delay)
    elem=driver.find_element_by_name("btnShowDetails")
    elem.click()
    time.sleep(delay)
    html_source = driver.page_source
    raw_html=html_source.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    with open(filename, "w") as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(raw_html.encode("UTF-8"))

def pdsFetchPrev(driver, db, logger, month="3"):
  '''
  Crawl the page for the khadya site and fecth the previous report given the month
  '''
  query="select b.pdsBlockCode,s.shopCode,b.name from pdsShops s,blocks b where b.blockCode=s.blockCode "
  logger.info('query: [%s]', query)
  cur=db.cursor()
  cur.execute(query)
  results = cur.fetchall()
  logger.info('results: [%s]', str(results))

  for row in results:
    pdsBlockCode=row[0]
    blockName=row[2]
    shopCode=row[1]

    if shopCode == "0":
      continue

    filename = './html/'+shopCode+'.html'
    if os.path.isfile(filename):
      logger.info("Skipped [%s]" % filename)
      continue

    logger.error('Block Name:[%s] Shop Code:[%s]' % (blockName, shopCode))
    url="http://khadya.cg.nic.in/rationcards/RationFC/RptShow_PreviousAllot_ShopWise.aspx"
    logger.info('URL: [%s]', url)

    driver.get(url)
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='DDdist']/option[@value='39']").click()
    driver.find_element_by_xpath("//select[@id='DDUR']/option[@value='R']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='DDBlock_NNN']/option[@value='"+pdsBlockCode+"']").click()
    time.sleep(delay)
    logger.info("Shopcode[" + shopCode + "]")
    driver.find_element_by_xpath("//select[@id='DDShop']/option[@value='"+shopCode+"']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='DDYear']/option[@value='2015']").click()
    time.sleep(delay)
    driver.find_element_by_xpath("//select[@id='DDMonth']/option[@value='" + month + "']").click()
    time.sleep(delay)
    elem=driver.find_element_by_name("Button1")
    elem.click()
    time.sleep(delay)
    html_source = driver.page_source
    raw_html=html_source.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    with open(filename, "w") as html_file:
      logger.info("Writing [%s]" % filename)
      html_file.write(raw_html.encode("UTF-8"))

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")

  db = dbInitialize(db="surguja")  
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])

  if args['visible']:
    delay = 2

  if args['prev']:
    pdsFetchPrev(driver, db, logger)
  else:
    pdsFetch(driver, db, logger)

  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db)

  logger.info("...END PROCESSING")
  exit(0)

if __name__ == '__main__':
  main()
