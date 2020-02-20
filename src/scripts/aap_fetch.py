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
is_virtual = True


#############
# Functions
#############




#############
# Classes
#############

class CEOKarnataka():
    def __init__(self, is_selenium=None):
        self.url = 'http://ceo.karnataka.gov.in/draftroll_2020/'
        self.status_file = 'status.csv'
        self.dir = 'Karnataka'
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

    def fetch_district_list(self, logger):
        return ['31', '32', '33', '34']

    def fetch_draft_rolls(self, logger):
        for district in self.fetch_district_list(logger):
            for ac_no in self.fetch_ac_list(logger, district=district):
                for part_no in self.fetch_part_list(logger, district, ac_no):
                    filename=f'{self.dir}/{district}_{ac_no}_{part_no}.pdf'
                    url = f'http://ceo.karnataka.gov.in/draftroll_2020/English/AC{ac_no}/S10A{ac_no}P{part_no}.pdf'
                    cmd = f'curl -L -o {filename} {url}'
                    logger.info(f'Executing cmd[{cmd}]...')
                    os.system(cmd)
                    logger.info(f'Fetched the Draft Roll [{filename}]')

    def fetch_ac_list(self, logger, district=None):
        # http://ceo.karnataka.gov.in/draftroll_2020/AC_List_B3.aspx?DistNo=31
        url = self.url + f'AC_List_B3.aspx?DistNo={district}'
        logger.info(f'Fetching URL[{url}]')
        response = requests.get(url)
        html_source = response.content
        filename=f'{self.dir}/{district}.html'
        with open(filename, 'wb') as html_file:
            logger.info(f'Writing file[{filename}]')
            html_file.write(html_source)

        df = pd.read_html(html_source)[1]
        logger.debug(f'{df}')
        filename = filename.replace('.html', '.csv')
        logger.info(f'Writing [{filename}]') 
        df.to_csv(filename, index=False)

        return df['AC NO'].to_list()
            
    def fetch_part_list(self, logger, district=None, ac_no=None):
        # http://ceo.karnataka.gov.in/draftroll_2020/Part_List_2019.aspx?ACNO=154
        url = self.url + f'Part_List_2019.aspx?ACNO={ac_no}'
        logger.info(f'Fetching URL[{url}]')
        response = requests.get(url)
        html_source = response.content
        filename=f'{self.dir}/{district}_{ac_no}.html'
        with open(filename, 'wb') as html_file:
            logger.info(f'Writing file[{filename}]')
            html_file.write(html_source)

        df = pd.read_html(html_source)[1]
        logger.debug(f'{df}')
        filename = filename.replace('.html', '.csv')
        logger.info(f'Writing [{filename}]') 
        df.to_csv(filename, index=False)

        return df['Part NO'].to_list()
            
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

    def test_fetch_draft_rolls(self):
        self.logger.info("Running test for Food Security Report")
        # Fetch Draft Rolls from http://ceo.karnataka.gov.in/
        ck = CEOKarnataka()
        ck.fetch_draft_rolls(self.logger)
        del ck
        
    def test_crawl_draft_rolls(self):
        self.logger.info("Running test for Food Security Report")
        # Fetch Draft Rolls from http://ceo.karnataka.gov.in/
        ck = CEOKarnataka(is_selenium=True)
        ck.crawl_fs_report(self.logger, circle='01020048', fps='100300400015')
        del ck
        
        
if __name__ == '__main__':
    unittest.main()
