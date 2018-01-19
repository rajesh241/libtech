import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from bs4 import BeautifulSoup

from wrappers.logger import loggerFetch
import unittest
import requests

district_name = 'LATEHAR'
block_name = 'MANIKA'
dealer_list_file = 'dealer_list.html'
filename = 'z.html'
district_lookup = {}
block_lookup = {}
year_code = 0

# Get the Dealer List
def fetch_dealer_cmd(logger):
    cmd= '''curl -L -o dealer_list.html 'http://aahar.jharkhand.gov.in/dealer_monthly_reports' -H 'Host: aahar.jharkhand.gov.in' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:45.0) Gecko/20100101 Firefox/45.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-GB,en;q=0.5' --compressed -H 'Referer: http://aahar.jharkhand.gov.in/block_city_monthly_reports' -H 'Cookie: CAKEPHP=2lsnclgccoaspcud6u46ector6; _ga=GA1.3.727748505.1512904756; _gid=GA1.3.1119544342.1513048166' -H 'Connection: keep-alive' --data '_method=POST&data%5BDealerMonthlyReport%5D%5Bide%5D=151%2C01%2C5%2C14' '''

    os.system(cmd)
    logger.info('Executing [%s]' % cmd)

    return 'SUCCESS'


# Fetch the list of all the districts for the given month and year
def fetch_district_list(logger, month='01', year='2018'):
    url="http://aahar.jharkhand.gov.in/district_monthly_reports/"
    response = requests.post(url)
    cookies = response.cookies

    headers = {
        'Host': 'aahar.jharkhand.gov.in',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Referer': 'http://aahar.jharkhand.gov.in/district_monthly_reports/',
        'Connection': 'keep-alive',
    }

    parameters = '%s-%s' % (month, year)
    data = [
        ('_method', 'POST'),
        ('data[DistrictMonthlyReport][mnthyer]', parameters),
    ]

    response =  requests.post('http://aahar.jharkhand.gov.in/district_monthly_reports', headers=headers, cookies=cookies, data=data)

    return response.content


# Fetch the dealer list of all the blocks given the district
def fetch_block_list(logger, district_code='14', month='01', year_code='5'):
    url="http://aahar.jharkhand.gov.in/district_monthly_reports/"
    response = requests.post(url)
    cookies = response.cookies

    headers = {
        'Host': 'aahar.jharkhand.gov.in',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Referer': 'http://aahar.jharkhand.gov.in/district_monthly_reports',
        'Connection': 'keep-alive',
    }

    parameters = district_code + ',' + month + ',' + year_code
    logger.info('Parameters for block list [%s]' % parameters)
    data = [
        ('_method', 'POST'),
        ('data[BlockCityMonthlyReport][ide]', parameters),
    ]

    response = requests.post('http://aahar.jharkhand.gov.in/block_city_monthly_reports', headers=headers, cookies=cookies, data=data)

    return response.content



# Fetch the dealer list where you can find all the dealer codes for the given block
def fetch_dealer_list(logger, district_name = '', block_name = '', month='01', year=''):
    url="http://aahar.jharkhand.gov.in/district_monthly_reports/"
    response = requests.post(url)
    cookies = response.cookies

    headers = {
        'Host': 'aahar.jharkhand.gov.in',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Referer': 'http://aahar.jharkhand.gov.in/block_city_monthly_reports',
        'Connection': 'keep-alive',
    }

    # parameters = '151,01,5,14'
    block_code = '151'
    year_code = '5'
    district_code = '14' # get_district_code(district_name)
    parameters = block_code = block_code + ',' + month + ',' + year_code + ',' + district_code
    logger.info('Using Parameters[%s]' % parameters)
    data = [
        ('_method', 'POST'),
        ('data[DealerMonthlyReport][ide]', parameters),
    ]

    return requests.post('http://aahar.jharkhand.gov.in/dealer_monthly_reports', headers=headers, cookies=cookies, data=data).content


# Fetch the details of the dealer given the dealer code
def fetch_dealer_detail(logger, dealer_code):
    url="http://aahar.jharkhand.gov.in/district_monthly_reports/"
    response = requests.post(url)
    cookies = response.cookies

    headers = {
        'Host': 'aahar.jharkhand.gov.in',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://aahar.jharkhand.gov.in/dealer_monthly_reports',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = [
        ('_method', 'POST'),
        #('data[DealerMonthlyReport][ide]', '4f265f6d-9d04-4dbe-99c5-0bf4c0a80102,01,5'),
        ('data[DealerMonthlyReport][ide]', dealer_code),
    ]

    logger.info('Data [%s]' % data)
    response = requests.post('http://aahar.jharkhand.gov.in/transactions/transaction', headers=headers, data=data,cookies=cookies)

    bs = BeautifulSoup(response.content, 'html.parser')
    
    shop_name = bs.find('b').text.strip().replace(' ', '_')
    logger.debug(shop_name)
    
    # filename = './dealers/' + dealer_code[0:36] + '.html'
    # Remove dealer code from below - Sakina
    filename = './dealers/' + district_name + '_' + block_name + '_' + shop_name + '_' + dealer_code[0:36] + '.html'
    logger.info(filename)

    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.content)

    return 'SUCCESS'


def populate_district_lookup(logger):
    logger.info('Fetching district_list...')
    district_list_html = fetch_district_list(logger, month = '01', year = '2018')
    filename = 'district_lists.html'
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(district_list_html)

    bs = BeautifulSoup(district_list_html, 'html.parser')
    click_list = bs.findAll('a')
    logger.debug(str(click_list))

    for anchor in click_list:
        a = str(anchor)
        pos = a.find('onclick="javascript:send(')
        logger.debug(pos)
        if pos > 0:
            beg = a.find("('") + 2

    for anchor in click_list:
        a = str(anchor)
        pos = a.find('onclick="javascript:send(')
        logger.debug(pos)
        if pos > 0:
            beg = a.find("('") + 2
            end = a.find("')") 
            dealer_code = a[beg:end]  # 28:71
            logger.info('Fetching the dealer[%s]...' % dealer_code)
            fetch_dealer_detail(logger, dealer_code)

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
        result = fetch_dealer_cmd(logger)
        self.assertEqual('SUCCESS', result)

    def test_fetch_pds_transactions(self):
        result = fetch_pds(self.logger)
        self.assertEqual('SUCCESS', result)

if __name__ == '__main__':
    unittest.main()

