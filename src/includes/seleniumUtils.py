import os
import csv
from bs4 import BeautifulSoup, Tag
import requests

import logging
import MySQLdb
import time
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

#######################
# Global Declarations
#######################

delay = 2
timeout = 10
logFile = __file__+'.log'
logLevel = logging.ERROR
logFormat = '%(asctime)s:[%(name)s|%(module)s|%(funcName)s|%(lineno)s|%(levelname)s]: %(message)s' #  %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s"

#############
# Functions
#############

'''
def logInitialize():
  import logging
  logging.basicConfig(filename=logFile, level=logLevel, format=logFormat) # Mynk
  logging.basicConfig(
    filename = fileName,
    format = "%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s",
    level = logging.DEBUG
)
'''

def loggerFetch(level=None):
  logger = logging.getLogger(__name__)

  if level:
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
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)
  #  parser.add_argument('-j', '--jobcard-number', help='Specify the jobcard no to fetch', required=True)
  #  parser.add_argument('-m', '--mobile-number', help='Specify the mobile number', required=True)
  #  parser.add_argument('-i', '--missed-call-id', help='Specify the ID of missed call', required=True)
  parser.add_argument('-d', '--directory', help='Specify directory to download html file to', required=False)
  parser.add_argument('-q', '--query', help='Query to specify the workset, E.g ... where id=147', required=False)

  args = vars(parser.parse_args())
  return args

def parserFinalize(parser):
  parser.close()

def dbInitialize(host="localhost", user="root", passwd="root123", db="libtech"):
  '''
  Connect to MySQL Database
  '''
  db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
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

def driverInitialize(browser=None):
  if browser ==  None:
    browser="Firefox"
  if browser == "Firefox":
    fp = webdriver.FirefoxProfile()
    fp.native_events_enabled = False
    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir", os.getcwd())
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")

    driver = webdriver.Firefox(fp)
  elif browser == "PhantomJS":
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
  else:
    driver = webdriver.Chrome()

  driver.implicitly_wait(10)

  return driver

def driverFinalize(driver):
  driver.close()
  driver.quit()


def wdTest(driver):
  driver.get("http://www.google.com")
  print driver.page_source.encode('utf-8')



