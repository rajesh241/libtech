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
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("BEGIN PROCESSING...")
  filename = "/tmp/z.html" 
  display = displayInitialize(args['visible'])
  driver = driverInitialize(browser=args['browser'], profile='/home/mayank/.mozilla/firefox/4s3bttuq.default/')
  base_url="https://www.skillshare.com/"
  driver.get(base_url + "/")
  driver.find_element_by_link_text("Sign In").click()
  driver.find_element_by_name("LoginForm[email]").clear()
  driver.find_element_by_name("LoginForm[email]").send_keys("anupreet@anupreet.com")
  driver.find_element_by_name("LoginForm[password]").clear()
  driver.find_element_by_name("LoginForm[password]").send_keys("golani123")
  driver.find_element_by_xpath("//input[@value='Sign In']").click()
  time.sleep(10)
  driver.get("https://www.skillshare.com/classes/Sketchbook-Practice-Bring-watercolour-to-Life-with-Line-Drawing/1053382271/classroom/discussions")
#  driver.find_element_by_link_text("Set Creative Goals - first steps to success").click()
#  driver.find_element_by_css_selector("p.session-item-title").click()
  time.sleep(10)
  html_source = driver.page_source

  bs = BeautifulSoup(html_source, "html.parser")
  html = bs.findAll('video', attrs={'class':['vjs-tech']})
  str_html = str(html)
  logger.info(str_html)
  logger.info(str_html[str_html.find("src=")+5:str_html.find("?pubId")])

  els = driver.find_elements_by_class_name("session-item")
  for el in els:
    logger.info(str(el))
    el.click()
    time.sleep(10)
    html_source = driver.page_source

    bs = BeautifulSoup(html_source, "html.parser")
    html = bs.findAll('video', attrs={'class':['vjs-tech']})
    str_html = str(html)
    logger.info(str_html)
    logger.info(str_html[str_html.find("src=")+5:str_html.find("?pubId")])
#   driver.back()
  
  writeFile(filename,html_source) 
  driverFinalize(driver)
  displayFinalize(display)
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
