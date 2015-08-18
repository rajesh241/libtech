import time

from logger import loggerFetch
from sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize

from bs4 import BeautifulSoup

#######################
# Global Declarations
#######################

timeout = 10

url = "http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=SmartCardreport_engRH&actionVal=debitLoagReport&id=1457@DOP$APOL&type=01/04/2015&listType="


#############
# Functions
#############


def runTestSuite():
  logger = loggerFetch("info")
  logger.info("BEGIN PROCESSING...")

  display = displayInitialize(1)
  driver = driverInitialize()


  driver.get(url)
  logger.info("Fetching...[%s]" % url)
  
  html_source = driver.page_source

  driver.get(url)
  logger.info("Fetching...[%s] for the purpose of refresh" % url)
  
  html_source = driver.page_source
  logger.debug("HTML Fetched [%s]" % html_source)

  bs = BeautifulSoup(html_source, "html.parser")
  # tr_norm = bs.findAll('tr', attrs={'class':'normalRow'})
  # tr_alt = bs.findAll('tr', attrs={'class':'alternateRow'})
  # tr_list = tr_norm + tr_alt
  tr_list = bs.findAll('tr', attrs={'class':['normalRow', 'alternateRow']})
  logger.debug(str(tr_list))

  for tr in tr_list:
  #  if 'class' in str(tr): # Mynk - Need to check why this fails - NOT a dict unless Tag type
  #    print tr['class'] 
  #  if 'class' not in tr:
  #    logger.info(str(tr))
  #    continue   
  #  if tr['class'] != 'normalRow' or tr['class'] != 'alternateRow':
  #    logger.info(str(tr))
  #    continue
      
    td = tr.find('td')
    td = td.findNext('td')
    panchayat = td.text.strip()
    logger.info("Panchayat[%s]", panchayat)

    elem = driver.find_element_by_link_text(panchayat)
    elem.click()
    time.sleep(1)
    
    
    filename="/tmp/%s.html" % panchayat
    with open(filename, 'w') as html_file:
      logger.info("Writing Prematurely[%s]" % filename)
      html_file.write(driver.page_source.encode('utf-8'))

    driver.back()

  driverFinalize(driver)
  displayFinalize(display)


  logger.info("...END PROCESSING")     


def main():
  runTestSuite()
  exit(0)

if __name__ == '__main__':
  main()
