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
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  filename=tempDir+"/z.html" 
  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])
  base_url="https://www.skillshare.com/"
  driver.get(base_url + "/")
  driver.find_element_by_link_text("Sign In").click()
  driver.find_element_by_name("LoginForm[email]").clear()
  driver.find_element_by_name("LoginForm[email]").send_keys("anupreet@anupreet.com")
  driver.find_element_by_name("LoginForm[password]").clear()
  driver.find_element_by_name("LoginForm[password]").send_keys("golani123")
  driver.find_element_by_xpath("//input[@value='Sign In']").click()
  driver.find_element_by_link_text("Set Creative Goals - first steps to success").click()
  driver.find_element_by_css_selector("p.session-item-title").click()
  html_source = driver.page_source
  writeFile(filename,html_source) 
  driverFinalize(driver)
  displayFinalize(display)
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
