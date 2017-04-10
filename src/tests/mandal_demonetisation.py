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

disbursement_url = 'http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=SmartCardreport_engRH&actionVal=debitLoagReport&id=%s@DOP$APOL&type=%s&listType=district'
#Vishakapathnam - http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=DemandRH&actionVal=labourworkd&id=03&type=23/01/2017&type1=mandalwise
workers_url = 'http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=DemandRH&actionVal=labourworkd&id=%s&type=%s&type1=mandalwise'

filename = './z.csv'

mandals = ['Ananthagiri', 'Araku Valley', 'Chintapalle', 'Dumbriguda', 'Gangaraju Madugula', 'Gudem Kothaveedhi', 'Hukumpeta', 'Koyyuru', 'Munchingiputtu', 'Paderu', 'Pedabayalu', 'Yatapaka', 'Kunavaram', 'Chintur', 'Rajavommangi', 'Rampachodavaram', 'Addateegala', 'Y Ramavaram', 'Devipatnam', 'Gangavaram', 'Maredumilli', 'Vararamachandrapuram', 'Seethampeta', 'Buttayagudem', 'Jeelugumilli', 'Polavaram', 'Gummalakshmipuram', 'Kurupam']
mandals = ['Yatapaka', 'Y Ramavaram']

districts = {'Ananthagiri':'03', 'Araku Valley':'03', 'Chintapalle':'03', 'Dumbriguda':'03', 'Gangaraju Madugula':'03', 'Gudem Kothaveedhi':'03', 'Hukumpeta':'03', 'Koyyuru':'03', 'Munchingiputtu':'03', 'Paderu':'03', 'Pedabayalu':'03', 'Yatapaka':'04', 'Kunavaram':'04', 'Chintur':'04', 'Rajavommangi':'04', 'Rampachodavaram':'04', 'Addateegala':'04', 'Y Ramavaram':'04', 'Devipatnam':'04', 'Gangavaram':'04', 'Maredumilli':'04', 'Vararamachandrapuram':'04', 'Seethampeta':'01', 'Buttayagudem':'05', 'Jeelugumilli':'05', 'Polavaram':'05', 'Gummalakshmipuram':'02', 'Kurupam':'02'}
    
#############
# Functions
#############

def date_range(start_date, end_date):
  return (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))

def fetch_total(logger, driver, url, date_str, type, mandal):
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
  a = bs.find('a', text = mandal)
  try:
    td = a.parent
  except Exception as e:
    logger.error(e)
    return 0
  logger.debug('@@ %s @@' % td)

  for i in range(0, 10):
    td = td.nextSibling.nextSibling
  total = td.text.strip()
  logger.info('%s[%s]' %(mandal, total))

  return total


def fetch_worker_total(logger, driver, url, date_str, type, mandal):
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
  td = bs.find('td', text = mandal)
  logger.info('@@ %s @@' % td)
  if not td:
    logger.error('Got None [%s]' % td)
    return 0  # FIXME

  for i in range(0, 10):
    logger.debug('%s[%d]=%s' %(mandal, i, td))
    td = td.nextSibling.nextSibling
  total = td.text.strip()
  logger.info('%s[%s]' %(mandal, total))

  return total


def generate_report(logger, driver, mandal, district_id):
  logger.info('MANDAL[%s] in District[%s]' % (mandal, district_id))
  report = 'date, disbursement_2015, workers_2015, date, disbursement_2016, workers_2016, disbursement drop, disbursement % drop, workers drop, workers % drop' + '\n'
  for d in date_range(start_date, end_date):
    logger.info(d.strftime('%Y/%m/%d'))

    date_str = d.strftime('%d/%m/%Y')
    url = disbursement_url % (district_id, date_str)
    disbursement_2015 = fetch_total(logger, driver, url, date_str, 'disbursement_' + district_id, mandal)

    url = workers_url % (district_id, date_str)
    workers_2015 = fetch_worker_total(logger, driver, url, date_str, 'worker_' +  district_id, mandal)

    row = '%s, %s, %s' % (date_str, disbursement_2015, workers_2015)

    year = int(d.strftime('%Y')) + 1
    date_format = '%d/%m/' + str(year)
    date_str  = d.strftime(date_format)
    logger.info("DATE[%s]" % date_str)
    url = disbursement_url % (district_id, date_str)
    disbursement_2016 = fetch_total(logger, driver, url, date_str, 'disbursement_' + district_id, mandal)

    url = workers_url % (district_id, date_str)
    workers_2016 = fetch_worker_total(logger, driver, url, date_str, 'worker_' + district_id, mandal)

    disbursed_drop = int(disbursement_2015) - int(disbursement_2016)
    if int(disbursement_2015) != 0:
      disbursed_drop_per = (disbursed_drop * 100)/int(disbursement_2015)
    else:
      disbursed_drop_per = 0
      
    workers_drop = int(workers_2015) - int(workers_2016)
    if int(workers_2015) != 0:
      workers_drop_per = (workers_drop * 100)/int(workers_2015)
    else:
      workers_drop_per = 0


    row = row + ', %s, %s, %s, %s, %s, %s, %s' % (date_str, disbursement_2016, workers_2016, disbursed_drop, disbursed_drop_per, workers_drop, workers_drop_per)
    
    logger.info(row)

    report = report + row + '\n'

  return report
  

def runTestSuite():
  logger = loggerFetch("info")
  logger.info("BEGIN PROCESSING...")

  display = displayInitialize(0)
  driver = driverInitialize()

  for mandal in mandals:
    report = generate_report(logger, driver, mandal, districts[mandal])
    logger.info('Finally: \n%s' % report)

    filename = './mandals/' +mandal + '.csv'
    with open(filename, 'wb') as csv_file:
      logger.info("Writing to [%s]" % filename)
      csv_file.write(report.encode('utf-8'))

    if final_report[0][0] == '':
      
    rows = report.split('|')
    

  driverFinalize(driver)
  displayFinalize(display)

  logger.info("...END PROCESSING")     

  return

def main():
  runTestSuite()
  exit(0)

if __name__ == '__main__':
  main()
