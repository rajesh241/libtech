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
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, TimeoutException, WebDriverException
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
import pandas as pd

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

        html_source = driver.page_source.replace('<head>',
                                                 '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
        logger.debug("HTML Fetched [%s]" % html_source)
    

        bs = BeautifulSoup(html_source, 'html.parser')

        # elem = driver.find_element_by_id('ctl00_MainContent_ddlDistrict')
        # elem = driver.find_element_by_name('ctl00$MainContent$ddlDistrict')
        # elem.send_keys(district_name)

        select = Select(driver.find_element_by_id('ctl00_MainContent_ddlDistrict'))
        select.select_by_visible_text(district_name)
        # elem.click()
        # elem = driver.find_element_by_xpath("//select[@name='ctl00$MainContent$ddlDistrict']/option[text()=district_name]").click()

        logger.info('Clicking Jobcard radio button')
        # elem = driver.find_element_by_id('ctl00_MainContent_txtSSPPEN') FIXME
        elem = driver.find_element_by_css_selector("input[type='radio'][value='rbnSSPPEN']")
        elem.click()

        logger.info('Entering Jobcard[%s]' % jobcard_no)
        elem = driver.find_element_by_id('ctl00_MainContent_txtSSPPEN')
        elem.send_keys(jobcard_no)
        elem.click()

        logger.info('Clicking Submit')
        elem = driver.find_element_by_id('ctl00_MainContent_btnMakePayment')
        elem.click()

        logger.info('Clicking Select radio button')
        elem = driver.find_element_by_css_selector("input[type='radio'][value='rbSelect']")
        elem.click()
    
        logger.info('Clicking View Ledger')
        elem = driver.find_element_by_id('ctl00_MainContent_btnTxDetails')
        elem.click()
        
        parent_handle = driver.current_window_handle
        logger.info("Handles : %s" % driver.window_handles + "Number : %d" % len(driver.window_handles))
        
        if len(driver.window_handles) == 2:
            driver.switch_to.window(driver.window_handles[-1])
            #time.sleep(2)
        else:
            logger.error("Handlers gone wrong [" + str(driver.window_handles) + 'jobcard %s' % jobcard_no + "]")
            driver.save_screenshot('./logs/button_'+jobcard_no+'.png')
            return 'FAILURE'
    except NoSuchElementException as e:
        logger.error('Exception for jobcard[%s] - EXCEPT[%s:%s]' % (jobcard_no, type(e), e))
        return 'FAILURE'
    except (WebDriverException, SessionNotCreatedException) as e:
        logger.critical('Not found for jobcard[%s] - EXCEPT[%s:%s]' % (jobcard_no, type(e), e))
        return 'ABORT'
    except BrokenPipeError as e:
        logger.error('Broken Pipe for jobcard[%s] - EXCEPT[%s:%s]' % (jobcard_no, type(e), e))
        return 'FAILURE'
    except Exception as e:
        logger.error('Exception for jobcard[%s] - EXCEPT[%s:%s]' % (jobcard_no, type(e), e))
        return 'FAILURE'

    try:
        logger.info('Waiting for the dialog box to open')
        elem = WebDriverWait(driver, timeout).until(
          EC.presence_of_element_located((By.CLASS_NAME, "btn"))
        )
    except TimeoutException as e:
        logger.error('Timeout waiting for dialog box - EXCEPT[%s:%s]' % (type(e), e))
        driver.close()
        driver.switch_to.window(parent_handle)
        return 'ABORT'
    except Exception as e:
        logger.error('Exception on WebDriverWait(10) - EXCEPT[%s:%s]' % (type(e), e))
        driver.save_screenshot('./button_'+jobcard_no+'.png')
        driver.close()
        driver.switch_to.window(parent_handle)
        return 'ABORT'

    try:
        html_source = driver.page_source.replace('<head>',
                                                 '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
        logger.debug("HTML Fetched [%s]" % html_source)
        filename = '%s/%s_%s_%s_ledger_details.html' % (dirname, block_name, panchayat_name, jobcard_no)
        with open(filename, 'w') as html_file:
            logger.info('Writing [%s]' % filename)
            html_file.write(html_source)
            
        driver.close()
        driver.switch_to.window(parent_handle)
    except WebDriverException:
        logger.critical('Aborting the current attempt')
        return 'ABORT'
    except SessionNotCreatedException:
        logger.critical('Aborting the current attempt')
        return 'ABORT'
    except Exception as e:
        logger.error('Exception for jobcard[%s] - EXCEPT[%s:%s]' % (jobcard_no, type(e), e))
        return 'FAILURE'

        
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
                jobcard_no = (worker.jobcard.tjobcard + '-0' + str(worker.applicantNo))
                if current_panchayat and (panchayat_name == current_panchayat and is_downloaded and (jobcard != current_jobcard)): 
                    logger.debug('Skipping[%s]' % jobcard_no)
                    continue            
                is_downloaded = False
                logger.info('Fetch details for jobcard_no[%s]' % jobcard_no)
                result = fetch_rn6_report(logger, driver, state=state, district_name=district_name, jobcard_no=jobcard_no, block_name=block_name, panchayat_name=panchayat_name)
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

def parse_rn6_report(logger, filename=None, panchayat_name=None, village_name=None, jobcard_no=None):
    logger.info('Parse the RN6 HTML file')

    try:
        with open(filename, 'r') as html_file:
            logger.info('Reading [%s]' % filename)
            html_source = html_file.read()
    except Exception as e:
        logger.error('Exception when opening file for jobcard[%s] - EXCEPT[%s:%s]' % (jobcard_no, type(e), e))
        raise e
        
    data = pd.DataFrame([], columns=['S.No', 'Mandal Name', 'Gram Panchayat', 'Village', 'Job card number/worker ID', 'Name of the wageseeker', 'Credited Date', 'Deposit (INR)', 'Debited Date', 'Withdrawal (INR)', 'Available Balance (INR)', 'Diff. time credit and debit'])
    try:
        df = pd.read_html(filename, attrs = {'id': 'ctl00_MainContent_dgLedgerReport'}, index_col='S.No.', header=0)[0]
        # df = pd.read_html(filename, attrs = {'id': 'ctl00_MainContent_dgLedgerReport'})[0]
    except Exception as e:
        logger.error('Exception when reading transaction table for jobcard[%s] - EXCEPT[%s:%s]' % (jobcard_no, type(e), e))
        return data
    logger.info('The transactions table read:\n%s' % df)
    
    bs = BeautifulSoup(html_source, 'html.parser')

    # tabletop = bs.find(id='ctl00_MainContent_PrintContent')
    # logger.info(tabletop)
    table = bs.find(id='tblDetails')
    logger.debug(table)

    account_no = table.find(id='ctl00_MainContent_lblAccountNo').text.strip()
    logger.debug('account_no [%s]' % account_no)

    bo_name = table.find(id='ctl00_MainContent_lblBOName').text.strip()
    logger.debug('bo_name [%s]' % bo_name)

    jobcard_id = table.find(id='ctl00_MainContent_lblJobcardPensionID').text.strip()
    logger.debug('jobcard_id [%s]' % jobcard_id)

    if jobcard_id != jobcard_no:
        logger.critical('Something went terribly wrong with [%s != %s]!' % (jobcard_id, jobcard_no))

    so_name = table.find(id='ctl00_MainContent_lblSOName').text.strip()
    logger.debug('so_name [%s]' % so_name)

    account_holder_name = table.find(id='ctl00_MainContent_lblName').text.strip()
    logger.debug('account_holder_name [%s]' % account_holder_name)

    mandal_name = table.find(id='ctl00_MainContent_lblMandalName').text.strip()
    logger.debug('mandal_name [%s]' % mandal_name)

    table = bs.find(id='ctl00_MainContent_dgLedgerReport')
    logger.debug(table)
    try:
        tr_list = table.findAll('tr')
    except:
        logger.info('No Transactions')
        return 'SUCCESS'
    logger.debug(tr_list)

    # desired_columns =  [1, ]
    # for row in df.itertuples(index=True, name='Pandas'):
    debit_timestamp = pd.to_datetime(0)

    df = df.iloc[::-1] # Reverse the order for calculating diff time Debit dates are easier to record in this order
    for index, row in df.iterrows():
        logger.debug('%d: %s' % (index, row))

        serial_no = index
        logger.debug('serial_no[%s]' % serial_no)

        transaction_date = row['Transaction Date']
        logger.debug('transaction_date[%s]' % transaction_date)

        transaction_ref = row['Transaction Reference']
        logger.debug('transaction_ref[%s]' % transaction_ref)

        withdrawn_at = row['Withdrawn at']
        logger.debug('withdrawn_at[%s]' % withdrawn_at)

        deposit_inr = row['Deposit (INR)']
        logger.debug('deposit_inr[%s]' % deposit_inr)

        withdrawal_inr = row['Withdrawal (INR)']
        logger.debug('withdrawal_inr[%s]' % withdrawal_inr)

        availalbe_balance = row['Available Balance (INR)']
        logger.debug('availalbe_balance[%s]' % availalbe_balance)

        if deposit_inr == 0:
            (credited_date, debited_date, diff_time, debit_timestamp) = (transaction_date, 0, 0, pd.to_datetime(transaction_date, dayfirst=True)) #  datetime.strptime(transaction_date, "%d/%m/%Y").timestamp())
        else:
            (credited_date, debited_date, diff_time) = (0, transaction_date, debit_timestamp - pd.to_datetime(transaction_date, dayfirst=True)) # datetime.strptime(transaction_date, "%d/%m/%Y").timestamp())
        logger.debug('credited_date[%s]' % credited_date)
        logger.debug('debited_date[%s]' % debited_date)
        logger.debug('diff_time[%s]' % diff_time)
        
        #csv_buffer.append('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' %(serial_no, mandal_name, bo_name, so_name, jobcard_id, account_holder_name, credited_date, debited_date, withdrawal_inr, availalbe_balance, diff_time))
        data = data.append({'S.No': serial_no, 'Mandal Name': mandal_name, 'Gram Panchayat': panchayat_name, 'Village': village_name, 'Job card number/worker ID': jobcard_id, 'Name of the wageseeker': account_holder_name, 'Credited Date': credited_date, 'Deposit (INR)': deposit_inr, 'Debited Date': debited_date, 'Withdrawal (INR)': withdrawal_inr, 'Available Balance (INR)': availalbe_balance, 'Diff. time credit and debit': diff_time}, ignore_index=True)

    data = data.set_index('S.No')
    data = data.iloc[::-1]  # Reverse the order back to normal        
    logger.info('The final table:\n%s' % data)

    return data

def dump_rn6_reports(logger):
    #from datetime import datetime

    from secure.libtech_settings import LIBTECH_AWS_ACCESS_KEY_ID,LIBTECH_AWS_SECRET_ACCESS_KEY
    from libtech.settings import AWS_STORAGE_BUCKET_NAME,AWS_S3_REGION_NAME,MEDIA_URL,S3_URL
    
    import boto3
    from boto3.session import Session
    from botocore.client import Config
    
    logger.info('Dump the RN6 HTMLs')

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
        # filename = 'jobcards/Gangaraju Madugula_G.Madugula_030291104271010017-01_ledger_details.html'
        filename = 'jobcards/Gangaraju Madugula_Gaduthuru_030291116195010015-04_ledger_details.html'
        #csv_buffer = ['S.No,Mandal Name,Gram Panchayat,Village,Job card number/worker ID,Name of the wageseeker,Credited Date,Deposit (INR),Debited Date,Withdrawal (INR),Available Balance (INR),Diff. time credit and debit\n']
        return 'SUCCESS'

    panchayats = Panchayat.objects.filter(block__name=block_name)        
    for panchayat in panchayats:
        panchayat_name = panchayat.name
        logger.info('Panchayat[%s]' % panchayat_name)
        workers = Worker.objects.filter(jobcard__panchayat=panchayat)
        for worker in workers:
            jobcard_no = (worker.jobcard.tjobcard + '-0' + str(worker.applicantNo))
            logger.debug('Parse HTML for jobcard_no[%s]' % jobcard_no)
            
            filename = '%s/%s_%s_%s_ledger_details.html' % (dirname, block_name, panchayat_name, jobcard_no)
            village_name = worker.jobcard.village.name
            logger.debug('Village Name[%s]' % village_name)
            try:
                data = parse_rn6_report(logger, filename=filename, panchayat_name=panchayat_name, village_name=village_name, jobcard_no=jobcard_no)
            except:
                csv_filename = filename.replace('.html','.XXX')
                open(csv_filename, 'a').close()
                logger.info('Marking the file [%s]' % csv_filename)
                break # continue
                
            csv_filename = filename.replace('.html','.csv')
            with open(csv_filename, 'w') as csv_file:
                logger.info('Writing to CSV [%s]' % csv_filename)
                csv_file.write(data.to_csv())

            break

    tarball_filename = '%s_%s.bz2' % (block_name, pd.Timestamp.now())
    tarball_filename = tarball_filename.replace(' ','-').replace(':','-')
    cmd = 'tar cjf %s %s/*.csv' % (tarball_filename, dirname)
    logger.info('Running cmd[%s]' % cmd)
    os.system(cmd)
    with open(tarball_filename, 'rb') as tarball_file:
        tarball_content = tarball_file.read()
    cloud_filename='media/temp/rn6/%s' % tarball_filename
    session = Session(aws_access_key_id=LIBTECH_AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=LIBTECH_AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3',config=Config(signature_version='s3v4'))
    s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(ACL='public-read',Key=cloud_filename, Body=tarball_content)
    public_url='https://s3.ap-south-1.amazonaws.com/libtech-nrega1/%s' % cloud_filename
    logger.info('CSV File written on AWS[%s]' % public_url)

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
            if result == 'SUCCESS' or count == 50:
                break
        self.assertEqual(result, 'SUCCESS')

    def test_dump_rn6_report(self):
        result = dump_rn6_reports(self.logger)
        self.assertEqual(result, 'SUCCESS')
        
if __name__ == '__main__':
    unittest.main()
