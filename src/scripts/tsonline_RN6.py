from bs4 import BeautifulSoup

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

import time
import unittest

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize, driverFinalize, displayInitialize, displayFinalize

#######################
# Global Declarations
#######################

timeout = 10

def fetch_rn6_report(logger, driver, state=None, district_name=None, jobcard_no=None):
    if not state:
        url = 'https://bdp.tsonline.gov.in/NeFMS_TS/NeFMS/Reports/NeFMS/AccountWiseTransactionReport.aspx'
    else:
        url = 'https://bdp.%sonline.gov.in/NeFMS_AP/NeFMS/Reports/NeFMS/AccountWiseTransactionReport.aspx' % state

    if not district_name:
        district_name = 'MAHABUBNAGAR'

    if not jobcard_no:
        jobcard_no = '142000520007010154-02'
    
    driver.get(url)
    logger.info("Fetching...[%s]" % url)
  
    html_source = driver.page_source.replace('<head>',
                                             '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    logger.debug("HTML Fetched [%s]" % html_source)
    
    filename = 'rn6.html'
    with open(filename, 'w') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(html_source)

    bs = BeautifulSoup(html_source, 'html.parser')

    # time.sleep(timeout)
    try:
        # elem = driver.find_element_by_id('ctl00_MainContent_ddlDistrict')
        # elem = driver.find_element_by_name('ctl00$MainContent$ddlDistrict')
        # elem.send_keys(district_name)

        select = Select(driver.find_element_by_id('ctl00_MainContent_ddlDistrict'))
        select.select_by_visible_text(district_name)
        # elem.click()
        # elem = driver.find_element_by_xpath("//select[@name='ctl00$MainContent$ddlDistrict']/option[text()=district_name]").click()
    except Exception as e:
        logger.error('Ouch! Caught Exception[%s]' % e)
    # time.sleep(timeout)

    try:
        select = Select(driver.find_element_by_id('ctl00_MainContent_ddlService'))
        select.select_by_visible_text('MGNREGA')
        logger.info('MGNREGA selected')
    except Exception as e:
        logger.error('Ouch! Caught Exception[%s]' % e)

    try:
        # elem = driver.find_element_by_id('ctl00_MainContent_txtSSPPEN')
        elem = driver.find_element_by_css_selector("input[type='radio'][value='rbnSSPPEN']")
        elem.click()
        logger.info('Clicked Jobcard radio button')
    except Exception as e:
        logger.error('Ouch! Caught Exception[%s]' % e)

    try:
        elem = driver.find_element_by_id('ctl00_MainContent_txtSSPPEN')
        elem.send_keys(jobcard_no)
        elem.click()
        logger.info('Entering Jobcard[%s]' % jobcard_no)
    except Exception as e:
        logger.error('Ouch! Caught Exception[%s]' % e)
    #time.sleep(timeout)

    try:
        elem = driver.find_element_by_id('ctl00_MainContent_btnMakePayment')
        elem.click()
        logger.info('Clicking Submit')
    except Exception as e:
        logger.error('Ouch! Caught Exception[%s]' % e)
    #time.sleep(timeout)


    try:
        elem = driver.find_element_by_css_selector("input[type='radio'][value='rbSelect']")
        elem.click()
        logger.info('Clicked Select radio button')
    except Exception as e:
        logger.error('Ouch! Caught Exception[%s]' % e)
    #time.sleep(timeout)
    
    try:
        elem = driver.find_element_by_id('ctl00_MainContent_btnTxDetails')
        elem.click()
        logger.info('Clicked View Ledger')
    except Exception as e:
        logger.error('Ouch! Caught Exception[%s]' % e)
    # time.sleep(timeout)

    parent_handle = driver.current_window_handle
    print("Handles : ", driver.window_handles, "Number : ", len(driver.window_handles))

    if len(driver.window_handles) == 2:
        driver.switch_to.window(driver.window_handles[-1])
        # time.sleep(timeout)
    else:
        logger.error("Handlers gone wrong [" + str(driver.window_handles) + "]")
        driver.save_screenshot('./logs/button_'+jobcard_no+'.png')
        return 'FAILURE'

    try:
        elem = WebDriverWait(driver, timeout).until(
          EC.presence_of_element_located((By.CLASS_NAME, "btn"))
        )
    except NoSuchElementException or TimeoutException:
        logger.error("Failed to locate Close Button")
        driver.save_screenshot('./logs/button_'+jcno+'.png')
        driver.close()
        driver.switch_to.window(parent_handle)
        return 'FAILURE'
        
    html_source = driver.page_source.replace('<head>',
                                             '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    logger.debug("HTML Fetched [%s]" % html_source)
    filename = '%s_ledger_details.html' % jobcard_no
    with open(filename, 'w') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(html_source)
        
    driver.close()
    driver.switch_to.window(parent_handle)        
        
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
        self.logger.info('...END PROCESSING')

    def test_rn6_report(self):
        result = fetch_rn6_report(self.logger, self.driver, state='ap', district_name='ANANTAPUR', jobcard_no='121673411011010257-02')
        #result = fetch_rn6_report(self.logger, self.driver)
        self.assertEqual(result, 'SUCCESS')

if __name__ == '__main__':
    unittest.main()
