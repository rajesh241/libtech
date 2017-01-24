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
end_date = date(2016, 1, 23)

disbursement_url = 'http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=SmartCardreport_engRH&actionVal=debitLoagReport&type=%s'

filename = './z.csv'


#############
# Functions
#############

def date_range(start_date, end_date):
  return (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))

def fetch_total(logger, driver, url, date_str, type):
  html_fname = 'html/' + type + '_' + date_str.replace('/', '_') + '.html'

  if os.path.exists(html_fname):
    with open(html_fname, 'r') as html_file:
      logger.info('Reading [%s]' % html_fname)
      html_source = html_file.read()
  else:
    driver.get(url)
    logger.info("Fetching...[%s]" % url)
    
    driver.get(url)    # A double refresh required for the page to load
    logger.info("Refreshing...[%s]" % url)

    html_source = driver.page_source.replace('<head>',
                                             '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    logger.debug("HTML Fetched [%s]" % html_source)

    with open(html_fname, 'w') as html_file:
      logger.info('Writing [%s]' % html_fname)
      html_file.write(html_source)
    
  bs = BeautifulSoup(html_source, "html.parser")

  td = bs.find('td', text = 'GRAND TOTAL')
  logger.debug('@@ %s @@' % td)
  if not td:
    logger.error('Got None')
    return 0

  for i in range(0, 9):
    logger.debug('%s[%s]' %(i, td))
    td = td.nextSibling.nextSibling
  total = td.text.strip()
  logger.info('Total[%s]', total)
  return total


def generate_report(logger, driver):
  report = 'date, disbursement_2015, date, disbursement_2016, disbursement drop, disbursement % drop' + '\n'
  for d in date_range(start_date, end_date):
    logger.info(d.strftime('%Y/%m/%d'))

    date_str = d.strftime('%d/%m/%Y')
    url = disbursement_url % date_str
    disbursement_2015 = fetch_total(logger, driver, url, date_str, 'GrandTotal')

    row = '%s, %s' % (date_str, disbursement_2015)

    year = int(d.strftime('%Y')) + 1
    date_format = '%d/%m/' + str(year)
    date_str  = d.strftime(date_format)
    logger.info("DATE[%s]" % date_str)
    url = disbursement_url % date_str
    disbursement_2016 = fetch_total(logger, driver, url, date_str, 'GrandTotal')

    disbursed_drop = int(disbursement_2015) - int(disbursement_2016)
    if int(disbursement_2015) != 0:
      disbursed_drop_per = (disbursed_drop * 100)/int(disbursement_2015)
    else:
      disbursed_drop_per = 0

    row = row + ', %s, %s, %s, %s' % (date_str, disbursement_2016, disbursed_drop, disbursed_drop_per)
    
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
