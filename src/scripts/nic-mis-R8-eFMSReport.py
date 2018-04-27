import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)
 
from os import errno
from bs4 import BeautifulSoup

from wrappers.logger import loggerFetch

import unittest
import requests


#######################
# Global Declarations
#######################

dirname = './reports/'

csv_buffer=['Wagelist No,Job card no,Applicant no,Applicant Name,Work Code,Work Name,MSR no,Reference No,Status,Rejection Reason,Proccess Date,Wage list FTO No.,Serial No.']


#############
# Functions
#############

def fetch_fto_status_report(logger, cookies=None): # Cookie? FIXME
    import requests

    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/65.0.3325.181 Chrome/65.0.3325.181 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'http://nregasp2.nic.in/netnrega/FTO/ResponseDetailStatusReport.aspx?lflag=eng&flg=W&page=b&state_name=JHARKHAND&state_code=34&district_name=LATEHAR&district_code=3406&block_name=Manika&block_code=3406004&panchayat_name=Badkadih&panchayat_code=3406004009&fin_year=2017-2018&typ=R&mode=B&source=&Digest=svGST7WUb4z13TVhomEJOg',
        'Connection': 'keep-alive',
    }
    
    params = (
        ('panchayat_code', '3406004009'),
        ('panchayat_name', 'Badkadihblock_code=3406004'),
        ('block_name', 'Manika'),
        ('flg', 'W'),
        ('state_code', '34'),
        ('ref_no', '3406004000NRG18010220180328089'),
        ('fin_year', '2017-2018'),
        ('source', ''),
    )
    
    response = requests.get('http://nregasp2.nic.in/netnrega/FTO/Rejected_ref_no_detail.aspx', headers=headers, params=params)

    filename = dirname + 'report.html'
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.content)

    
    

