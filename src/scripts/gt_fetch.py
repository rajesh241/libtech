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
import cv2

import argparse
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

import requests
import time
import unittest
import datetime

from wrappers.logger import logger_fetch
from wrappers.sn import driverInitialize, driverFinalize, displayInitialize, displayFinalize

import psutil
import pandas as pd
import json

# For crawler.py

from slugify import slugify
import csv
import urllib.parse as urlparse


#######################
# Global Declarations
#######################

timeout = 3
directory = '/home/mayank/libtech/src/scripts/AllDistricts'
#directory = '/home/mayank/libtech/src/scripts/Vishakhapatnam'
base_url = 'https://meebhoomi.ap.gov.in/'

village_list = [('విశాఖపట్నం', 'అచ్యుతాపురం', 'జోగన్నపాలెం'), ('విశాఖపట్నం', 'అనంతగిరి', 'నిన్నిమామిడి'), ('విశాఖపట్నం', 'అనందపురం', 'ముచ్చెర్ల')]
skip_district = ['3',]
is_visible = True
is_virtual = True


#############
# Functions
#############




#############
# Classes
#############

class GeorgeTown():
    def __init__(self, is_selenium=None):
        self.fs_url = 'https://nfs.delhi.gov.in/Citizen/Householdtobeincluded.aspx'
        self.status_file = 'status.csv'
        self.dir = 'data'
        try:
            os.makedirs(self.dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        self.is_selenium = False
        if is_selenium:
            self.is_selenium = is_selenium

        if self.is_selenium:
            self.display = displayInitialize(isDisabled = not is_virtual, isVisible = is_visible)
            self.driver = driverInitialize(timeout=3)
            #self.driver = driverInitialize(path='/opt/firefox/', timeout=3)

    def __del__(self):
        if self.is_selenium:
            driverFinalize(self.driver) 
            displayFinalize(self.display)
      
    def wait_for_window(self, timeout = 2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]
        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()
        
    def login(self, logger, auto_captcha=False):
        url = 'https://ysrrythubharosa.ap.gov.in/RBApp/RB/Login'
        logger.info('Fetching URL[%s]' % url)
        self.driver.get(url)
        time.sleep(3)

        user = '9959905843'
        elem = self.driver.find_element_by_xpath('//input[@type="text"]')
        logger.info('Entering User[%s]' % user)
        elem.send_keys(user)

        password = '9959905843'
        elem = self.driver.find_element_by_xpath('//input[@type="password"]')
        logger.info('Entering Password[%s]' % password)
        elem.send_keys(password)
        if auto_captcha:
            retries = 0
            while True and retries < 3:
                logger.info('Waiting for Captcha...')
                #input()
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.ID, "captchdis")))
                time.sleep(3)
                
                captcha_text = '12345'
                fname = 'captcha.png'
                self.driver.save_screenshot(fname)
                img = Image.open(fname)
                # box = (815, 455, 905, 495)   Captcha Box
                if is_mynk:
                    box = (830, 470, 905, 485)   # Mynk Desktop
                    # box = (1170, 940, 1315, 965)   # Mynk Mac
                else:
                    box = (1025, 940, 1170, 965)   # Goli Mac
                
                area = img.crop(box)
                filename = 'cropped_' + fname 
                area.save(filename, 'PNG')
                img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
                img = cv2.resize(img, None, fx=10, fy=10, interpolation=cv2.INTER_LINEAR)
                img = cv2.medianBlur(img, 9)
                th, img = cv2.threshold(img, 185, 255, cv2.THRESH_BINARY)
                filename = 'processed_captcha.png'
                cv2.imwrite(filename, img)
                fname = 'converted_captcha.png'
                check_output(['convert', filename, '-resample', '10', fname])
                captcha_text = pytesseract.image_to_string(Image.open(fname), lang='eng', config='--psm 8  --dpi 300 -c tessedit_char_whitelist=ABCDEF0123456789')
                
                elem = self.driver.find_element_by_xpath('(//input[@type="text"])[2]')
                logger.info('Entering Captcha_Text[%s]' % captcha_text)
                elem.send_keys(captcha_text)
                
                login_button = '(//button[@type="button"])[2]'            
                elem = self.driver.find_element_by_xpath(login_button)
                logger.info('Clicking Login Button')
                elem.click()
                try:
                    WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[@class ='swal2-confirm swal2-styled']"))).click()
                    logger.info(f'Invalid Captcha [{captcha_text}]')
                    retries += 1                
                    WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Refresh'))).click()
                    continue
                except TimeoutException:
                    logger.info(f'Valid Captcha [{captcha_text}]')
                    break
                except Exception as e:
                    logger.error(f'Error guessing [{captcha_text}] - EXCEPT[{type(e)}, {e}]')

            if retries == 3:
                return 'FAILURE'
            else:
                return 'SUCCESS'
        else:
            logger.info('Please ennter the catpcha on the webpage and hit any key...')
            input()

    def print_current_window_handles(self, logger, event_name=None):
        """Debug function to print all the window handles"""
        handles = self.driver.window_handles
        logger.info(f"Printing current window handles after {event_name}")
        for index, handle in enumerate(handles):
            logger.info(f"{index}-{handle}")


    def request_fs_report(self, logger, circle=None, fps=None):
        url = 'https://nfs.delhi.gov.in/Citizen/Householdtobeincluded.aspx'
        logger.info(f'Fetching URL[{url}]')
        response = requests.get(url, verify=False)
        filename=f'{self.dir}/{circle}_{fps}.html'
        with open(filename, 'wb') as html_file:
            logger.info(f'Writing file[{filename}]')
            html_file.write(response.content)

        bs = BeautifulSoup(response.content, 'html.parser')
        view_state = bs.find('input', attrs={'id':'__VIEWSTATE'})['value']
        event_validation = bs.find('input', attrs={'id':'__EVENTVALIDATION'})['value']
        session_id = response.cookies['ASP.NET_SessionId']
        logger.info(f'Cookies[ASP.NET_SessionId:{session_id}] and vs[{view_state}] and ev[{event_validation}]')

        cookies = {
            'ASP.NET_SessionId': session_id,
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://nfs.delhi.gov.in',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://nfs.delhi.gov.in/Citizen/Householdtobeincluded.aspx',
            'Upgrade-Insecure-Requests': '1',
        }

        data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': view_state, 
            '__EVENTVALIDATION': event_validation,
            'ctl00$MainContent$ddlCircle': circle,
            'ctl00$MainContent$ddlFps': fps,
            'ctl00$MainContent$btnview': 'Show'
        }

        response = requests.post(url, headers=headers, cookies=cookies, data=data, verify=False)
        with open(filename, 'wb') as html_file:
            logger.info(f'Writing file[{filename}]')
            html_file.write(response.content)
                
    def crawl_fs_report(self, logger, circle=None, fps=None):
        driver = self.driver
        url = self.fs_url
        logger.info(f'Fetching URL[{url}]')
        driver.get(url)
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_btnview"]')))
            logger.info(f'Fetching Food Security report for Circle[{circle}] and FPS[{fps}]...')
        except TimeoutException:
            logger.error(f'Timed out waiting for drop down for Circle[{circle}] and FPS[{fps}]')
            # return 'FAILURE'
        except Exception as e:
            logger.error(f'Errored Waiting for Food Security report, Circle[{circle}] and FPS[{fps}] - EXCEPT[{type(e)}, {e}]')
            # return 'FAILURE'

        # elem = driver.find_element_by_xpath('//*[@id="MainContent_ddlCircle"]')
        select = Select(driver.find_element_by_id('MainContent_ddlCircle'))
        select.select_by_value(circle)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'#MainContent_ddlFps > option[value="{fps}"]'))
            )
        except TimeoutException:
            logger.error(f'Timed out waiting for drop down for FPS[{fps}]')
            # return 'FAILURE'
        except Exception as e:
            logger.error(f'Errored Waiting for Food Security report, for FPS[{fps}] - EXCEPT[{type(e)}, {e}]')
            # return 'FAILURE'

        select = Select(driver.find_element_by_id('MainContent_ddlFps'))
        select.select_by_value(fps)

        time.sleep(3)

        '''
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f''))  # Ideal would be to check if Circle would be available
            )
        except TimeoutException:
            logger.error(f'Timed out waiting for drop down for FPS[{fps}]')
            # return 'FAILURE'
        except Exception as e:
            logger.error(f'Errored Waiting for Food Security report, for FPS[{fps}] - EXCEPT[{type(e)}, {e}]')
            # return 'FAILURE'
        '''
        
        try:
            show_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_btnview"]')))
            logger.info(f'Fetching Food Security report for Circle[{circle}] and FPS[{fps}]...')
        except TimeoutException:
            logger.error(f'Timed out waiting for drop down for Circle[{circle}] and FPS[{fps}]')
            # return 'FAILURE'
        except Exception as e:
            logger.error(f'Errored Waiting for Food Security report, Circle[{circle}] and FPS[{fps}] - EXCEPT[{type(e)}, {e}]')
            # return 'FAILURE'

        show_button.click()

        html_source = self.driver.page_source
        filename=f'{self.dir}/{circle}_{fps}.html'
        with open(filename, 'w') as html_file:
            logger.info(f'Writing file[{filename}]')
            html_file.write(html_source)

        filename=f'{self.dir}/{circle}_{fps}.csv'
        df = pd.read_html(html_source)[0]
        logger.debug(f'{df}')
        logger.info(f'Writing [{filename}]') 
        df.to_csv(filename, index=False)
        
        return 'SUCCESS'   # Leaving it at this

        villages = df['Village Name']
        
        table_id = 'tblreject'
        logger.info('Waiting for the table ID[{table_id}] to load')
        table = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, table_id))
        )
        specific_index = None
        if village:
            logger.info(f'The village list [{villages}]')
            specific_index = village.find(village)
            logger.info(f'Yippie! We have a hit for {village} {specific_index}')

        for i, elem in enumerate(table.find_elements_by_css_selector('a')):
            value = elem.get_attribute('text')
            if value == '0':
                continue
            index = int(i/2)
            village = villages[index]
            logger.info(f'specific_index[{specific_index}] vs index[{index}]')
            if specific_index:
                logger.info(f'Entered index[{index}]')
                if specific_index != index:
                    logger.info(f'Skipping {village}')
                    continue
                else:
                    logger.info(f'Chose index[{index}]')
            logger.info(f'Clicking for village[{village}] > value[{value}]')
            logger.info("Handles : [%s]    Number : [%d]" % (self.driver.window_handles, len(self.driver.window_handles)))
            #elem.click()
            #time.sleep(3) #FIXME
            elem.click()
            time.sleep(5) #FIXME
            parent_handle = self.driver.current_window_handle
            #logger.info("Handles : %s" % self.driver.window_handles + "Number : %d" % len(self.driver.window_handles))
            logger.info("Handles : [%s]    Number : [%d]" % (self.driver.window_handles, len(self.driver.window_handles)))
            '''
            html_source = self.driver.page_source
            df = pd.read_html(html_source)[0]
            logger.debug(f'{df}')
            filename=f'{self.dir}/{district}_{mandal}_{village}_base.csv'
            logger.info(f'Writing [{filename}]') 
            df.to_csv(filename, index=False)
            '''
            if len(self.driver.window_handles) > 1:
                logger.info('Switching Window...')
                self.driver.switch_to.window(self.driver.window_handles[-1])
                logger.info('Switched!!!')
                html_source = self.driver.page_source
                #time.sleep(2)
            else:
                logger.error(f'Handlers gone wrong [{str(self.driver.window_handles)}]')
                self.driver.save_screenshot('./button_'+captcha_text+'.png')
                return 'FAILURE'
            '''
            try:
                logger.info('Waiting for page to load')
                elem = WebDriverWait(driver, timeout).until(
                    #EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_lbl_village"))
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[3]/div/div[2]/div/div/table/thead/tr/th[4]'))
                )
            except TimeoutException as e:
                logger.error('Timeout waiting for dialog box - EXCEPT[%s:%s]' % (type(e), e))
                self.driver.close()
                self.driver.switch_to.window(parent_handle)
                return 'ABORT'
            except Exception as e:
                logger.error('Exception on WebDriverWait(10) - EXCEPT[%s:%s]' % (type(e), e))
                self.driver.save_screenshot('./button_'+captcha_text+'.png')
                self.driver.close()
                self.driver.switch_to.window(parent_handle)
                return 'ABORT'
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[3]/div/div[2]/div/div/table/thead/tr/th[4]'))
            )
            '''
            df = pd.read_html(html_source)[0]
            logger.debug(f'{df}')
            filename=f'{self.dir}/{district}_{mandal}_{village}.csv'
            logger.info(f'Writing [{filename}]') 
            df.to_csv(filename, index=False)
            logger.info('Closing Current Window')
            self.driver.close()
            logger.info('Switching back to Parent Window')            
            self.driver.switch_to.window(parent_handle)
            if False:
                logger.info('Press any key')
                input()
        
        return 'SUCCESS'
 
def get_unique_district_block(logger, dataframe):
    logger.info(dataframe.columns)
    df = dataframe.groupby(["district_name_telugu",
                            "block_name_telugu"]).size().reset_index(name='counts')
    logger.info(len(df))
    
class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = logger_fetch('info')
        self.logger.info('BEGIN PROCESSING...')

    def tearDown(self):
        self.logger.info('...END PROCESSING')

    def test_crawl_fs_report(self):
        self.logger.info("Running test for Food Security Report")
        # Start a RhythuBharosa Crawl
        gt = GeorgeTown(is_selenium=True)
        gt.crawl_fs_report(self.logger, circle='01020048', fps='100300400015')
        del gt
        
    def test_request_fs_report(self):
        self.logger.info("Running test for Food Security Report")
        # Start a RhythuBharosa Crawl
        gt = GeorgeTown()
        gt.request_fs_report(self.logger, circle='01020048', fps='100300400015')
        gt.request_fs_report(self.logger, circle='01090067', fps='100500500005')
        del gt
        
        
if __name__ == '__main__':
    unittest.main()
