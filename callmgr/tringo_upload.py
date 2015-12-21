from bs4 import BeautifulSoup

import time
import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize


#######################
# Global Declarations
#######################

timeout = 10

url="http://www.hostedivr.in"


#############
# Functions
#############

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
  parser.add_argument('-f', '--filename', help='Specify the wave file to upload', required=True)
  parser.add_argument('-d', '--directory', help='Specify directory to download html file to', required=False)

  args = vars(parser.parse_args())
  return args
  

def waveUpload(logger, url, driver, wave_file):
  '''
  Fetch the html for the jobcard
  '''
  driver.get(url)
  driver.find_element_by_name("uname").clear()
  driver.find_element_by_name("uname").send_keys("togoli@gmail.com")
  driver.find_element_by_name("upass").clear()
  driver.find_element_by_name("upass").send_keys("golani123")
  driver.find_element_by_css_selector("button.button-yellow").click()
#  driver.find_element_by_xpath("(//a[contains(text(),'Upload Wave')])[3]").click()
  driver.find_element_by_link_text("Upload Wave").click()
  driver.find_element_by_name("uploaded_file").send_keys(wave_file)
  driver.find_element_by_css_selector("button.button-yellow").click()
  time.sleep(10)

  if driver.find_element_by_css_selector("div.success"):
    driver.find_element_by_link_text("My Voice").click()
    time.sleep(5)
    driver.find_element_by_link_text("My Voice").click()
    time.sleep(5)

    html_source = driver.page_source
    bs = BeautifulSoup(html_source)

    table = bs.find("table", {"class" : "tablesorter"})
    
    filename = "523_" + os.path.basename(wave_file)   # Hard Coding group ID Mynk
    td = table.find('td')
    file_id =  td.text
    logger.info(file_id)
    file_uploaded = td.findNext('td').text.strip()
    logger.info(file_uploaded)
    if  file_uploaded == filename:
      print td.text, file_id
      return file_id
    else:
      logger.info("[%s] == [%s]" % (filename, file_uploaded))
      return None   # If the file uploaded does not match 
  
  
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  display = displayInitialize(args['visible'])
  driver = driverInitialize(args['browser'])

  wave_file = args['filename']

  logger.info("Uploading file [%s]..." % wave_file)
  file_id = waveUpload(logger, url, driver, wave_file)
  logger.info("Upload Succesful. FILE_ID[%s]" % file_id)

  driverFinalize(driver)
  displayFinalize(display)
  exit(0)

if __name__ == '__main__':
  main()
