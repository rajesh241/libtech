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
is_mynk = True
is_virtual = True


#############
# Functions
#############




#############
# Classes
#############

class CEOKarnataka():
    def __init__(self, logger=None, is_selenium=None):
        if logger:
            self.logger = logger
        else:
            logger = self.logger = logger_fetch('info')
        logger.info(f'Constructor({type(self).__name__})')
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
        self.logger.info(f'Destructor({type(self).__name__})')

    def pdf2text(self, pdf_file):
        logger = self.logger
        filename = pdf_file.replace('.pdf', '.txt')
        if os.path.exists(filename):
            logger.info(f'File already downloaded. Reading [{filename}]...')
            with open(filename) as txt_file:
                text = txt_file.read()
            return text

        if is_mynk:
            aap_location = '/media/mayank/FOOTAGE1/AAP_BBMP_FILEs'
            basename = os.path.basename(filename).strip('.txt')
            dirname = f'{aap_location}/{basename}'
        else:
            dirname = filename.strip('.txt')
        page_file = os.path.join(dirname, 'page') # f'{dirname}/page'
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            # Revisit
            cmd = f'pdftoppm -png -r 300 -freetype yes {pdf_file} {page_file}'
            logger.info(f'Executing cmd[{cmd}]...')
            os.system(cmd)

        logger.debug(os.listdir(dirname))
        for png_file in os.listdir(dirname):
            if not png_file.endswith('.png'):  # Only needed during debugging
                continue
            img = os.path.join(dirname, png_file) # f'{dirname}/{png_file}'
            if not img.endswith('-01.png'):   # Only for now Mynk #FIXME
                continue
            #if img.endswith('-01.png') or img.endswith('-02.png'):
            if img.endswith('-02.png'):
                continue
            if os.path.exists(img.replace('.png', '.txt')):
                continue
            cmd = f'tesseract {img} {img.strip(".png")} --dpi 300'
            logger.info(f'Executing cmd[{cmd}]...')
            os.system(cmd)

        cmd = f'''cat {page_file}-*.txt | grep -v '^$' | 
            grep -v 'Assembly Constituency' | 
            grep -v 'Section No and Name' | 
            grep -v '^Part number : ' | grep -v '^ ' | 
            grep -v 'Available' | grep -v 'Date of Publication:' > \
            {filename}'''
        cmd = f'''cat {page_file}-*.txt > {filename}'''
        logger.info(f'Executing cmd[{cmd}]...')
        return ''
        '''
        os.system(cmd)

        #exit(0)

        #cmd = f'rm -rfv {dirname}'
        cmd = f'mv -v {dirname} {aap_location}/'
        logger.info(f'Executing cmd[{cmd}]...')
        os.system(cmd)
        cmd = f'ln -s {aap_location}/{dirname} .'
        logger.info(f'Executing cmd[{cmd}]...')
        os.system(cmd)
        '''
        
        logger.info(f'Reading [{filename}]...')
        with open(filename) as txt_file:
            text = txt_file.read()
        return text

    def fetch_draft_roll(self, district, ac_no, part_no, convert=None):
        logger = self.logger
        filename=os.path.join(f'{self.dir}', f'{district}_{ac_no}_{part_no}.pdf')
        if os.path.exists(filename):
            logger.info(f'File already downloaded. Converting [{filename}]...')
            '''
            with open(filename) as html_file:
                html_source = html_file.read()
            '''
        else:
            url = f'http://ceo.karnataka.gov.in/draftroll_2020/English/AC{ac_no}/S10A{ac_no}P{part_no}.pdf'
            cmd = f'curl -L -o {filename} {url}'
            logger.info(f'Executing cmd[{cmd}]...')
            os.system(cmd)
            logger.info(f'Fetched the Draft Roll [{filename}]')

        if convert:
            self.pdf2text(filename)
        
    def fetch_district_list(self):
        logger = self.logger
        return ['32']

    def fetch_draft_rolls(self):
        logger = self.logger
        for district in self.fetch_district_list():
            for ac_no in self.fetch_ac_list(district=district):
                for part_no in self.fetch_part_list(district, ac_no):
                    self.fetch_draft_roll(district, ac_no, part_no, convert=True)

    def fetch_ac_list(self, district=None):
        logger = self.logger        
        filename = os.path.join(self.dir, f'{district}.html')
        url = self.url + f'AC_List_B3.aspx?DistNo={district}'
        type = 'AC NO'
        return self.fetch_lookup(url, filename, type)
            
    def fetch_part_list(self, district=None, ac_no=None):
        logger = self.logger        
        filename = os.path.join(f'{self.dir}', f'{district}_{ac_no}.html')
        url = self.url + f'Part_List_2019.aspx?ACNO={ac_no}'
        type = 'Part NO'
        return self.fetch_lookup(url, filename, type)

    def fetch_lookup(self, url, filename, type):
        logger = self.logger
        if os.path.exists(filename):
            logger.info(f'File already downloaded. Reading [{filename}]...')
            with open(filename) as html_file:
                html_source = html_file.read()
        else:
            logger.info(f'Fetching URL[{url}]')
            response = requests.get(url)
            html_source = response.content
            with open(filename, 'wb') as html_file:
                logger.info(f'Writing file[{filename}]')
                html_file.write(html_source)

        df = pd.read_html(html_source)[1]
        logger.debug(f'{df}')
        filename = filename.replace('.html', '.csv')
        logger.info(f'Writing [{filename}]') 
        df.to_csv(filename, index=False)

        return df[type].to_list()


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = logger_fetch('info')
        self.logger.info('BEGIN PROCESSING...')

    def tearDown(self):
        self.logger.info('...END PROCESSING')

    def test_fetch_draft_rolls(self):
        self.logger.info("TestCase: E2E - fetch_draft_rolls()")
        # Fetch Draft Rolls from http://ceo.karnataka.gov.in/
        ck = CEOKarnataka(logger=self.logger)
        ck.fetch_draft_rolls()
        del ck
        
    def test_fetch_draft_roll(self):
        self.logger.info("TestCase: UnitTest - fetch_draft_roll(district, ac_no, part_no)")
        # Fetch Draft Rolls from http://ceo.karnataka.gov.in/
        ck = CEOKarnataka(logger=self.logger)
        ck.fetch_draft_roll(district='32', ac_no='151', part_no='115', convert=True)
        #ck.fetch_draft_roll(self.logger, district='31', ac_no='154', part_no='7')
        del ck
        
if __name__ == '__main__':
    unittest.main()
