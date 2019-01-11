import pandas as pd
import psutil
from wrappers.sn import driverInitialize, driverFinalize, displayInitialize, displayFinalize
from wrappers.logger import loggerFetch
import unittest
import time
import requests
import sys
from bs4 import BeautifulSoup

import os
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(CUR_DIR)
REPO_DIR = os.path.dirname(ROOT_DIR)

sys.path.insert(0, ROOT_DIR)


#######################
# Global Declarations
#######################

directory = ''


#############
# Functions
#############

def fetch_muster_rolls(logger, dirname=None, state=None, district=None, block=None, panchayat=None):

    url = 'http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=NewReportsRH&actionVal=R1Display&page=Newreportcenter_ajax_eng#'

    logger.info('Fetching URL[%s] for cookies' % url)
    with requests.Session() as session:
        response = session.get(url)

        cookies = session.cookies

        if not cookies:
            cookies = {
                'JSESSIONID': '8203300153E164F2995719BEF0F3D040.mgnregsapps1',
                '_ga': 'GA1.3.1634808397.1540151653',
                'S_MODE': '2',
            }

        headers = {
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=NewReportsRH&actionVal=R1Display&page=Newreportcenter_ajax_eng',
            'Connection': 'keep-alive',
        }

        params = (
            ('requestType', 'NewReportsRH'),
            ('actionVal', 'AjaxDisplay'),
            ('State', '-1'),
            ('District', '03'),
            ('Mandal', '11'),
            ('GP', '03'),
            ('vill', '-1'),
            ('Financial', '2018'),
            ('Month', '01'),
            ('id', 'Village'),
            ('page', 'Newreportcenter_ajax_eng'),
        )
        response = session.get('http://www.nrega.ap.gov.in/Nregs/FrontServlet',
                               headers=headers, params=params, cookies=cookies)
        # NB. Original query string below. It seems impossible to parse and
        # reproduce query strings 100% accurately so the one below is given
        # in case the reproduced version is not "correct".
        # response = requests.get('http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=NewReportsRH&actionVal=AjaxDisplay&State=-1&District=03&Mandal=11&GP=03&vill=014&Financial=2018&Month=01&id=Village&page=Newreportcenter_ajax_eng', headers=headers, cookies=cookies)

        url = 'http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=Common_engRH&actionVal=musterinfo&page=MusterRolls_eng'

        '''
        cookies = {
            'JSESSIONID': '05B0EE7BA69097C6F2E8D0E1235E65D3.mgnregsapps1',
        }
        '''

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=Common_engRH&actionVal=musterinfo&page=MusterRolls_eng',
            'Content-Type': 'application/x-www-form-urlencoded',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        params = (
            ('requestType', 'Common_engRH'),
            ('actionVal', 'musterinfo'),
            ('page', 'MusterRolls_eng'),
        )

        data = {
            'State': '-1',
            'District': '03',
            'Mandal': '11',
            'Panchayat': '03',
            'FromDate': '01/12/2018',
            'ToDate': '31/12/2018',
            'Go': '',
            'spl': 'Select',
            'input2': '',
            'userCaptcha': ''
        }

        logger.info('Fetching URL[%s] for cookies' % url)
        response = session.post('http://www.nrega.ap.gov.in/Nregs/FrontServlet',
                                headers=headers, params=params, cookies=cookies, data=data)

        # NB. Original query string below. It seems impossible to parse and
        # reproduce query strings 100% accurately so the one below is given
        # in case the reproduced version is not "correct".
        # response = requests.post('http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=Common_engRH&actionVal=musterinfo&page=MusterRolls_eng', headers=headers, cookies=cookies, data=data)

        '''
        districtkey =  '03'
        mandalkey = '11'
        panchayatkey = '03'
        frmDatekey = '01/12/2018'
        toDatekey = '31/12/2018'
        # url = 'http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=PaymentsWork_engRH&actionVal=musterrolls&page=SocialAuditPrint_eng&District="+districtkey+"&Mandal="+mandalkey+"&Panchayat="+panchayatkey+"&FromDate="+frmDatekey+"&ToDate="+toDatekey+"&exec="+exec;'
        url = "http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=PaymentsWork_engRH&actionVal=musterrolls&page=SocialAuditPrint_eng&District="+districtkey+"&Mandal="+mandalkey+"&Panchayat="+panchayatkey+"&FromDate="+frmDatekey+"&ToDate="+toDatekey+"&exec=muster"

        '''

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'http://www.nrega.ap.gov.in/Nregs/FrontServlet?requestType=Common_engRH&actionVal=musterinfo&page=MusterRolls_eng',
            'Content-Type': 'application/x-www-form-urlencoded',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        params = (
            ('requestType', 'PaymentsWork_engRH'),
            ('actionVal', 'musterrolls'),
            ('page', 'SocialAuditPrint_eng'),
            ('District', '03'),
            ('Mandal', '11'),
            ('Panchayat', '03'),
            ('FromDate', '20/12/2018'),
            ('ToDate', '06/01/2019'),
            ('exec', 'muster'),
        )

        data = {
            'State': '-1',
            'District': '03',
            'Mandal': '11',
            'Panchayat': '03',
            'FromDate': '20/12/2018',
            'ToDate': '06/01/2019',
            'Go': '',
            'spl': 'Select',
            'input2': '',
            'userCaptcha': ''
        }

        logger.info('Cookies[%s]' % session.cookies)

        logger.info('Dowloading the muster from the URL[%s]' % url)
        response = session.post('http://www.nrega.ap.gov.in/Nregs/FrontServlet',
                                headers=headers, params=params, cookies=cookies, data=data)

        filename = '/tmp/z.xlsx'
        with open(filename, 'wb') as html_file:
            logger.info('Writing [%s]' % filename)
            html_file.write(response.content)

    return 'SUCCESS'


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = loggerFetch('info')
        self.logger.info('BEGIN PROCESSING...')

    def tearDown(self):
        self.logger.info('...END PROCESSING')

    def test_fetch_muster_rolls(self):
        result = fetch_muster_rolls(self.logger, dirname=directory)
        self.assertEqual(result, 'SUCCESS')


if __name__ == '__main__':
    unittest.main()
