#! /usr/bin/env python

#This code will get the Oabcgatat Banes
import csv
from bs4 import BeautifulSoup
import requests

import logging
import MySQLdb
import time
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


#######################
# Global Declarations
#######################

delay = 2
url="http://www.nrega.telangana.gov.in/"
browser="Firefox"
logFile = 'jc.log'
logLevel = logging.ERROR
logFormat = '%(asctime)s:[%(name)s|%(levelname)s]: %(message)s'

# Error File Defination
# errorfile = open('./logs/jc.log', 'w')


#############
# Functions
#############

'''
def logInitialize():
  import logging
  logging.basicConfig(filename=logFile, level=logLevel, format=logFormat) # Mynk
'''

def loggerFetch(level='ERROR'):
  logger = logging.getLogger(__name__)

  if level:                     # Mynk ???
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
      raise ValueError('Invalid log level: %s' % level)
    else:
      logger.setLevel(numeric_level)
  else:
    logger.setLevel(logLevel)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)    # Mynk ???

  # create formatter e.g - FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
  formatter = logging.Formatter(logFormat)

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  logger.addHandler(ch)

  return logger

def loggerTest(logger):
  logger.debug('debug message')
  logger.info('info message')
  logger.warn('warn message')
  logger.error('error message')
  logger.critical('critical message')
    

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
  #parser.add_argument('-d', '--debug', help='Debug level (default=)', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)

  args = vars(parser.parse_args())
  return args


def parserFinalize(parser):
  parser.close()


def dbInitialize():
  '''
  Connect to MySQL Database
  '''
  db = MySQLdb.connect(host="localhost", user="root", passwd="root123", db="mahabubnagar")
  cur=db.cursor()
  db.autocommit(True)
  return db;

def dbFinalize(db):
  db.close()

def displayInitialize(isVisible=0):
  from pyvirtualdisplay import Display
  
  display = Display(visible=isVisible, size=(600, 400))
  display.start()
  return display

def displayFinalize(display):
  display.stop()

def driverInitialize(browser="Firefox"):
  if browser == "Firefox":
    profile = webdriver.FirefoxProfile()
    profile.native_events_enabled = False
    driver = webdriver.Firefox(profile)
  elif browser == "PhantomJS":
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
  else:
    driver = webdriver.Chrome()
  return driver

def driverFinalize(driver):
  driver.close()

def wdTest(driver):
  driver.get("http://www.google.com")
  print driver.page_source.encode('utf-8')

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))        # Mynk WTF is '_' doing here?
  # loggerTest(logger)
  logger.info('args: %s', str(args))

  db = dbInitialize()
  display = displayInitialize(args['visible'])
  driver = driverInitialize(browser)

  wdTest(driver)

  driverFinalize(driver)
  displayFinalize(display)
  dbFinalize(db)
  exit(0)

if __name__ == '__main__':
  main()

def crawlJobcards(driver):
    
  driver.get(url)

  elem = driver.find_element_by_link_text("Wage Seekers")
  elem.send_keys(Keys.RETURN)
  time.sleep(1)

  elem = driver.find_element_by_link_text("Job Card Holders Information")
  elem.send_keys(Keys.RETURN)
  time.sleep(1)

  elem = driver.find_element_by_name("District")
  elem.send_keys("Mahabubnagar")
  elem.send_keys(Keys.RETURN)
  #elem.click()
  time.sleep(delay)

  elem = driver.find_element_by_name("Mandal")
  elem.send_keys("Ghattu")
  elem.send_keys(Keys.RETURN)
  #elem.click()
  time.sleep(delay)

  # Query to get all the blocks
  query="select stateCode,districtCode,blockCode,name from blocks"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    blockName=row[3]

  query="select name,panchayatCode,id from panchayats where jobcardCrawlStatus=0 and stateCode='"+stateCode+"' and districtCode='"+districtCode+"' and blockCode='"+blockCode+"' "
  cur.execute(query)
  panchresults = cur.fetchall()
  #print panchresults

  for panchrow in panchresults:
    panchayatName=panchrow[0]
    panchayatCode=panchrow[1]
    panchID=panchrow[2]
    #print stateCode+districtCode+blockCode+blockName+panchayatCode+panchayatName
    elem = driver.find_element_by_name("Panchayat")
    elem.send_keys(panchayatName)
    elem.send_keys(Keys.RETURN)
    #elem.click()
    time.sleep(delay)

    elem = driver.find_element_by_name("Go")
    elem.send_keys(Keys.RETURN)
    
    curtime = time.strftime('%Y-%m-%d %H:%M:%S')
    html_source = driver.page_source
    htmlsoup=BeautifulSoup(html_source)
    try:
      table=htmlsoup.find('table',id="sortable")
      rows = table.findAll('tr')
      td = table.find('td')
      #print "DATA[", td.text, "]"
     # #print rows
      status=1
    except:
      status=0
    query="update panchayats set jobcardCrawlStatus="+str(status)+", jobcardCrawlDate='"+curtime+"' where id="+str(panchID) 
    # #print query
    cur.execute(query)
    if status==1:
      for tr in rows:
        td = tr.findNext('td')
        #print "DATA1[", td.text, "]"
        td = td.findNext('td')
        #print "DATA2[", td.text, "]"
        jcno = td.text.strip()
        #print "jcno", jcno
        td = td.findNext('td')
        #print "DATA3[", td.text, "]"
        gjcno = td.text.strip()
        #print "gjcno", gjcno
        td = td.findNext('td')
        #print "DATA4[", td.text, "]"
        hof = td.text
        #print "HOF", hof
        td = td.findNext('td')
        regDate = td.text
        #print "Reg Date", regDate
        issueDate = "STR_TO_DATE('"+regDate+"','"+"%d/%m/%Y')"
        td = td.findNext('td')
        caste = td.text
        #print "caste", caste
                        
        if True:
          #print jcno
          query="insert into jobcardRegister (jobcard,govtJobcard,stateCode,headOfFamily,issueDate,caste,districtCode,blockCode,panchayatCode) values ('"+jcno+"','"+gjcno+"','"+stateCode+"','"+hof+"',"+issueDate+",'"+caste+"','"+districtCode+"','"+blockCode+"','"+panchayatCode+"')"
          #print "<<", query, ">>"
          try:
            cur.execute(query)
          except MySQLdb.IntegrityError,e:
            errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
            errorfile.write(errormessage)
          continue

        #exit(0)

#driver.back()
#    driver.back()
    time.sleep(delay)

#  driver.back()
  time.sleep(delay)

