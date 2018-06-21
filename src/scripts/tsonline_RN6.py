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

from os import errno

import requests
import time
import unittest

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize, driverFinalize, displayInitialize, displayFinalize

#######################
# Global Declarations
#######################

timeout = 10
dirname = 'jobcards'

def fetch_rn6_report(logger, driver, state=None, district_name=None, jobcard_no=None, block_name=None, panchayat_name=None):
    if not state:
        url = 'https://bdp.tsonline.gov.in/NeFMS_TS/NeFMS/Reports/NeFMS/AccountWiseTransactionReport.aspx'
    else:
        url = 'https://bdp.%sonline.gov.in/NeFMS_AP/NeFMS/Reports/NeFMS/AccountWiseTransactionReport.aspx' % state

    if not district_name:
        district_name = 'MAHABUBNAGAR'

    if not jobcard_no:
        jobcard_no = '142000520007010154-02'

    filename = '%s/%s_%s_%s_ledger_details.html' % (dirname, block_name, panchayat_name, jobcard_no)
    if os.path.exists(filename):
        logger.info('File already donwnloaded. Skipping [%s]' % filename)
        return 'SUCCESS'

    driver.get(url)
    logger.info("Fetching...[%s]" % url)

    html_source = driver.page_source.replace('<head>',
                                         '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    logger.debug("HTML Fetched [%s]" % html_source)

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
        logger.error('Ouch! Caught Exception[%s, err[%d]]' % (e, e.errno))
        return e.errno
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
    #time.sleep(2)

    parent_handle = driver.current_window_handle
    print("Handles : ", driver.window_handles, "Number : ", len(driver.window_handles))

    if len(driver.window_handles) == 2:
        driver.switch_to.window(driver.window_handles[-1])
        #time.sleep(2)
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
    filename = '%s/%s_%s_%s_ledger_details.html' % (dirname, block_name, panchayat_name, jobcard_no)
    with open(filename, 'w') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(html_source)
        
    driver.close()
    driver.switch_to.window(parent_handle)        
        
    return 'SUCCESS'

def fetch_rn6_reports(logger, driver):
    logger.info('Fetch the jobcards')

    if False:
        result = fetch_rn6_report(logger, driver, state='ap', district_name='ANANTAPUR', jobcard_no='121673411011010257-02')
        result = fetch_rn6_report(logger, driver, district_name='MAHABUBNAGAR', jobcard_no='142000520007010015-03')
        return 'SUCCESS'

    district_name = 'MAHABUBNAGAR'
    block_name = 'Damaragidda'
    # block_id = block_lookup[block_name]
    block_id = '4378'

    url = 'http://b.libtech.info:8000/api/panchayats/?bid=%s' % block_id
    
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise        
    
    try:
        logger.info('Fetching URL[%s]' % url)
        response = requests.get(url, timeout=timeout) # , cookies=cookies)
    except Exception as e:
        logger.error('Caught Exception[%s]' % e) 

    panchayats_json = response.json()
    logger.debug('Panchayats JSON[%s]' % panchayats_json)

    
    for panchayat_object in panchayats_json:
        panchayat_name = panchayat_object['name'].strip()
        panchayat_code = panchayat_object['code'].strip()
        logger.info('Fetch jobcards for Panchayat[%s, %s]' % (panchayat_name, panchayat_code))
        
        url = 'http://b.libtech.info:8000/api/getworkers/?pcode=%s' % panchayat_code
        try:
            logger.info('Fetching URL[%s]' % url)
            response = requests.get(url, timeout=timeout)
        except Exception as e:
            logger.error('Caught Exception[%s]' % e)
        jobcards_json = response.json()
        logger.debug('JobCards JSON[%s]' % jobcards_json)
        for jobcard_object in jobcards_json:
            jobcard = '%s-0%s' % (jobcard_object['jobcard']['tjobcard'], jobcard_object['applicantNo'])
            logger.info('Fetch details for jobcard[%s]' % jobcard)
            fetch_rn6_report(logger, driver, district_name=district_name, jobcard_no=jobcard, block_name=block_name, panchayat_name=panchayat_name)
    
    return 'SUCCESS'

class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = loggerFetch('info')
        self.logger.info('BEGIN PROCESSING...')
        self.display = displayInitialize(0)
        self.driver = driverInitialize(path='/opt/firefox/')

    def tearDown(self):
        #FIXME driverFinalize(self.driver) 
        displayFinalize(self.display)
        self.logger.info('...END PROCESSING')

    def test_rn6_report(self):
        result = fetch_rn6_reports(self.logger, self.driver)
        #result = fetch_rn6_report(self.logger, self.driver)
        self.assertEqual(result, 'SUCCESS')

if __name__ == '__main__':
    unittest.main()
