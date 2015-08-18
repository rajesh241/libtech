import time

from logger import loggerFetch
from sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize
import requests
from bs4 import BeautifulSoup, Tag

#######################
# Global Declarations
#######################

delay = 2
timeout = 10


#############
# Functions
#############




def runTestSuite():
  logger = loggerFetch("info")
  logger.info("BEGIN PROCESSING...")

  display = displayInitialize(1)
  driver = driverInitialize()

  url = "http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=SmartCardreport_engRH&actionVal=debitLoagReport&id=1457@DOP$APOL&type=01/04/2015&listType="

  driver.get(url)
  logger.info("Fetching...[%s]" % url)
  
  html_source = driver.page_source
  logger.debug("HTML Fetched [%s]" % html_source)

  filename="/tmp/1.html"
  with open(filename, 'w') as html_file:
    logger.info("Writing Prematurely[%s]" % filename)
    html_file.write(html_source.encode('utf-8'))

  driver.get(url)
  logger.info("Fetching...[%s]" % url)
  
  html_source = driver.page_source
  logger.debug("HTML Fetched [%s]" % html_source)

  filename="/tmp/2.html"
  with open(filename, 'w') as html_file:
    logger.info("Writing Prematurely[%s]" % filename)
    html_file.write(html_source.encode('utf-8'))

  bs = BeautifulSoup(html_source)
  tr = bs.find('tr',attrs={'class':'normalRow'})
  logger.info("tr[%s]" % tr)

  td = tr.find('td')
  td = td.findNext('td')
  panchayat = td.text.strip()
  logger.info("Panchayat[%s]", panchayat)

  elem = driver.find_element_by_link_text(panchayat)
  print(elem)
  elem.click()
  time.sleep(1)


  driverFinalize(driver)
  displayFinalize(display)


  logger.info("...END PROCESSING")     


def main():
  runTestSuite()
  exit(0)

if __name__ == '__main__':
  main()
