from bs4 import BeautifulSoup

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch

import unittest
from urllib.request import urlopen   # REVIST
from urllib.parse import urlencode
import httplib2


#######################
# Global Declarations
#######################

httplib2.debuglevel = 1
h = httplib2.Http('.cache')

fto_no='CH3305007_280516FTO_119245' # 'CH3305000285_020816APB_FTO_267494'
fin_year='2016-2017'
state_code='33'

url = "http://164.100.129.6/netnrega/fto/fto_status_dtl.aspx?fto_no=%s&fin_year=%s&state_code=%s" % (fto_no, fin_year, state_code)
filename = 'fto.html'


#############
# Functions
#############

def nic_fetch_fto(logger,):
    response = urlopen(url)
    html_source = response.read()
    logger.debug("HTML Fetched [%s]" % html_source)

    bs = BeautifulSoup(html_source, "html.parser")
    state = bs.find(id='__VIEWSTATE').get('value')
    logger.info('state[%s]' % state)
    validation = bs.find(id='__EVENTVALIDATION').get('value')
    logger.info('value[%s]' % validation)

    data = {
      '__EVENTTARGET':'ctl00$ContentPlaceHolder1$Ddfto',
      '__EVENTARGUMENT':'',
      '__LASTFOCUS':'',
      '__VIEWSTATE': state,
      '__VIEWSTATEENCRYPTED':'',
      '__EVENTVALIDATION': validation,
      'ctl00$ContentPlaceHolder1$Ddfin': fin_year,
      'ctl00$ContentPlaceHolder1$Ddstate': state_code,
      'ctl00$ContentPlaceHolder1$Txtfto': fto_no,
      'ctl00$ContentPlaceHolder1$Ddfto': fto_no,
    }

    
    response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})

    with open(filename, 'wb') as html_file:
      logger.info('Writing [%s]' % filename)
      html_file.write(content)

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
    
  def test_fetch(self):
    result = nic_fetch_fto(self.logger)
    
    self.assertEqual('SUCCESS', result)

  def pull(self):
    bs = BeautifulSoup(self.html, "html.parser")
    self.logger.info(bs.find(id='__VIEWSTATE'))
    self.logger.info(bs.find(id='__EVENTVALIDATION'))

    self.assertEqual(1, 1)


if __name__ == '__main__':
  unittest.main()

