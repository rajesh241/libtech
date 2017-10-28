import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
import unittest
import requests

filename = 'panchregpeople.html' 

# Obtain the Registration Application Register page
def fetch_regapp(logger):
    # Obtain a cookie
    url = 'http://mnregaweb2.nic.in/netnrega/IndexFrame.aspx?lflag=eng&District_Code=2721&district_name=AJMER&state_name=RAJASTHAN&state_Code=27&block_name=%E0%A4%85%E0%A4%B0%E0%A4%BE%E0%A4%88&block_code=2721001&fin_year=2017-2018&check=1&Panchayat_name=%E0%A4%B2%E0%A4%BE%E0%A4%AE%E0%A5%8D%E0%A4%AC%E0%A4%BE&Panchayat_Code=2721001029'
    response = requests.get(url)
    logger.debug(response.text)
    cookies = response.cookies
    logger.info(cookies)

    # Fetch the actual page
    fetch_url = 'http://mnregaweb2.nic.in/netnrega/Citizen_html/Panchregpeople.aspx'
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'mnregaweb2.nic.in',
        'Referer': url,
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0',
    }

    params = (
        ('lflag', 'eng'),
        ('fin_year', '2017-2018'),
        ('Panchayat_Code', '2721001029'),
        ('type', 'a'),
        ('Digest', '3mabBRWDbPmDl1MTHX7gjw'),
    )

    response = requests.get(fetch_url, headers=headers, params=params, cookies=cookies)
    logger.debug(response.content)
    
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.content)

    return 'SUCCESS'

def fetch_panchregpeople(logger):
    hard_url = 'http://mnregaweb2.nic.in/netnrega/IndexFrame.aspx?lflag=eng&District_Code=2721&district_name=AJMER&state_name=RAJASTHAN&state_Code=27&block_name=%E0%A4%85%E0%A4%B0%E0%A4%BE%E0%A4%88&block_code=2721001&fin_year=2017-2018&check=1&Panchayat_name=%E0%A4%B2%E0%A4%BE%E0%A4%AE%E0%A5%8D%E0%A4%AC%E0%A4%BE&Panchayat_Code=2721001029'
    logger.info('Fetch URL[%s]' % hard_url)
    response = requests.get(hard_url)
    logger.info(response.text)
    cookies = response.cookies
    logger.info(cookies)

    if False:
        response = requests.get(url, headers=headers, params=params, cookies=cookies)
        logger.info(response.cookies)
        logger.info(response.text)
        
        url = 'http://mnregaweb2.nic.in/netnrega/writereaddata/citizen_out/panchregpeople_2721001029_eng1718.html'
        cmd = 'curl -L -O %s' % url
        os.system(cmd)
    
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.text.encode('utf-8'))

    return 'SUCCESS'


##########
# Tests
##########

class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = loggerFetch('info')
        self.logger.info('BEGIN PROCESSING')

    def tearDown(self):
        self.logger.info('...END PROCESSING')

    @unittest.skip('Skipping direct command approach')
    def test_direct_cmd(self):
        url = 'http://mnregaweb2.nic.in/netnrega/writereaddata/citizen_out/panchregpeople_2721001029_eng1718.html'
        cmd = 'curl -L -O %s' % url
        os.system(cmd)

    @unittest.skip('Skipping the curl approach')
    def test_fetch_panchregpeople(self):
        result = fetch_panchregpeople(self.logger)
        self.assertEqual('SUCCESS', result)

    def test_fetch_regapp(self):
        result = fetch_regapp(self.logger)
        self.assertEqual('SUCCESS', result)

if __name__ == '__main__':
    unittest.main()

