from bs4 import BeautifulSoup
from PIL import Image
from subprocess import check_output

import os
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(CUR_DIR)
REPO_DIR = os.path.dirname(ROOT_DIR)

import sys
sys.path.insert(0, ROOT_DIR)

import errno
import pytesseract

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

import requests
import time
import unittest

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize, driverFinalize, displayInitialize, displayFinalize

import psutil
import pandas as pd
import json


#######################
# Global Declarations
#######################

timeout = 3
directory = 'reports'
base_url = 'https://meebhoomi.ap.gov.in/'

village_list = [('విశాఖపట్నం', 'అచ్యుతాపురం', 'జోగన్నపాలెం'), ('విశాఖపట్నం', 'అనంతగిరి', 'నిన్నిమామిడి'), ('విశాఖపట్నం', 'అనందపురం', 'ముచ్చెర్ల')]


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


def fetch_parent(logger, driver, url=None):
    if not url:
        url = base_url + 'ROR.aspx'
    filename = '%s/parent.html' % (directory)
    logger.info("Fetching...[%s]" % url)

    try:
        driver.get(url)
        # time.sleep(5)
        
        logger.info('Waiting for the base page to load...')
        elem = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtCaptcha"))
        )
    except Exception as e:
        logger.error('Exception on WebDriverWait(10) - EXCEPT[%s:%s]' % (type(e), e))
        return 'FAILURE'
        
    html_source = driver.page_source.replace('<head>',
                                                 '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    logger.debug("HTML Fetched [%s]" % html_source)
    
    with open(filename, 'w') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(html_source)
        
    return BeautifulSoup(html_source, 'html.parser')


def fetch_lookup(logger, filename, url=None, cookies=None, headers=None, data=None):
    if os.path.exists(filename):
        logger.info('File already downloaded. Reading [%s]...' % filename)
        with open(filename) as json_file:
            lookup = json.load(json_file)
        return lookup
    
    logger.info('Fetching URL[%s]...' % url)
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    logger.info(response.content)
    
    data = pd.read_json(response.content)
    if data['d'].empty:
        logger.error('Why empty?')
        #exit(0)
    df = pd.DataFrame(data['d'].tolist(), columns=['name', 'value'])

    lookup = df.set_index('value').to_dict('dict')['name']
    logger.debug(lookup)

    with open(filename, 'w') as json_file:
        logger.info('Writing [%s]' % filename)
        json_file.write(json.dumps(lookup))
        
    return lookup

    
def fetch_captcha(logger, cookies=None, url=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',
        'Accept': 'image/webp,*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://meebhoomi.ap.gov.in/ROR.aspx',
        'DNT': '1',
    }

    #response = requests.get('https://meebhoomi.ap.gov.in/CaptchaImage.axd', headers=headers, params=params, cookies=cookies)
    response = requests.get(url, headers=headers, cookies=cookies)
    
    filename = 'captcha.jpg'
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.content)

    check_output(['convert', filename, '-resample', '35', filename])

    return pytesseract.image_to_string(Image.open(filename), lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    #return pytesseract.image_to_string(Image.open(filename), lang='eng', config='-c tessedit_char_whitelist=0123456789')



def fetch_appi_gram1b_report(logger, driver, cookies=None, dirname=None, url=None, district_name=None, mandal_name=None, village_name=None):
    logger.info('Verify District[%s] > Mandal[%s] > Village[%s]' % (district_name, mandal_name, village_name))
    if not dirname:
        dirname = directory

    if not url:
        url = base_url + 'ROR.aspx'
    
    if not district_name:
        district_name = 'శ్రీకాకుళం'

    if not mandal_name:
        mandal_name = 'కొత్తూరు'

    if not village_name:
        village_name = 'అల్ది'

    captcha_text = ''
    
    filename = '%s/%s_%s_%s_rejected_payments.html' % (dirname, district_name, mandal_name, village_name)
    if os.path.exists(filename):
        logger.info('File already downloaded. Skipping [%s]' % filename)
        return 'SUCCESS'

    bs = fetch_parent(logger, driver)
    
    #timeout = 2
    try:
        select = Select(driver.find_element_by_id('ContentPlaceHolder1_ddlDist'))
        select.select_by_visible_text(district_name)
        # elem.click()
        logger.info('Selected District [%s]' % district_name)
        time.sleep(timeout)

        select = Select(driver.find_element_by_id('ContentPlaceHolder1_ddlMandals'))
        select.select_by_visible_text(mandal_name)
        # elem.click()
        logger.info('Selected Mandal [%s]' % mandal_name)
        time.sleep(timeout)

        select = Select(driver.find_element_by_id('ContentPlaceHolder1_ddlVillageName'))
        select.select_by_visible_text(village_name)
        # elem.click()
        logger.info('Selected Village [%s]' % village_name)
        time.sleep(timeout)


        imgs = bs.findAll("img")
        logger.info('imgs[%s]' % imgs)
        logger.info('no of images = %s!' % len(imgs))
        if len(imgs) < 4:
            img = imgs[1]
            #return 'FAILURE'
        else:
            img = imgs[3]
        logger.debug('Yippie [%s]' % img.attrs)

        url = base_url + img['src']
        logger.info('Fetching URL[%s]' % url)

        captcha_text = fetch_captcha(logger, cookies, url)
        time.sleep(timeout)
        logger.info('Captcha Text[%s]' % captcha_text)
        if len(captcha_text) != 5 or not captcha_text.isdigit():
            logger.warning('Incorrect Captcha length[%s]' % len(captcha_text))
            return 'FAILURE'
        
        elem = driver.find_element_by_id('ContentPlaceHolder1_txtCaptcha')
        elem.send_keys(captcha_text)
        time.sleep(timeout)
        elem.click()

        logger.info('Clicking Submit')
        elem = driver.find_element_by_id('ContentPlaceHolder1_btn_go')
        elem.click()
        time.sleep(timeout)
        
    except Exception as e:
        logger.error('Exception for Captcha[%s] - EXCEPT[%s:%s]' % (captcha_text, type(e), e))
        time.sleep(10)
        return 'FAILURE'

    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                   'Timed out waiting for PA creation ' +
                                   'confirmation popup to appear.')

        alert = driver.switch_to.alert
        alert.accept()
        logger.warning('Handled Alert!')
        return 'FAILURE'
    except TimeoutException:
        logger.warning('Time Out waiting for ALERT')
    except Exception as e:
        logger.error('Exception during wait for alert captcha_id[%s] - EXCEPT[%s:%s]' % (captcha_text, type(e), e))
        
    if False:
        try:
            alert = driver.switch_to.alert  # driver.switch_to_alert()
            alert.accept()
        except:
            logger.warning('No ALERT around Submit')
            
    parent_handle = driver.current_window_handle
    #logger.info("Handles : %s" % driver.window_handles + "Number : %d" % len(driver.window_handles))
    logger.info("Handles : [%s]    Number : [%d]" % (driver.window_handles, len(driver.window_handles)))
        
    if len(driver.window_handles) == 2:
        logger.info('Switching Window...')
        try:
            alert = driver.switch_to.alert  # driver.switch_to_alert()
            alert.accept()
        except:
            logger.warning('No ALERT Around Handles')
        driver.switch_to.window(driver.window_handles[1])
        logger.info('Switched!!!')
        #time.sleep(2)
    else:
        logger.error("Handlers gone wrong [" + str(driver.window_handles) + 'captcha_id %s' % captcha_text + "]")
        driver.save_screenshot('./button_'+captcha_text+'.png')
        try:
            alert = driver.switch_to.alert  # driver.switch_to_alert()
            alert.accept()
        except:
            logger.warning('No ALERT')
        return 'FAILURE'
    try:
        logger.info('Waiting for the dialog box to open')
        elem = WebDriverWait(driver, timeout).until(
          EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_lbl_village"))
        )
    except (WebDriverException) as e:
        logger.critical('Not found for captcha_id[%s] - EXCEPT[%s:%s]' % (captcha_text, type(e), e))
        driver.close()
        driver.switch_to.window(parent_handle)
        return 'ABORT'
    except TimeoutException as e:
        logger.error('Timeout waiting for dialog box - EXCEPT[%s:%s]' % (type(e), e))
        driver.close()
        driver.switch_to.window(parent_handle)
        return 'ABORT'
    except Exception as e:
        logger.error('Exception on WebDriverWait(10) - EXCEPT[%s:%s]' % (type(e), e))
        driver.save_screenshot('./button_'+captcha_text+'.png')
        driver.close()
        driver.switch_to.window(parent_handle)
        return 'ABORT'

    if True:
        try:
            alert = driver.switch_to.alert  # driver.switch_to_alert()
            alert.accept()
        except:
            logger.warning('No ALERT around dumping html')
    try:
        html_source = driver.page_source.replace('<head>',
                                                 '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
        logger.debug("HTML Fetched [%s]" % html_source)
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
        logger.error('Exception for captcha_id[%s] - EXCEPT[%s:%s]' % (captcha_text, type(e), e))
        return 'FAILURE'
        
    return 'SUCCESS'


def fetch_appi_reports(logger, dirname=None, url=None):
    logger.info('Fetch the Gram 1B reports into dir[%s]' % dirname)

    display = displayInitialize(1)
    #driver = driverInitialize(timeout=3, options='--headless') # driverInitialize(path='/opt/firefox/', timeout=3)
    driver = driverInitialize(timeout=3) # driverInitialize(path='/opt/firefox/', timeout=3)
    
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise    

    #driver.get(base_url)
    fetch_parent(logger, driver)
    '''
    url = base_url

    try:
        logger.info('Requesting URL[%s]' % url)
        response = requests.get(url, timeout=timeout, cookies=cookies)
    except Exception as e:
        logger.error('Caught Exception[%s]' % e) 
    '''

    cookies = driver.get_cookies()
    logger.info('Cookies[%s]' % cookies)
    logger.debug('Cookie -> Session ID[%s]' % cookies[0]['value'])
    
    cookies = {
        'hibext_instdsigdipv2': '1',
        'ASP.NET_SessionId': cookies[0]['value'],
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json; charset=utf-8',
        'Origin': 'https://meebhoomi.ap.gov.in',
        'Connection': 'keep-alive',
        'Referer': 'https://meebhoomi.ap.gov.in/ROR.aspx',
        'DNT': '1',
    }

    data = '{"knownCategoryValues":"","category":"District"}'
    
    filename = '%s/district.json' % directory
    district_url = base_url + 'UtilityWebService.asmx/GetDistricts'
    district_lookup = fetch_lookup(logger, filename, url=district_url, cookies=cookies, headers=headers, data=data)
    logger.info(district_lookup)

    mandal_url = base_url + 'UtilityWebService.asmx/GetMandals'
    for district_no, district_name in district_lookup.items():
        if district_no != '3':
            continue
        logger.info('Fetch Mandals for District[%s] = [%s]' % (district_name, district_no))
        data = '{"knownCategoryValues":"District:%s;","category":"Mandal"}' % (district_no)
        logger.info('With Data[%s]' % data)

        filename = '%s/%s_%s_mandal_list.json' % (directory, district_no, district_name)
        mandal_lookup = fetch_lookup(logger, filename, url=mandal_url, cookies=cookies, headers=headers, data=data)
        logger.info(mandal_lookup)

        village_url = base_url + 'UtilityWebService.asmx/GetVillages'
        for mandal_no, mandal_name in mandal_lookup.items():
            logger.info('Fetch Villages for Mandal[%s] = [%s]' % (mandal_name, mandal_no))
            data = '{"knownCategoryValues":"District:%s;Mandal:%02s;","category":"Mandal"}' % (district_no, mandal_no)
            logger.info('With Data[%s]' % data)

            filename = '%s/%s_%s_village_list.json' % (directory, district_name, mandal_name)
            village_lookup = fetch_lookup(logger, filename, url=village_url, cookies=cookies, headers=headers, data=data)
            logger.info(village_lookup)

            for village_no, village_name in village_lookup.items():
                logger.info('Fetch Gram 1B Report for District[%s] > Mandal[%s] > Village[%s]' % (district_name, mandal_name, village_name))
                result = fetch_appi_gram1b_report(logger, driver, cookies=cookies,
                                                  district_name=district_name.strip(),
                                                  mandal_name=mandal_name.strip(),
                                                  village_name=village_name.strip())
                if result == 'ABORT':
                    return result

    '''
    if False:
        result = fetch_appi_gram1b_report(logger, driver, bs=bs, cookies=cookies, dirname=dirname, url=url)
        driverFinalize(driver)
        displayFinalize(display)
        #process_cleanup(logger)
        return 'SUCCESS'

    retries = 3
    while True and retries:
        result = fetch_appi_gram1b_report(logger, driver, bs=bs, cookies=cookies, dirname=dirname, url=url)
        retries -= 1
        if result == 'SUCCESS':
            break
    '''
    
    driverFinalize(driver) 
    displayFinalize(display)
    return result # 'SUCCESS'


def fetch_reports_for(logger, dirname=None, url=None, villages=None):
    logger.info('Fetch the Gram 1B reports into dir[%s]' % dirname)

    display = displayInitialize(1)
    driver = driverInitialize(timeout=3) # driverInitialize(path='/opt/firefox/', timeout=3)
    
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise    

    fetch_parent(logger, driver)

    cookies = driver.get_cookies()
    logger.info('Cookies[%s]' % cookies)
    logger.debug('Cookie -> Session ID[%s]' % cookies[0]['value'])
    
    cookies = {
        'hibext_instdsigdipv2': '1',
        'ASP.NET_SessionId': cookies[0]['value'],
    }

    for (district_name, mandal_name, village_name) in villages:
        logger.info('Fetch Gram 1B Report for District[%s] > Mandal[%s] > Village[%s]' % (district_name, mandal_name, village_name))
        result = fetch_appi_gram1b_report(logger, driver, cookies=cookies,
                                          district_name=district_name.strip(),
                                          mandal_name=mandal_name.strip(),
                                          village_name=village_name.strip())    
    driverFinalize(driver) 
    displayFinalize(display)
    return result # 'SUCCESS'


def parse_appi_report(logger, filename=None, panchayat_name=None, village_name=None, captcha_text=None):
    logger.info('Parse the RN6 HTML file')

    try:
        with open(filename, 'r') as html_file:
            logger.info('Reading [%s]' % filename)
            html_source = html_file.read()
    except Exception as e:
        logger.error('Exception when opening file for captcha_id[%s] - EXCEPT[%s:%s]' % (captcha_text, type(e), e))
        raise e
        
    data = pd.DataFrame([], columns=['S.No', 'Mandal Name', 'Gram Panchayat', 'Village', 'Job card number/worker ID', 'Name of the wageseeker', 'Credited Date', 'Deposit (INR)', 'Debited Date', 'Withdrawal (INR)', 'Available Balance (INR)', 'Diff. time credit and debit'])
    try:
        df = pd.read_html(filename, attrs = {'id': 'ctl00_MainContent_dgLedgerReport'}, index_col='S.No.', header=0)[0]
        # df = pd.read_html(filename, attrs = {'id': 'ctl00_MainContent_dgLedgerReport'})[0]
    except Exception as e:
        logger.error('Exception when reading transaction table for captcha_id[%s] - EXCEPT[%s:%s]' % (captcha_text, type(e), e))
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

    captcha_id_id = table.find(id='ctl00_MainContent_lblCaptcha_IdPensionID').text.strip()
    logger.debug('captcha_id_id [%s]' % captcha_id_id)

    if captcha_id_id != captcha_text:
        logger.critical('Something went terribly wrong with [%s != %s]!' % (captcha_id_id, captcha_text))

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
            (credited_date, debited_date, diff_days, debit_timestamp) = (0, transaction_date, 0, pd.to_datetime(transaction_date, dayfirst=True)) #  datetime.strptime(transaction_date, "%d/%m/%Y").timestamp())
        else:
            (credited_date, debited_date, diff_days) = (transaction_date, 0, (debit_timestamp - pd.to_datetime(transaction_date, dayfirst=True)).days) # datetime.strptime(transaction_date, "%d/%m/%Y").timestamp())
        logger.info('credited_date[%s]' % credited_date)
        logger.info('debited_date[%s]' % debited_date)
        logger.info('diff_days[%s]' % diff_days)

        if diff_days < 0:
            diff_days = 0
            continue
        logger.info('After Reset diff_days[%s]' % diff_days)
        
        #csv_buffer.append('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' %(serial_no, mandal_name, bo_name, so_name, captcha_id_id, account_holder_name, credited_date, debited_date, withdrawal_inr, availalbe_balance, diff_time))
        data = data.append({'S.No': serial_no, 'Mandal Name': mandal_name, 'Gram Panchayat': panchayat_name, 'Village': village_name, 'Job card number/worker ID': captcha_id_id, 'Name of the wageseeker': account_holder_name, 'Credited Date': credited_date, 'Deposit (INR)': deposit_inr, 'Debited Date': debited_date, 'Withdrawal (INR)': withdrawal_inr, 'Available Balance (INR)': availalbe_balance, 'Diff. time credit and debit': diff_days}, ignore_index=True)

    data = data.set_index('S.No')
    data = data.iloc[::-1]  # Reverse the order back to normal        
    logger.info('The final table:\n%s' % data)

    return data

def dump_appi_reports(logger, dirname=None):
    #from datetime import datetime

    logger.info('Dump the RN6 HTMLs into [%s]' % dirname)

    if not isGM:
        state = None
        district_name = 'MAHABUBNAGAR'
        block_name = 'Damaragidda'
        # block_id = block_lookup[block_name]
        block_id = '4378'

        block_name = 'Maddur'
        block_code = '3614006'
        block_name = 'Koilkonda'
        block_code = '3614007'
        block_name = 'Hanwada'
        block_code = '3614008'
    else:
        state = 'ap'
        district_name = 'VISAKHAPATNAM'
        block_name = 'Gangaraju Madugula'
        block_id = None

    #dirname = block_name
    if False:
        # filename = 'captcha_ids/Gangaraju Madugula_G.Madugula_030291104271010017-01_ledger_details.html'
        filename = 'captcha_ids/Gangaraju Madugula_Gaduthuru_030291116195010015-04_ledger_details.html'
        #csv_buffer = ['S.No,Mandal Name,Gram Panchayat,Village,Job card number/worker ID,Name of the wageseeker,Credited Date,Deposit (INR),Debited Date,Withdrawal (INR),Available Balance (INR),Diff. time credit and debit\n']
        return 'SUCCESS'

    if block_code:
        panchayats = Panchayat.objects.filter(block__code=block_code)
    else:
        panchayats = Panchayat.objects.filter(block__name=block_name)
    logger.info(panchayats)
    for panchayat in panchayats:
        panchayat_name = panchayat.name
        logger.info('Panchayat[%s]' % panchayat_name)
        if needed and (panchayat_name not in needed):
            logger.info('Not interested in [%s]' % panchayat_name)
            continue
        if skip and (panchayat_name in skip):
            logger.info('To skip [%s]' % panchayat_name)
            continue        
        workers = Worker.objects.filter(captcha_id__panchayat=panchayat)
        logger.info(workers)
        for worker in workers:
            logger.debug('WorkerID[%s]' % worker.id)
            tcaptcha_id = worker.captcha_id.tcaptcha_id
            if tcaptcha_id:
                captcha_text = (tcaptcha_id + '-0' + str(worker.applicantNo))
            else:
                logger.error('tcaptcha_id is NULL for [%s]' % worker)
                continue
            logger.debug('Parse HTML for captcha_text[%s]' % captcha_text)
            
            filename = '%s/%s_%s_%s_ledger_details.html' % (dirname, block_name, panchayat_name, captcha_text)
            village_name = worker.captcha_id.village.name
            try:
                data = parse_appi_report(logger, filename=filename, panchayat_name=panchayat_name, village_name=village_name, captcha_text=captcha_text)
            except Exception as e:
                logger.error('Caught Exception[%s]' % e) 
                csv_filename = filename.replace('.html','.XXX')
                open(csv_filename, 'a').close()
                logger.info('Marking the file [%s]' % csv_filename)
                continue # break 
                
            csv_filename = filename.replace('.html','.csv')
            logger.info('Writing to CSV [%s]' % csv_filename)
            data.to_csv(csv_filename)
            '''
            with open(csv_filename, 'w') as csv_file:
                logger.info('Writing to CSV [%s]' % csv_filename)
                csv_file.write(data.to_csv())
            '''
            # break
        # break
    
    '''

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
        logger.info('Fetch captcha_ids for Panchayat[%s, %s]' % (panchayat_name, panchayat_code))
        url = 'http://b.libtech.info:8000/api/getworkers/?pcode=%s' % panchayat_code
        try:
            logger.info('Requesting URL[%s]' % url)
            response = requests.get(url, timeout=timeout)
        except Exception as e:
            logger.error('Caught Exception[%s]' % e)
        captcha_ids_json = response.json()
        logger.debug('Captcha_Ids JSON[%s]' % captcha_ids_json)
        is_downloaded = True
        for captcha_id_object in captcha_ids_json:
            #logger.info(captcha_id_object)
            captcha_text = '%s-0%s' % (captcha_id_object['captcha_id']['tcaptcha_id'], captcha_id_object['applicantNo'])
            if False and (panchayat_name == 'VITHALAPUR' and is_downloaded and (captcha_id != '142000501002010385-01')): 
                logger.debug('Skipping[%s]' % captcha_id)
                continue            
            is_downloaded = False
            logger.debug('Parse HTML for captcha_text[%s]' % captcha_text)
            
            filename = '%s/%s_%s_%s_ledger_details.html' % (dirname, block_name, panchayat_name, captcha_text)
            # village_name = captcha_id_object['village']['name']
            # logger.debug('Village Name[%s]' % village_name)
            try:
                data = parse_appi_report(logger, filename=filename, panchayat_name=panchayat_name, captcha_text=captcha_text) # Village Name
            except Exception as e:
                logger.error('Exception when reading transaction table for captcha_id - EXCEPT[%s:%s]' % (type(e), e))
                csv_filename = filename.replace('.html','.XXX')
                open(csv_filename, 'a').close()
                logger.info('Marking the file [%s]' % csv_filename)
                continue
                
            csv_filename = filename.replace('.html','.csv')
            with open(csv_filename, 'w') as csv_file:
                logger.info('Writing to CSV [%s]' % csv_filename)
                csv_file.write(data.to_csv())
    '''
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

    def test_fetch_appi_report(self):
        count = 0
        url = base_url + 'ROR.aspx'

        while True:
            count += 1
            self.logger.info('Beginning the download for the nth time, where n=%d' % count)
            result = fetch_appi_reports(self.logger, dirname=directory, url=url)
            if result == 'SUCCESS' or count == 100:
                break
        self.assertEqual(result, 'SUCCESS')

    @unittest.skip('Skipping direct command approach')
    def test_fetch_appi_report_for(self):
        url = base_url + 'ROR.aspx'
        result = fetch_reports_for(self.logger, dirname=directory, url=url, villages=village_list)
        self.assertEqual(result, 'SUCCESS')

    @unittest.skip('Skipping direct command approach')
    def test_dump_appi_report(self):
        result = dump_appi_reports(self.logger, dirname=directory)
        self.assertEqual(result, 'SUCCESS')
        
if __name__ == '__main__':
    unittest.main()
