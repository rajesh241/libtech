import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
import unittest
import requests

filename = 'requests.html' 


def fetch_panchayat(logger):
    url = 'http://mnregaweb2.nic.in/netnrega/Citizen_html/Panchregpeople.aspx'
    

    cookies = {
        'ASP.NET_SessionId': 'xpa43k45pjlzun45k4kdm245',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'mnregaweb2.nic.in',
        'Referer': 'http://mnregaweb2.nic.in/netnrega/IndexFrame.aspx?lflag=eng&District_Code=2721&district_name=AJMER&state_name=RAJASTHAN&state_Code=27&block_name=%E0%A4%85%E0%A4%B0%E0%A4%BE%E0%A4%88&block_code=2721001&fin_year=2017-2018&check=1&Panchayat_name=%E0%A4%B2%E0%A4%BE%E0%A4%AE%E0%A5%8D%E0%A4%AC%E0%A4%BE&Panchayat_Code=2721001029',
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

    logger.info(cookies)
    response = requests.get(url, headers=headers, params=params, cookies=cookies)
    #response = requests.get(url, headers=headers, params=params)
    logger.info(response)
    cookies = response.cookies
    logger.info(cookies)

    if False:
        response = requests.get(url, headers=headers, params=params, cookies=cookies)
        logger.info(response.cookies)
    
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

    def tst_direct_cmd(self):
        url = 'http://mnregaweb2.nic.in/netnrega/writereaddata/citizen_out/panchregpeople_2721001029_eng1718.html'
        cmd = 'curl -L -O %s' % url
        os.system(cmd)

    def test_fetch_panchayat(self):
        url = 'http://www.google.com/url?q=http%3A%2F%2Fmnregaweb2.nic.in%2Fnetnrega%2FIndexFrame.aspx%3Flflag%3Deng%26District_Code%3D2721%26district_name%3DAJMER%26state_name%3DRAJASTHAN%26state_Code%3D27%26block_name%3D%25E0%25A4%2585%25E0%25A4%25B0%25E0%25A4%25BE%25E0%25A4%2588%26block_code%3D2721001%26fin_year%3D2017-2018%26check%3D1%26Panchayat_name%3D%25E0%25A4%25B2%25E0%25A4%25BE%25E0%25A4%25AE%25E0%25A5%258D%25E0%25A4%25AC%25E0%25A4%25BE%26Panchayat_Code%3D2721001029&sa=D&sntz=1&usg=AFQjCNEUunLt0tnX3QGSZez-Cjs084xigg'
        result = fetch_panchayat(self.logger)
        self.assertEqual('SUCCESS', result)

if __name__ == '__main__':
    unittest.main()

