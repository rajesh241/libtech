from bs4 import BeautifulSoup

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)
#FIXME
#sys.path.append(os.path.dirname(rootdir) + '/django/n.libtech.info/src/custom/includes')
#print(os.path.dirname(rootdir) + '/django/n.libtech.info/src/custom/includes')
#exit(0)

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

import psutil

###

includePath='/home/libtech/repo/django/n.libtech.info/src/custom/includes'
sys.path.append(includePath) # os.path.join(os.path.dirname(__file__), '..', 'includes') #FIXME

from customSettings import repoDir, djangoDir, djangoSettings
from crawlFunctions import getAPJobcardData, computeWorkPaymentStatus, crawlWagelists, parseMuster, getAPJobcardData, processAPJobcardData
#from nregaFunctions import is_ascii

sys.path.append(djangoDir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)

import django

# This is so Django knows where to find stuff.
# This is so my local_settings.py gets loaded.
django.setup()

from nrega.models import State,District,Block,Panchayat,PaymentInfo,LibtechTag,CrawlQueue,Worker


#######################
# Global Declarations
#######################

timeout = 10
dirname = 'jobcards'


#############
# Functions
#############

def on_terminate(proc):
    print("process {} terminated with exit code {}".format(proc, proc.returncode))

def process_cleanup(logger):
    logger.info('Process Cleanup Begins')
    children = psutil.Process().children(recursive=True)
    for p in children:
        logger.info('Terminating the subproces[%s]' % p.pid)
        try:
            p.terminate()
            p.wait()
        except Exception as e:
            logger.error('Kill failed with Exception[%s]' % e)
    gone, alive = psutil.wait_procs(children, timeout=10, callback=on_terminate)

    logger.info('Processes still alive [%s]' % alive)
    for p in children: # alive:
        logger.info('Killing the subproces[%s]' % p.pid)
        try:
            p.kill()
            p.wait()
        except Exception as e:
            logger.error('Kill failed with Exception[%s]' % e)
    logger.info('Cleaning up /tmp')
    os.system('cd /tmp; pkill firefox; pkill Xvfb; rm -rf rust_mozprofile.* tmp*')
    logger.info('Process Cleanup Ends')
    
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
        # driver = driverInitialize(timeout=3)  # FIXME
        # driver.get(url)
        logger.critical('Aborting the current attempt')
        return 'FAILURE'

    try:
        html_source = driver.page_source.replace('<head>',
                                                 '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    except Exception as e:
        logger.error('Exception getting HTML source - EXCEPT[%s]' % e)
        return 'ABORT'
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
        #return 'FAILURE'
    #time.sleep(timeout)

    try:
        logger.info('Clicking Submit')
        elem = driver.find_element_by_id('ctl00_MainContent_btnMakePayment')
        elem.click()
    except Exception as e:
        logger.error('Exception Clicking Submit for jobcard[%s] - EXCEPT[%s]' % (jobcard_no,e))
        return 'ABORT'
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

    try:
        parent_handle = driver.current_window_handle
    except Exception as e:
        logger.error('Exception when assining window handle[%s] - EXCEPT[%s]' % (jobcard_no,e))
        return 'ABORT'
        
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
        return 'ABORT'
        
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

def fetch_rn6_reports(logger):
    logger.info('Fetch the jobcards')

    display = displayInitialize(0)
    driver = driverInitialize(timeout=3, options='--headless') # driverInitialize(path='/opt/firefox/', timeout=3)
    
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise    
    
    current_panchayat = None
    current_jobcard = None
    filename = dirname + '/status.dat'
    if os.path.exists(filename):
        with open(filename, 'r') as status_file:
            logger.info('Reading [%s]' % filename)
            status = status_file.read().strip()
        (current_panchayat, current_jobcard) = status.split(',')

    if False:
        state = None
        district_name = 'MAHABUBNAGAR'
        block_name = 'Damaragidda'
        # block_id = block_lookup[block_name]
        block_id = '4378'
    else:
        state = 'ap'
        district_name = 'VISAKHAPATNAM'
        block_name = 'Gangaraju Madugula'
        block_id = None

    if False:
        # result = fetch_rn6_report(logger, driver, state='ap', district_name='ANANTAPUR', jobcard_no='121673411011010257-02')
        # result = fetch_rn6_report(logger, driver, district_name='MAHABUBNAGAR', jobcard_no='141990515024010071-08')
        # result = fetch_rn6_report(logger, driver, state='ap', district_name='VISAKHAPATNAM', jobcard_no='030300927050030026-02')
        result = fetch_rn6_report(logger, driver, state=state, district_name=district_name, jobcard_no=current_jobcard, block_name=block_name, panchayat_name=current_panchayat)
        driverFinalize(driver)
        displayFinalize(display)
        #process_cleanup(logger)
        return 'SUCCESS'

    if not block_id:
        panchayats = Panchayat.objects.filter(block__name=block_name)
        
        is_panchayat = True
        for panchayat in panchayats:
            panchayat_name = panchayat.name
            logger.info('Panchayat[%s]' % panchayat_name)
            if current_panchayat and is_panchayat and panchayat_name != current_panchayat:
                logger.debug('Already downloaded. Skipping[%s]' % panchayat_name)
                continue
            is_panchayat = False
            workers = Worker.objects.filter(jobcard__panchayat=panchayat)
            is_downloaded = True
            for worker in workers:
                jobcard = (worker.jobcard.tjobcard + '-0' + str(worker.applicantNo))
                if current_panchayat and (panchayat_name == current_panchayat and is_downloaded and (jobcard != current_jobcard)): 
                    logger.debug('Skipping[%s]' % jobcard)
                    continue            
                is_downloaded = False
                logger.info('Fetch details for jobcard[%s]' % jobcard)
                result = fetch_rn6_report(logger, driver, state=state, district_name=district_name, jobcard_no=jobcard, block_name=block_name, panchayat_name=panchayat_name)
                if result != 'SUCCESS':
                    logger.error('Failure returned [%s]' % result)
                    if result == 'ABORT':
                        logger.info('Finalizing Driver')
                        try:
                            driverFinalize(driver)
                        except:
                            pass  # FIXME should not suppress!
                        logger.info('Finalizing Display')
                        displayFinalize(display)
                        process_cleanup(logger)
                        time.sleep(10)
                        return 'FAILURE'
                    else:
                        continue  # FIXME why is this even needed. Why is it not working?
                with open(filename, 'w') as status_file:
                    logger.info('Updating status file [%s]' % filename)
                    status = panchayat_name + ',' + jobcard
                    logger.info('Status[%s]' % status)
                    status_file.write(status)
                    
        return 'SUCCESS'


    # This part can go eventual - FIXME  ---vvv
    
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
            result = fetch_rn6_report(logger, driver, state=state, district_name=district_name, jobcard_no=jobcard, block_name=block_name, panchayat_name=panchayat_name)
            if result != 'SUCCESS':
                logger.error('Failure returned [%s]' % result)
                #time.sleep(3)
                continue  # FIXME why is this even needed. Why is it not working?

    driverFinalize(driver) 
    displayFinalize(display)
    return 'SUCCESS'

def parse_rn6_reports(logger):
    logger.info('Parse the RN6 HTMLs')

    # filename = 'jobcards/Gangaraju Madugula_G.Madugula_030291104271010017-01_ledger_details.html'
    filename = 'jobcards/Gangaraju Madugula_Gaduthuru_030291116195010015-04_ledger_details.html'
    
    with open(filename, 'r') as html_file:
        logger.info('Reading [%s]' % filename)
        html_source = html_file.read()

    bs = BeautifulSoup(html_source, 'html.parser')

    # tabletop = bs.find(id='ctl00_MainContent_PrintContent')
    # logger.info(tabletop)
    table = bs.find(id='tblDetails')
    logger.debug(table)

    account_no = table.find(id='ctl00_MainContent_lblAccountNo').text.strip()
    logger.info('account_no [%s]' % account_no)

    bo_name = table.find(id='ctl00_MainContent_lblBOName').text.strip()
    logger.info('bo_name [%s]' % bo_name)

    jobcard_id = table.find(id='ctl00_MainContent_lblJobcardPensionID').text.strip()
    logger.info('jobcard_id [%s]' % jobcard_id)

    so_name = table.find(id='ctl00_MainContent_lblSOName').text.strip()
    logger.info('so_name [%s]' % so_name)

    account_holder_name = table.find(id='ctl00_MainContent_lblName').text.strip()
    logger.info('account_holder_name [%s]' % account_holder_name)

    mandal_name = table.find(id='ctl00_MainContent_lblMandalName').text.strip()
    logger.info('mandal_name [%s]' % mandal_name)

    table = bs.find(id='ctl00_MainContent_dgLedgerReport')
    logger.debug(table)
    try:
        tr_list = table.findAll('tr')
    except:
        logger.info('No Transactions')
        return 'SUCCESS'
    logger.debug(tr_list)

    # desired_columns =  [1, ]
    for tr in tr_list:
        logger.debug(tr)
        td_list = tr.findAll('td')

        transaction_date = td_list[1].text.strip()
        logger.info('transaction_date[%s]' % transaction_date)

        transaction_ref = td_list[2].text.strip()
        logger.info('transaction_ref[%s]' % transaction_ref)

        withdrawn_at = td_list[3].text.strip()
        logger.info('withdrawn_at[%s]' % withdrawn_at)

        deposit_inr = td_list[4].text.strip()
        logger.info('deposit_inr[%s]' % deposit_inr)

        withdrawal_inr = td_list[5].text.strip()
        logger.info('withdrawal_inr[%s]' % withdrawal_inr)

        availalbe_balance = td_list[6].text.strip()
        logger.info('availalbe_balance[%s]' % availalbe_balance)


    '''    
    tr = tr_list[0]
    td = tr.find('td')
    td = td.findNext()
    account_no = td.text.strip()
    logger.info('account_no [%s]' % account_no)
    
    td = td.findNext()
    td = td.findNext()
    td = td.findNext()
    bo_name = td.text.strip()
    logger.info('bo_name [%s]' % bo_name)

    ###
    
    tr = tr_list[1]
    logger.info(tr)
    td = tr.find('td')
    td = td.findNext()
    td = td.findNext()
    jobcard_id = td.text.strip()
    logger.info('jobcard_id [%s]' % jobcard_id)
    
    td = td.findNext()
    td = td.findNext()
    td = td.findNext()
    td = td.findNext()
    so_name = td.text.strip()
    logger.info('so_name [%s]' % so_name)

    ###
    
    tr = tr_list[2]
    logger.info(tr)
    td = tr.find('td')
    td = td.findNext()
    account_holder_name = td.text.strip()
    logger.info('account_holder_name [%s]' % account_holder_name)
    
    td = td.findNext()
    mandal_name = td.text.strip()
    logger.info('mandal_name [%s]' % mandal_name)
    '''
    return 'SUCCESS'

class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = loggerFetch('info')
        self.logger.info('BEGIN PROCESSING...')

    def tearDown(self):
        self.logger.info('...END PROCESSING')

    def test_fetch_rn6_report(self):
        count = 0
        while True:
            count += 1
            result = fetch_rn6_reports(self.logger)
            if result == 'SUCCESS' or count == 10:
                break
        self.assertEqual(result, 'SUCCESS')

    @unittest.skip('Skipping the parse')
    def test_parse_rn6_report(self):
        result = parse_rn6_reports(self.logger)
        self.assertEqual(result, 'SUCCESS')
        
if __name__ == '__main__':
    unittest.main()
