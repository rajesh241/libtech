import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
import unittest
import requests
import time

timeout=10
dirname = './dealers/'
filename = dirname + 'z.html'
district_name = 'LATEHAR'
# block_name = 'MAHUADANR'
block_name = 'MANIKA'
district_name = 'KHUNTI'
block_name = 'KHUNTI'
district_name = 'RANCHI'
block_name = 'NAGRI'
dealer_list_file = 'dealer_list.html'
district_lookup = {}
block_lookup = {}
year_code = 0

district_name = 'LATEHAR'
block_name = 'MANIKA'

dealer_lookup = {}

# Get the Dealer List
def fetch_via_cmd(logger):
    cmd = '''curl 'http://nregasp2.nic.in/Netnrega/writereaddata/state_out/unfulfilled_demand3405006_eng_1718.html' -H 'Host: nregasp2.nic.in' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Cookie: ASP.NET_SessionId=qbo33v45rlpbnvvil0idfarm' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -o z.html'''

    os.system(cmd)
    logger.info('Executing [%s]' % cmd)

    return 'SUCCESS'


def fetch_unfulfilled(logger, cookies=None):
    logger.info('Fetch list')

    if not cookies:
        url='https://www.google.com/url?q=http://nregasp2.nic.in/netnrega/Progofficer/PoIndexFrame.aspx?flag_debited%3DD%26lflag%3Deng%26District_Code%3D3405%26district_name%3DPALAMU%26state_name%3DJHARKHAND%26state_Code%3D2017-2018%26finyear%3D34%26check%3D1%26block_name%3DManatu%26Block_Code%3D3405006&sa=D&source=hangouts&ust=1543325325793000&usg=AFQjCNGz7BQdBf7P9oTuYCLhct2R3GJ2zQ'
        response = requests.post(url, timeout=timeout, verify=False)
        cookies = response.cookies
    else:
        cookies = {
            'ASP.NET_SessionId': 'qbo33v45rlpbnvvil0idfarm',
        }

    headers = {
        'Host': 'nregasp2.nic.in',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    
    response = requests.get('http://nregasp2.nic.in/Netnrega/writereaddata/state_out/unfulfilled_demand3405006_eng_1718.html', headers=headers, cookies=cookies)

        
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.content)
    
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
    def test_directly(self):
        result = fetch_dea_cmd(self.logger)
        self.assertEqual('SUCCESS', result)

    def test_direct_cmd(self):
        result = fetch_via_cmd(self.logger)
        self.assertEqual('SUCCESS', result)

    def test_fetch_unfulfilled(self):
        result = fetch_unfulfilled(self.logger)
        self.assertEqual('SUCCESS', result)

if __name__ == '__main__':
    unittest.main()

