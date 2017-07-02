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


#############
# Functions
#############

def requests_fetch(logger,):
    url = 'http://mnregaweb2.nic.in/netnrega/citizen_html/musternew.aspx'

    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36 Vivaldi/1.91.867.42',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }

    params = (
        ('state_name', 'RAJASTHAN'),
        ('district_name', 'CHITTORGARH'),
        ('block_name', 'बेगूँ'),
        ('panchayat_name', 'अन‍ोपपुरा'),
        ('workcode', '2729003055/IF/112908246951'),
        ('panchayat_code', '2729003055'),
        ('msrno', '7369'),
        ('finyear', '2017-2018'),
        ('dtfrm', '10/06/2017'),
        ('dtto', '24/06/2017'),
        ('wn', 'अपना+खेत+अपना+काम+लाडू+लाल+/गणेश+लाल+हजुरी'),
        ('id', '1'),
    )

    response = requests.get(url, headers=headers, params=params)
    cookies = response.cookies
    logger.info(cookies)
        
    response = requests.get(url, headers=headers, params=params, cookies=cookies)
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

