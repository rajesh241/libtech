from bs4 import BeautifulSoup

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize

from datetime import timedelta, date

import unittest


#######################
# Global Declarations
#######################

start_date = date(2015, 11, 9)
end_date = date(2015, 12, 19)

disbursement_url = 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=SmartCardreport_engRH&actionVal=debitLoagReport&type=%s'
workers_url = 'http://www.nrega.telangana.gov.in/Nregs/FrontServlet?requestType=DemandRH&actionVal=labourworkd&type=%s'

filename = './z.csv'
    
#############
# Functions
#############

def date_range(start_date, end_date):
  return (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))

def fetch_total(logger, driver, url, date_str):
  driver.get(url)
  logger.info("Fetching...[%s]" % url)
  
  driver.get(url)    # A double refresh required for the page to load
  logger.info("Refreshing...[%s]" % url)

  html_source = driver.page_source.replace('<head>',
                                             '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
  logger.debug("HTML Fetched [%s]" % html_source)

  with open('html/' + date_str.replace('/', '_') + '.html', 'w') as html_file:
    logger.info('Writing [%s]' % filename)
    html_file.write(html_source)
    
  bs = BeautifulSoup(html_source, "html.parser")
  tfoot = bs.find('tfoot')
  td = tfoot.findAll('td')[9]
  logger.info(td)

  return td.text

def generate_report(logger, driver):
  report = 'date, disbursement_2015, workers_2015, date, disbursement_2016, workers_2016, disbursement drop, disbursement % drop, workers drop, workers % drop' + '\n'
  for d in date_range(start_date, end_date):
    logger.info(d.strftime('%Y/%m/%d'))

    date_str = d.strftime('%d/%m/%Y')
    url = disbursement_url % date_str
    disbursement_2015 = fetch_total(logger, driver, url, date_str)

    date_str =  d.strftime('%d/%m/%Y')
    url = workers_url % date_str
    workers_2015 = fetch_total(logger, driver, url, date_str)

    row = '%s, %s, %s' % (date_str, disbursement_2015, workers_2015)

    date_str  = d.strftime('%d/%m/2016')
    url = disbursement_url % date_str
    disbursement_2016 = fetch_total(logger, driver, url, date_str)

    date_str =  d.strftime('%d/%m/2016')
    url = workers_url % date_str
    workers_2016 = fetch_total(logger, driver, url, date_str)

    disbursed_drop = int(disbursement_2015) - int(disbursement_2016)
    disbursed_drop_per = (disbursed_drop * 100)/int(disbursement_2015)
    workers_drop = int(workers_2015) - int(workers_2016)
    if int(workers_2015) != 0:
      workers_drop_per = (workers_drop * 100)/int(workers_2015)

    row = row + ', %s, %s, %s, %s, %s, %s, %s' % (date_str, disbursement_2016, workers_2016, disbursed_drop, disbursed_drop_per, workers_drop, workers_drop_per)
    
    logger.info(row)

    report = report + row + '\n'

  return report
  

def runTestSuite():
  logger = loggerFetch("info")
  logger.info("BEGIN PROCESSING...")

  display = displayInitialize(0)
  driver = driverInitialize()

  report = generate_report(logger, driver)
  logger.info('Finally: \n%s' % report)

  with open(filename, 'wb') as csv_file:
    logger.info("Writing to [%s]" % filename)
    csv_file.write(report.encode('utf-8'))

  driverFinalize(driver)
  displayFinalize(display)

  logger.info("...END PROCESSING")     

  return

def main():
  runTestSuite()
  exit(0)

if __name__ == '__main__':
  main()
