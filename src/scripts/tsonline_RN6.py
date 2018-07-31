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


#############
# Functions
#############

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

    try:
        logger.info("Fetching...[%s]" % url)
        driver.get(url)
    except Exception as e:
        logger.error('Exception when fetching url [%s] - EXCEPT[%s]' % (url, e))
        # time.sleep(timeout)
        driver = driverInitialize(timeout=3)  # FIXME
        driver.get(url)
        # return 'FAILURE'

    try:
        html_source = driver.page_source.replace('<head>',
                                                 '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    except Exception as e:
        logger.error('Exception getting HTML source - EXCEPT[%s]' % e)
        return 'FAILURE'
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
        logger.error('Exception during Select() - EXCEPT[%s]' % e)
        # return 'FAILURE'
    # time.sleep(timeout)

    try:
        select = Select(driver.find_element_by_id('ctl00_MainContent_ddlService'))
        select.select_by_visible_text('MGNREGA')
        logger.info('MGNREGA selected')
    except Exception as e:
        logger.error('Exception during Select() - EXCEPT[%s]' % e)

    try:
        # elem = driver.find_element_by_id('ctl00_MainContent_txtSSPPEN')
        elem = driver.find_element_by_css_selector("input[type='radio'][value='rbnSSPPEN']")
        elem.click()
        logger.info('Clicked Jobcard radio button')
    except Exception as e:
        logger.error('Exception Jobcard radio button - EXCEPT[%s]' % e)
        # return 'FAILURE'

    try:
        elem = driver.find_element_by_id('ctl00_MainContent_txtSSPPEN')
        elem.send_keys(jobcard_no)
        elem.click()
        logger.info('Entering Jobcard[%s]' % jobcard_no)
    except Exception as e:
        logger.error('Exception Entering Jobcard[%s] - EXCEPT[%s]' % (jobcard_no,e))
        # return 'FAILURE'
    #time.sleep(timeout)

    try:
        logger.info('Clicking Submit')
        elem = driver.find_element_by_id('ctl00_MainContent_btnMakePayment')
        elem.click()
    except Exception as e:
        logger.error('Exception Clicking Submit for jobcard[%s] - EXCEPT[%s]' % (jobcard_no,e))
        return 'FAILURE'
    #time.sleep(timeout)


    try:
        logger.info('Clicking Select radio button')
        elem = driver.find_element_by_css_selector("input[type='radio'][value='rbSelect']")
        elem.click()
    except Exception as e:
        logger.error('Exception selecting radio button for jobcard[%s] - EXCEPT[%s]' % (jobcard_no,e))
        return 'FAILURE'
    #time.sleep(timeout)
    
    try:
        logger.info('Clicking View Ledger')
        elem = driver.find_element_by_id('ctl00_MainContent_btnTxDetails')
        elem.click()
    except Exception as e:
        logger.error('Exception clicking view ledger for jobcard[%s] - EXCEPT[%s]' % (jobcard_no,e))
        return 'FAILURE'
    #time.sleep(2)

    parent_handle = driver.current_window_handle
    logger.info("Handles : %s" % driver.window_handles + "Number : %d" % len(driver.window_handles))

    if len(driver.window_handles) == 2:
        driver.switch_to.window(driver.window_handles[-1])
        #time.sleep(2)
    else:
        logger.error("Handlers gone wrong [" + str(driver.window_handles) + 'jobcard %s' % jobcard_no + "]")
        driver.save_screenshot('./logs/button_'+jobcard_no+'.png')
        return 'FAILURE'

    try:
        logger.info('Waiting for the dialog box to open')
        elem = WebDriverWait(driver, timeout).until(
          EC.presence_of_element_located((By.CLASS_NAME, "btn"))
        )
    except Exception as e:
        logger.error('Exception on WebDriverWait(10) - EXCEPT[%s]' % e)
        driver.save_screenshot('./button_'+jobcard_no+'.png')
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

    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise        
    
    if False:
        # result = fetch_rn6_report(logger, driver, state='ap', district_name='ANANTAPUR', jobcard_no='121673411011010257-02')
        # result = fetch_rn6_report(logger, driver, district_name='MAHABUBNAGAR', jobcard_no='141990515024010071-08')
        result = fetch_rn6_report(logger, driver, state='ap', district_name='VISAKHAPATNAM', jobcard_no='030300927050030026-02')
        return 'SUCCESS'

    if True:
        state = None
        district_name = 'MAHABUBNAGAR'
        block_name = 'Damaragidda'
        # block_id = block_lookup[block_name]
        block_id = '4378'
    else:
        state = 'ap'
        district_name = 'VISAKHAPATNAM'
        block_name = 'Gangaraju Madugula'
        block_id = '0203011'

    url = 'http://b.libtech.info:8000/api/panchayats/?bid=%s' % block_id
    
    try:
        logger.info('Requesting URL[%s]' % url)
        response = requests.get(url, timeout=timeout) # , cookies=cookies)
    except Exception as e:
        logger.error('Caught Exception[%s]' % e) 

    panchayats_json = response.json()
    logger.debug('Panchayats JSON[%s]' % panchayats_json)

    
    is_panchayat = True
    for panchayat_object in panchayats_json:
        panchayat_name = panchayat_object['name'].strip()
        panchayat_code = panchayat_object['code'].strip()
        logger.info('Fetch jobcards for Panchayat[%s, %s]' % (panchayat_name, panchayat_code))
        '''
        if is_panchayat and panchayat_name != 'VITHALAPUR':
            logger.debug('Already downloaded. Skipping[%s]' % panchayat_name)
            continue
        is_panchayat = False
        '''
        url = 'http://b.libtech.info:8000/api/getworkers/?pcode=%s' % panchayat_code
        try:
            logger.info('Requesting URL[%s]' % url)
            response = requests.get(url, timeout=timeout)
        except Exception as e:
            logger.error('Caught Exception[%s]' % e)
        jobcards_json = response.json()
        logger.debug('JobCards JSON[%s]' % jobcards_json)
        is_downloaded = True
        for jobcard_object in jobcards_json:
            jobcard = '%s-0%s' % (jobcard_object['jobcard']['tjobcard'], jobcard_object['applicantNo'])
            '''
            if (panchayat_name == 'VITHALAPUR' and is_downloaded and (jobcard != '142000501002010385-01')): 
                logger.debug('Skipping[%s]' % jobcard)
                continue            
            is_downloaded = False
            '''
            logger.info('Fetch details for jobcard[%s]' % jobcard)
            result = fetch_rn6_report(logger, driver, district_name=district_name, jobcard_no=jobcard, block_name=block_name, panchayat_name=panchayat_name)
            if result != 'SUCCESS':
                logger.error('Failure returned [%s]' % result)
                #time.sleep(3)
                continue  # FIXME why is this even needed. Why is it not working?

    return 'SUCCESS'

class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = loggerFetch('info')
        self.logger.info('BEGIN PROCESSING...')
        self.display = displayInitialize(0)
        self.driver = driverInitialize(timeout=3, options='--headless') # driverInitialize(path='/opt/firefox/', timeout=3)

    def tearDown(self):
        #driverFinalize(self.driver) 
        displayFinalize(self.display)
        self.logger.info('...END PROCESSING')

    def test_rn6_report(self):
        result = fetch_rn6_reports(self.logger, self.driver)
        #result = fetch_rn6_report(self.logger, self.driver)
        self.assertEqual(result, 'SUCCESS')

if __name__ == '__main__':
    unittest.main()