def fetch_efms_report(logger, state_name=None, district_name=None, block_name=None, panchayat_name=None, fin_year=None):
    logger.info('Fetch the Rejected Payments Report')
    if not state_name:
        state_name = 'JHARKHAND'
    if not district_name:
        district_name = 'LATEHAR'
    if not block_name:
        block_name = 'Manika'
    if not panchayat_name:
        panchayat_name = 'Badkadih'
    if not fin_year:
        fin_year = '2017-2018'

    state_code = '34'
    district_code = '3406'
    block_code = '3406004'
    panchayat_code = '3406004009'

    logger.info('Fetching report for State[%s] District[%s] Block[%s] Panachayat[%s] Financial Year[%s]' % (state_name, district_name, block_name, panchayat_name, fin_year))

    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise        

    #Reference url = 'http://nregasp2.nic.in/netnrega/FTO/ResponseDetailStatusReport.aspx?lflag=eng&flg=W&page=b&state_name=JHARKHAND&state_code=34&district_name=LATEHAR&district_code=3406&block_name=Manika&block_code=3406004&panchayat_name=Badkadih&panchayat_code=3406004009&fin_year=2017-2018&typ=R&mode=B&source=&'
    url = 'http://nregasp2.nic.in/netnrega/FTO/ResponseDetailStatusReport.aspx?lflag=eng&flg=W&page=b&state_name=%s&state_code=%s&district_name=%s&district_code=%s&block_name=%s&block_code=%s&panchayat_name=%s&panchayat_code=%s&fin_year=%s&typ=R&mode=B&source=&' % (state_name, state_code, district_name, district_code, block_name, block_code, panchayat_name, panchayat_code, fin_year)
        
    
    try:
        logger.info('Fetching URL[%s]' % url)
        response = requests.post(url)
    except Exception as e:
        logger.error('Caught Exception[%s]' % e)
        
    cookies = response.cookies
    reference_no_html = response.content

    filename = dirname + 'rejection_details.html'
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(reference_no_html)

    '''
    district_lookup = populate_district_lookup(logger, cookies=cookies, month = month, year = year)

    district_param=district_lookup[district_name]
    logger.info('Populating blocks for district[%s] param[%s]' % (district_name, district_param))
    block_lookup = populate_block_lookup(logger, cookies=cookies, district_lookup=district_lookup, district_param=district_param) # district_param='14,01,5')

    reference_no_lookup = populate_reference_no_lookup(logger, reference_no_html)
    '''    
    #FIXME fetch_fto_status_report(logger, cookies=cookies)

    ref_no = '3406004000NRG18010220180328089'
    ref_no = '3406004000NRG18021120170259332'
    #Reference url = 'http://nregasp2.nic.in/netnrega/FTO/Rejected_ref_no_detail.aspx?panchayat_code=3406004009&panchayat_name=Badkadihblock_code=3406004&block_name=Manika&flg=W&state_code=34&ref_no=3406004000NRG18010220180328089&fin_year=2017-2018&source='
    url = 'http://nregasp2.nic.in/netnrega/FTO/Rejected_ref_no_detail.aspx?panchayat_code=%s&panchayat_name=%sblock_code=%s&block_name=%s&flg=W&state_code=%s&ref_no=%s&fin_year=%s&source=' % (panchayat_code, panchayat_name, block_code, block_name, state_code, ref_no, fin_year)
    try:
        logger.info('Fetching URL[%s]' % url)
        response = requests.get(url)
    except Exception as e:
        logger.error('Caught Exception[%s]' % e)

    transaction_trail_html = response.content
    filename = dirname + '%s_%s_%s_%s_%s_%s.html' % (state_name, district_name, block_name, panchayat_name, ref_no, fin_year)
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(transaction_trail_html)

    bs = BeautifulSoup(transaction_trail_html, 'html.parser')
    table = bs.find(id="ctl00_ContentPlaceHolder1_grid_find_ref")
    logger.debug(str(table))

    tr_list = table.select('tr')
    logger.debug(str(tr_list))
    for tr in tr_list:
        if len(tr.select('td')) != 13:
            continue
        td = table.findChild('td')
        wagelist_no = td.text
        logger.info('Wagelist_No[%s]' % wagelist_no)
    
        td = td.findNext('td')
        jobcard_no = td.text
        logger.info('Jobcard_No[%s]' % jobcard_no)
    
        td = td.findNext('td')
        applicant_no = td.text
        logger.info('Applicant_No[%s]' % applicant_no)
    
        td = td.findNext('td')
        applicant_name = td.text
        logger.info('Applicant_Name[%s]' % applicant_name)
    
        td = td.findNext('td')
        work_code = td.text
        logger.info('Work_Code[%s]' % work_code)
    
        td = td.findNext('td')
        work_name = td.text
        logger.info('Work_Name[%s]' % work_name)
    
        td = td.findNext('td')
        msr_no = td.text
        logger.info('Msr_No[%s]' % msr_no)
    
        td = td.findNext('td')
        reference_no = td.text
        logger.info('Reference_No[%s]' % reference_no)
    
        td = td.findNext('td')
        status = td.text
        logger.info('Status[%s]' % status)
    
        td = td.findNext('td')
        rejection_reason = td.text
        logger.info('Rejection_Reason[%s]' % rejection_reason)
    
        td = td.findNext('td')
        process_date = td.text
        logger.info('Process_Date[%s]' % process_date)
    
        td = td.findNext('td')
        wagelist_fto_no = td.text
        logger.info('Wagelist_Fto_No[%s]' % wagelist_fto_no)
    
        td = td.findNext('td')
        serial_no = td.text
        logger.info('Serial_No[%s]' % serial_no)
    
        row = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (wagelist_no, jobcard_no, applicant_no, applicant_name, work_code, work_name, msr_no, reference_no, status, rejection_reason, process_date, wagelist_fto_no, serial_no)
        logger.info(row)
        csv_buffer.append(row)
        
    return 'SUCCESS'
    

##########
# Tests
##########

class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = loggerFetch('info')
        self.logger.info('BEGIN PROCESSING...')

    def tearDown(self):
        self.logger.info('...END PROCESSING')

    def test_r8_efms_report(self):
        result = fetch_efms_report(self.logger)
        self.assertEqual('SUCCESS', result)

if __name__ == '__main__':
    unittest.main()
