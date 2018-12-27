import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from bs4 import BeautifulSoup

from wrappers.logger import loggerFetch
import unittest
import requests
import time

timeout=60
dirname = './reports/'
filename = dirname
district_name = 'NAYAGARH'
block_name = 'Nuagaon'
panchayat = 'BAHADAJHOLA'

# Get the reports via curl cmd directly
def fetch_reports_cmd(logger):
    cmd= '''curl -L -o district_list.html 'curl 'https://www.google.com/url?q=http://mnregaweb2.nic.in/netnrega/state_html/empspecifydays.aspx?page%3DP%26lflag%3Deng%26state_name%3DODISHA%26state_code%3D24%26district_name%3DNAYAGARH%26district_code%3D2422%26block_name%3DNuagaon%26fin_year%3D2017-2018%26Block_code%3D2422004%26&sa=D&source=hangouts&ust=1545720831376000&usg=AFQjCNHkWGSasgE4mlyC6HenvHabiZZvFQ' -H 'Host: www.google.com' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:60.0) Gecko/20100101 Firefox/60.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Cookie: SID=lQbrI25ydlNYYkFnVn1kZQd8zoQvU9hvTKI8_htgUqXNzBbSO73PncLfw8ohFqv3Wys2Og.; HSID=ASJDxhlLy7HzVWk_Q; SSID=ACrFLZJ--tBKIWoeu; APISID=BKmMZyKBbXC90KdV/A5X9MZfItPEgJHrHp; SAPISID=1wSnKDwOZ8YGBQ6_/Az-Hw_RJi0WQuhlOz; OGP=-5061451:-19006965:; NID=152=iuwrZ5Ne3_AfWF4AqoACvFT4sYsL-VFRkD_uMTAANE0eUodsbqzhTLSlyfOJ1GZE9whTgEFrkPFhSSonY-0WxFSZP72fDp318PnCicwRw4ehcwKuxiTZLjhNHPda5yyWaczNCB8_KEmUkFoYxSNPCNrunutqOn_qn5_OLVRhxakYrkCcbma0KwDy6um5qQ22lozZ6Q8HtdCtm1bp8Ecd0MXEsq7OHc_MqNM_LLqc8ek8FMnq7aBUVeXaWPC8VjoDWBQw0OTzjnt_3iR-kX_E08id; _ga=GA1.1.1794022198.1519327020; SIDCC=ABtHo-E4DPq7nxryyu9XiFNYpYXRkwu_ar0sVHNEMxDTsLUhdfo9AA78OWlQAYFwqZIVHDuKVek5; 1P_JAR=2018-12-24-05; OGPC=19008374-2:19009193-2:19009353-2:' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1'' '''

    os.system(cmd)
    logger.info('Executing [%s]' % cmd)

    return 'SUCCESS'


