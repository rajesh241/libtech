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

csv_buffer=['Wagelist No,Job card no,Applicant no,Applicant Name,Work Code,Work Name,MSR no,Reference No,Status,Rejection Reason,Proccess Date,Wage list FTO No.,Serial No.\n']


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

def populate_panchayat_list(logger, state_name, state_code, district_name, district_code, block_name, block_code, fin_year):
    panchayat_list = {}

    #Reference url = 'http://nregasp2.nic.in/netnrega/Progofficer/PoIndexFrame.aspx?flag_debited=D&lflag=local&District_Code=3406&district_name=LATEHAR&state_name=JHARKHAND&state_Code=34&finyear=2018-2019&check=1&block_name=Manika&Block_Code=3406004'
    url = 'http://nregasp2.nic.in/netnrega/Progofficer/PoIndexFrame.aspx?flag_debited=D&lflag=local&District_Code=3406&district_name=LATEHAR&state_name=JHARKHAND&state_Code=34&finyear=2018-2019&check=1&block_name=Manika&Block_Code=3406004'

    try:
        logger.info('Fetching URL[%s]' % url)
        response = requests.post(url)
    except Exception as e:
        logger.error('Caught Exception[%s]' % e)
        
    panchayat_list_html = response.content
    
    filename = dirname + 'panchayat_list.html'
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(panchayat_list_html)

    bs = BeautifulSoup(panchayat_list_html, 'html.parser')

    table = bs.find(id='ctl00_ContentPlaceHolder1_gvpanch')
    logger.debug(str(table))
    click_list = table.findAll('a')
    logger.debug(str(click_list))

    for anchor in click_list:
        a = str(anchor)
        pos = a.find('Panchayat_name=')
        logger.debug(pos)
        if pos > 0:
            beg = a.find('Panchayat_name=') + len('Panchayat_name=')
            end = a.find('&amp;Panchayat_Code=') 
            panchayat_name = a[beg:end]
            beg = a.find('Panchayat_Code=') + len('Panchayat_Code=')
            end = beg + 10
            panchayat_code = a[beg:end]
            panchayat_list[panchayat_name] = panchayat_code
            logger.info('Found [%s, %s]...' % (panchayat_name, panchayat_code))

    return panchayat_list
        
def populate_reference_no_lookup(logger, reference_no_html):
    reference_no_list = []
    
    bs = BeautifulSoup(reference_no_html, 'html.parser')
    span = bs.find(id='ctl00_ContentPlaceHolder1_lbl_head')
    logger.debug('SPAN[%s]' % str(span))

    table = span.findNext('table')
    logger.debug(str(table))

    tr_list = table.select('tr')
    logger.debug(str(tr_list))

    is_first_row = True
    for tr in tr_list:
        if is_first_row:
            is_first_row = False
            continue
        td = tr.findChild('td')
        serial_no = td.text
        logger.debug('Serial_No[%s]' % serial_no)

        td = td.findNext('td')
        fto_no = td.text
        logger.debug('Fto_No[%s]' % fto_no)
        
        td = td.findNext('td')
        reference_no = td.text.strip()
        logger.debug('Reference_No[%s]' % reference_no)

        reference_no_list.append(reference_no)
        
    return reference_no_list
    

def parse_transaction_trail(logger, transaction_trail_html):
    bs = BeautifulSoup(transaction_trail_html, 'html.parser')
    table = bs.find(id='ctl00_ContentPlaceHolder1_grid_find_ref')
    logger.debug(str(table))

    tr_list = table.select('tr')
    logger.debug(str(tr_list))
    is_first_row = True
    for tr in tr_list:
        logger.debug('ROW[%s]' % str(tr))        
        if is_first_row:
            is_first_row = False
            logger.debug('HEADER[%s]' % str(tr))        
            continue
        td = tr.findChild('td')
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
    
        row = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (wagelist_no, jobcard_no, applicant_no, applicant_name, work_code, work_name, msr_no, reference_no, status, rejection_reason, process_date, wagelist_fto_no, serial_no)
        logger.info(row)
        csv_buffer.append(row)
    

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

    panchayat_list = populate_panchayat_list(logger, state_name, state_code, district_name, district_code, block_name, block_code, fin_year)

    
    for (panchayat_name, panchayat_code) in panchayat_list.items():
        # reference_no_html = fetch_reference_numbers_html(logger, state_name, state_code, district_name, district_code, block_name, block_code, panchayat_name, panchayat_code, fin_year)
    
        #Reference url = 'http://nregasp2.nic.in/netnrega/FTO/ResponseDetailStatusReport.aspx?lflag=eng&flg=W&page=b&state_name=JHARKHAND&state_code=34&district_name=LATEHAR&district_code=3406&block_name=Manika&block_code=3406004&panchayat_name=Badkadih&panchayat_code=3406004009&fin_year=2017-2018&typ=R&mode=B&source=&'
        url = 'http://nregasp2.nic.in/netnrega/FTO/ResponseDetailStatusReport.aspx?lflag=eng&flg=W&page=b&state_name=%s&state_code=%s&district_name=%s&district_code=%s&block_name=%s&block_code=%s&panchayat_name=%s&panchayat_code=%s&fin_year=%s&typ=R&mode=B&source=&' % (state_name, state_code, district_name, district_code, block_name, block_code, panchayat_name, panchayat_code, fin_year)
            
        
        try:
            logger.info('Fetching URL[%s]' % url)
            response = requests.post(url)
        except Exception as e:
            logger.error('Caught Exception[%s]' % e)
            
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
        '''
    
        reference_no_list = populate_reference_no_lookup(logger, reference_no_html)
        logger.debug(reference_no_list)
    
        for ref_no in reference_no_list:
            # ref_no = '3406004000NRG18010220180328089'
            # ref_no = '3406004000NRG18021120170259332'
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
        
            parse_transaction_trail(logger, transaction_trail_html)
    
        filename = dirname + '%s_%s_%s_%s_%s.csv' % (state_name, district_name, block_name, panchayat_name, fin_year)
        with open(filename, 'w') as csv_file:
            logger.info("Writing to [%s]" % filename)
            csv_file.write(''.join(csv_buffer))
        
    # Ends fetch_reference_no_html()
            
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
