from bs4 import BeautifulSoup

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

import unittest

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize, driverFinalize, displayInitialize, displayFinalize

#######################
# Global Declarations
#######################

timeout = 10

url = 'https://bdp.tsonline.gov.in/NeFMS_TS/NeFMS/Reports/NeFMS/AccountWiseTransactionReport.aspx'

def fetch_rn6_report(logger, driver, district_name=None):
    if not district_name:
        district_name = 'MAHABUBNAGAR'
    
    driver.get(url)
    logger.info("Fetching...[%s]" % url)
  
    html_source = driver.page_source.replace('<head>',
                                             '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    logger.info("HTML Fetched [%s]" % html_source)
    
    filename = 'rn6.html'
    with open(filename, 'w') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(html_source)

    bs = BeautifulSoup(html_source, 'html.parser')

    elem = driver.find_element_by_id('ctl00_MainContent_ddlDistrict')
    elem.send_keys(district_name)
    time.sleep(timeout)

    elem = driver.find_element_by_id('ctl00_MainContent_ddlService')
    elem.send_keys('MGNREGA')
    time.sleep(timeout)

    elem = driver.find_element_by_id('ctl00_MainContent_txtSSPPEN')
    elem.click()
    time.sleep(timeout)

    elem = driver.find_element_by_id('ctl00_MainContent_btnMakePayment')
    elem.click()
    time.sleep(timeout)

    return 'SUCCESS'

class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = loggerFetch('info')
        self.logger.info('BEGIN PROCESSING...')
        self.display = displayInitialize(1)
        self.driver = driverInitialize(path='/opt/firefox/')

    def tearDown(self):
        #FIXME driverFinalize(self.driver) 
        displayFinalize(self.display)
        self.logger('...END PROCESSING')

    def test_rn6_report(self):
        result = fetch_rn6_report(self.logger, self.driver)
        self.assertEqual(result, 'SUCCESS')

if __name__ == '__main__':
    unittest.main()