# Fetch the list of all the districts for the given month and year
def fetch_reports(logger, cookies=None, month='01', year='2018', district_name=None):
    if not district_name:
        district_name = 'NAYAGARH'
    logger.info('Fetch district list for given month[%s] and year[%s]' % (month, year))
    filename = dirname + 'district_list_%s.html' % district_name

    if os.path.exists(filename):
        with open(filename, 'rb') as html_file:
            logger.info('File already donwnloaded. Reading [%s]' % filename)
            district_list_html = html_file.read()
    
        return district_list_html

    session = requests.Session()
 
    if not cookies:
        # url = 'http://nregasp2.nic.in/netnrega/state_html/empspecifydays.aspx?page=P&lflag=eng&state_name=BIHAR&state_code=05&district_name=VAISHALI&district_code=0516&block_name=VAISHALI&fin_year=2017-2018&Block_code=0516005&'
        url = 'http://mnregaweb2.nic.in/netnrega/state_html/empspecifydays.aspx?page=P&lflag=eng&state_name=ODISHA&state_code=24&district_name=NAYAGARH&district_code=2422&block_name=Nuagaon&fin_year=2017-2018&Block_code=2422004&'
        url = 'http://mnregaweb2.nic.in/netnrega/state_html/empspecifydays.aspx?page=P&lflag=eng&state_name=ODISHA&state_code=24&district_name=GAJAPATI&district_code=2424&block_name=MOHONA&fin_year=2017-2018&Block_code=2424004&'

        '''
        import urllib.request
        response = urllib.request.urlopen(url)
        cookies = response
        logger.info(str(cookies))
        '''
        logger.info('Fetching URL[%s]' % url)
        response = session.post(url, timeout=timeout, verify=False, allow_redirects=False)
        res = response
        if res.status_code == 302: # expected here
            jar = res.cookies
            logger.info('Jar ' + str(jar))
            redirect_URL2 = res.headers['Location']
            logger.error('URL = ' + redirect_URL2)
            url = res.history[0].url
            logger.error('histor url = ' + url)            
            res = session.get(redirect_URL2, cookies=jar)
            # res2 is made with cookies collected during res' 302 redirect                
        # logger.info('XPATH[%s]' % response.xpath("//*[@id='__VIEWSTATE']/@value").extract())
        cookies = session.cookies
        cookies = requests.cookies.RequestsCookieJar()
        logger.info('Cookies = ' + str(res.cookies))
        '''
        response = session.post(url, timeout=timeout, verify=False)
        cookies = session.cookies
        logger.info(str(cookies))
        '''
    else:
        cookies = {
            'ASP.NET_SessionId': 'tzjumqmozpmbajiuq4hyy555',
        }

    '''
    headers = {
        'Host': 'mnregaweb2.nic.in',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:60.0) Gecko/20100101 Firefox/60.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    params = (
        ('page', 'P'),
        ('lflag', 'eng'),
        ('state_name', 'ODISHA'),
        ('state_code', '24'),
        ('district_name', 'NAYAGARH'),
        ('district_code', '2422'),
        ('block_name', 'Nuagaon'),
        ('fin_year', '2017-2018'),
        ('Block_code', '2422004'),
        ('', ''),
    )

    response = session.get('http://mnregaweb2.nic.in/netnrega/state_html/empspecifydays.aspx', headers=headers, params=params, allow_redirects=False)

    cookies = session.cookies
    logger.info(str(cookies))
    logger.info('Policy ' + str(response.history))
    '''
    myhtml=response.content
    htmlsoup=BeautifulSoup(myhtml,"lxml")
    validation = htmlsoup.find(id='__EVENTVALIDATION').get('value')
    logger.info(validation)
    viewState = htmlsoup.find(id='__VIEWSTATE').get('value')
    logger.info(viewState)
    cookies=session.cookies
    logger.info('No Cookies: ' + str(cookies)) #  + '==' + r.text)

    #######    

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'http://mnregaweb2.nic.in/netnrega/state_html/empspecifydays.aspx?page=P&lflag=eng&state_name=ODISHA&state_code=24&district_name=GAJAPATI&district_code=2424&block_name=MOHONA&fin_year=2017-2018&Block_code=2424004&',
        'X-MicrosoftAjax': 'Delta=true',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

    params = (
        ('page', 'P'),
        ('lflag', 'eng'),
        ('state_name', 'ODISHA'),
        ('state_code', '24'),
        ('district_name', 'GAJAPATI'),
        ('district_code', '2424'),
        ('block_name', 'MOHONA'),
        ('fin_year', '2017-2018'),
        ('Block_code', '2424004'),
        ('', ''),
    )

    data = {
        'ctl00$ContentPlaceHolder1$ScriptManager1': 'ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$btn_pro',
        'ctl00$ContentPlaceHolder1$ddr_panch': '2424004002',
        'ctl00$ContentPlaceHolder1$ddr_cond': 'gt',
        'ctl00$ContentPlaceHolder1$lbl_days': '0',
        'ctl00$ContentPlaceHolder1$rblRegWorker': 'Y',
        '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btn_pro',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': viewState,
        '__EVENTVALIDATION': validation,
        '__VIEWSTATEENCRYPTED': '',
        '__ASYNCPOST': 'true',
        '': ''
    }

    response = session.post('http://mnregaweb2.nic.in/netnrega/state_html/empspecifydays.aspx', headers=headers, params=params, data=data, allow_redirects=False)
    res = response
    logger.info('status code [%s]' % res.status_code)
    if res.status_code == 302: # expected here
        jar = res.cookies
        logger.info('Jar ' + str(jar))
        redirect_URL2 = res.headers['Location']
        logger.error('URL = ' + redirect_URL2)
        url = res.history[0].url
        logger.error('histor url = ' + url)            
        res = session.get(redirect_URL2, cookies=jar)
        # res2 is made with cookies collected during res' 302 redirect                
        # logger.info('XPATH[%s]' % response.xpath("//*[@id='__VIEWSTATE']/@value").extract())
    cookies = session.cookies
    logger.info('Yippie = ' + str(cookies))
    cookies = requests.cookies.RequestsCookieJar()
    logger.info('Cookies = ' + str(res.cookies))

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'http://mnregaweb2.nic.in/netnrega/state_html/empspecifydays.aspx?page=P&lflag=eng&state_name=ODISHA&state_code=24&district_name=GAJAPATI&district_code=2424&block_name=MOHONA&fin_year=2017-2018&Block_code=2424004&',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    params = (
        ('lflag', 'eng'),
        ('fin_year', '2017-2018'),
        ('RegWorker', 'Y'),
    )

    response = requests.get('http://mnregaweb2.nic.in/netnrega/state_html/empprovdays.aspx', headers=headers, params=params, cookies=cookies)
    district_list_html = response.content
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(district_list_html)

    '''
    cookies = session.cookies
    logger.info(str(cookies))
    logger.info('History ' + str(response.history))
    '''

    session.keep_alive = False  # session.quit()
    
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
        result = fetch_district_cmd(logger)
        self.assertEqual('SUCCESS', result)

    def test_fetch_reports(self):
        result = fetch_reports(self.logger)
        self.assertEqual('SUCCESS', result)

if __name__ == '__main__':
    unittest.main()

