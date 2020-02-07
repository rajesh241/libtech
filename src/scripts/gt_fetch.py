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
is_mynk = True


#############
# Functions
#############




#############
# Classes
#############

class GeorgeTown():
    def __init__(self):
        self.fs_url = 'https://nfs.delhi.gov.in/Citizen/Householdtobeincluded.aspx'
        self.status_file = 'status.csv'
        self.dir = 'data/'
        try:
            os.makedirs(self.dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise    
        
        self.display = displayInitialize(isDisabled = True, isVisible = is_visible)
        self.driver = driverInitialize(timeout=3)
        #self.driver = driverInitialize(path='/opt/firefox/', timeout=3)

    def __del__(self):
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
        cookies = {
            'ASP.NET_SessionId': 'xjw2ze5bneieggjx3010atic',
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
          '__VIEWSTATE': '/wEPDwUKLTE5NTA4OTE2OA9kFgJmD2QWAgIDD2QWBAITDw8WAh4HVmlzaWJsZWhkZAIVD2QWBgIJDxAPFgYeDkRhdGFWYWx1ZUZpZWxkBQhDaXJjbGVObx4NRGF0YVRleHRGaWVsZAUKQ2lyY2xlTmFtZR4LXyFEYXRhQm91bmRnZBAVRwwtLS1TZWxlY3QtLS0RQURBUlNIIE5BR0FSIFswNF0TQU1CRURLQVIgTkFHQVIgWzQ4XQ1CQUJBUlBVUiBbNjddDUJBREFSUFVSIFs1M10KQkFETEkgWzA1XQ9CQUxMSU1BUkFOIFsyMl0LQkFXQU5BIFswN10NQklKV0FTQU4gWzM2XQtCVVJBUkkgWzAyXRJDSEFORE5JIENIT1dLIFsyMF0QQ0hIQVRUQVJQVVIgWzQ2XRBERUxISSBDQU5UVCBbMzhdCkRFT0xJIFs0N10LRFdBUktBIFszM10RR0FOREhJIE5BR0FSIFs2MV0LR0hPTkRBIFs2Nl0NR09LQUxQVVIgWzY4XRRHUkVBVEVSIEtBSUxBU0ggWzUwXQ9IQVJJIE5BR0FSIFsyOF0OSkFOQUtQVVJJIFszMF0NSkFOR1BVUkEgWzQxXQxLQUxLQUpJIFs1MV0SS0FSQVdBTCBOQUdBUiBbNzBdD0tBUk9MIEJBR0ggWzIzXRNLQVNUVVJCQSBOQUdBUiBbNDJdC0tJUkFSSSBbMDldC0tPTkRMSSBbNTZdEktSSVNITkEgTkFHQVIgWzYwXRBMQVhNSSBOQUdBUiBbNThdDE1BRElQVVIgWzI2XRJNQUxWSVlBIE5BR0FSIFs0M10PTUFOR09MUFVSSSBbMTJdDE1BVElBTEEgWzM0XRBNQVRJQSBNQUhBTCBbMjFdDU1FSFJBVUxJIFs0NV0PTU9ERUwgVE9XTiBbMThdD01PVEkgTkFHQVIgWzI1XQtNVU5ES0EgWzA4XQ9NVVNUQUZBQkFEIFs2OV0OTkFKQUZHQVJIIFszNV0QTkFOR0xPSSBKQVQgWzExXQtOQVJFTEEgWzAxXQ5ORVcgREVMSEkgWzQwXQpPS0hMQSBbNTRdClBBTEFNIFszN10QUEFURUwgTkFHQVIgWzI0XQ9QQVRQQVJHQU5KIFs1N10TUkFKRU5ERVIgTkFHQVIgWzM5XRJSQUpPUkkgR0FSREFOIFsyN10MUklU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',
          '__EVENTVALIDATION': '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',
          'ctl00$MainContent$ddlCircle': circle,
          'ctl00$MainContent$ddlFps': fps,
          'ctl00$MainContent$btnview': 'Show'
        }
        
        response = requests.post('https://nfs.delhi.gov.in/Citizen/Householdtobeincluded.aspx', headers=headers, cookies=cookies, data=data, verify=False)
        filename=f'{self.dir}/{circle}_{fps}.csv'
        with open(filename, 'wb') as html_file:
            logger.info(f'Writing file[{filename}]')
            html_file.write(response.content)
                
    def crawl_fs_report(self, logger, circle=None, fps=None):
        driver = self.driver
        url = self.fs_url
        logger.info(f'Fetching URL[{url}]')
        driver.get(url)
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_ddlCircle"]')))
            logger.info(f'Fetching Food Security report for Circle[{circle}] and FPS[{fps}]...')
        except TimeoutException:
            logger.error(f'Timed out waiting for drop down for Circle[{circle}] and FPS[{fps}]')
            #break
            #return 'FAILURE'
        except Exception as e:
            logger.error(f'Errored Waiting for Food Security report, Circle[{circle}] and FPS[{fps}] - EXCEPT[{type(e)}, {e}]')
            #break
            #return 'FAILURE'

        filename=f'{self.dir}/{circle}_{fps}.csv'
        html_source = self.driver.page_source
        df = pd.read_html(html_source)[0]
        logger.debug(f'{df}')
        logger.info(f'Writing [{filename}]') 
        df.to_csv(filename, index=False)

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
        gt = GeorgeTown()
        gt.crawl_fs_report(self.logger, circle='01020048', fps='100300400015')
        del gt
        
    def test_request_fs_report(self):
        self.logger.info("Running test for Food Security Report")
        # Start a RhythuBharosa Crawl
        gt = GeorgeTown()
        #gt.request_fs_report(self.logger, circle='01020048', fps='100300400015')
        gt.request_fs_report(self.logger, circle='01090067', fps='100500500005')
        del gt
        
        
if __name__ == '__main__':
    unittest.main()
