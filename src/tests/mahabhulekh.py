import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch

import unittest
import requests


#######################
# Global Declarations
#######################

filename = 'requests.html'
filename = '1.json'


#############
# Functions
#############

def requests_fetch(logger,):
    gat = 1
    url = 'https://mahabhulekh.maharashtra.gov.in/Konkan/Home.aspx/getSnos'
    '''
    url = 'https://mahabhulekh.maharashtra.gov.in/Konkan/pg712.aspx'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'mahabhulekh.maharashtra.gov.in',
        'Referer': 'https://mahabhulekh.maharashtra.gov.in/Konkan/Home.aspx',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0',
    }

    # response = requests.get('https://mahabhulekh.maharashtra.gov.in/Konkan/pg712.aspx', headers=headers, cookies=cookies)

    '''
    headers = {
        'Host': 'mahabhulekh.maharashtra.gov.in',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json;charset=utf-8',
        'Referer': 'https://mahabhulekh.maharashtra.gov.in/Konkan/Home.aspx',
        'Content-Length': '62',
        'Connection': 'keep-alive',
    }

    params = (
        ('ptxt', '%s' % gat),
        ('vid', '273200030399810000'),
        ('did', '32'),
        ('tid', '3')
    )

    # requests.post(url, headers=headers, cookies=cookies)

    response = requests.get('https://mahabhulekh.maharashtra.gov.in')
    
    cookies = response.cookies
    logger.info(cookies)
        
    response = requests.post(url, headers=headers, params=params, cookies=cookies)
    logger.info(response.cookies)
    
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.text.encode('utf-8'))

    return 'SUCCESS'


#############
# Tests
#############


class TestSuite(unittest.TestCase):
  def setUp(self):
    self.logger = loggerFetch('info')
    self.logger.info('BEGIN PROCESSING...')

  def tearDown(self):
    self.logger.info("...END PROCESSING")
    
  def test_requests_fetch(self):
    result = requests_fetch(self.logger)    
    self.assertEqual('SUCCESS', result)

if __name__ == '__main__':
  unittest.main()

