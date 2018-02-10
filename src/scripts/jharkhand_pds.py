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
def fetch_block_list(logger, district_code='14', month='01', year_code='5', district_param=None, district_lookup=None):
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

    if district_param:
        parameters = district_param
    else:
        parameters = district_code + ',' + month + ',' + year_code
    logger.info('Parameters for block list [%s]' % parameters)
    data = [
        ('_method', 'POST'),
        ('data[BlockCityMonthlyReport][ide]', parameters),
    ]

    response = requests.post('http://aahar.jharkhand.gov.in/block_city_monthly_reports', headers=headers, cookies=cookies, data=data)

    return response.content



# Fetch the dealer list where you can find all the dealer codes for the given block
def fetch_dealer_list(logger, district_name = '', block_name = '', month='01', year='', block_param=None):
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

    if block_param:
        parameters = block_param
        # parameters = '151,01,5,14'
    else:
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
    
    shop_name = bs.find('b').text.strip().replace(' ', '-')
    logger.debug(shop_name)
    
    # filename = './dealers/' + dealer_code[0:36] + '.html'
    # Remove dealer code from below - Sakina
    # filename = './dealers/' + district_name + '_' + block_name + '_' + shop_name + '_' + dealer_code[0:36] + '.html'
    filename = './dealers/' + district_name + '_' + block_name + '_' + shop_name + '.html'
    logger.info(filename)

    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.content)

    return 'SUCCESS'


def populate_dealer_lookup(logger, block_param):
    logger.info('Fetching Dealer List for [%s]...' % (block_param))
    dealer_list_html = fetch_dealer_list(logger, block_param)

    filename = 'dealer_list.html'
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(dealer_list_html)
    
    bs = BeautifulSoup(dealer_list_html, 'html.parser')
    click_list = bs.findAll('a')
    logger.debug(str(click_list))

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
            end = a.find("')")
            district_param = a[beg:end]  # 28:71
            logger.debug('district_param[%s]...' % district_param)
            beg = a.find('value="') + len('value="')
            end = a[beg:].find('"')
            district_name = a[beg:beg+end]
            logger.debug(district_name)
            district_lookup[district_name] = district_param
    logger.info('District Lookup[%s]' % district_lookup)

    return district_lookup


def populate_block_lookup(logger, district_param=None, district_lookup=None):
    logger.info('Fetching block_list...')
    block_list_html = fetch_block_list(logger, district_param=district_param, district_lookup=district_lookup)
    filename = 'block_lists.html'
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(block_list_html)

    bs = BeautifulSoup(block_list_html, 'html.parser')
    click_list = bs.findAll('a')
    logger.debug(str(click_list))

    for anchor in click_list:
        a = str(anchor)
        pos = a.find('onclick="javascript:send(')
        logger.debug(pos)
        if pos > 0:
            beg = a.find("('") + 2
            end = a.find("')")
            block_param = a[beg:end]  # 28:71
            logger.debug('block_param[%s]...' % block_param)
            beg = a.find('value="') + len('value="')
            end = a[beg:].find('"')
            block_name = a[beg:beg+end]
            logger.debug(block_name)
            block_lookup[block_name] = block_param
    logger.info('Block Lookup[%s]' % block_lookup)

    return block_lookup


def fetch_pds(logger):
    logger.info('Fetching PDS related info...')

    district_lookup = populate_district_lookup(logger)

    block_lookup = populate_block_lookup(logger, district_lookup=district_lookup, district_param=district_lookup[district_name]) # district_param='14,01,5')

    populate_dealer_lookup(logger, block_lookup[block_name]) # '151,01,5,14') # 

    return 'SUCCESS'

############################################################################



card_types = {
    '5' : 'PH',
    '6' : 'AAY',
    '7' : 'WHITE',
    }


village_codes = {
    '366879':'Agardih Mandhania',
    '366847':'Ambatikar',
    '366846':'Antikheta',
    '366917':'Ara',
    '366922':'Aunratanr',
    '366881':'Bandua',
    '366855':'Banri',
    '366871':'Baraitola',
    '366892':'Baraitu',
    '366926':'Barkadih',
    '366864':'Barwadih',
    '366884':'Barwaia Kalan',
    '366886':'Barwaia Khurd',
    '366902':'Beang',
    '366885':'Betla',
    '366868':'Bhatko',
    '366913':'Bichlidag',
    '366904':'Bikra',
    '366910':'Bishunbandh',
    '366888':'Chama',
    '366859':'Chechendha',
    '366867':'Dasdih',
    '366925':'Deobar',
    '366890':'Doki',
    '366865':'Dumbi',
    '366872':'Dumri',
    '366914':'Dundu',
    '366856':'Ejamar',
    '366845':'Hatla',
    '366893':'Hesatu',
    '366850':'Humamara',
    '366848':'Jabla',
    '366869':'Jagtu',
    '366909':'Jalima',
    '366882':'Jamho',
    '366852':'Jamuna',
    '366870':'Jerua',
    '366921':'Jungur',
    '366866':'Khapiadih',
    '366876':'Koili',
    '366873':'Kope',
    '366905':'Kuchal',
    '366877':'Kui',
    '366901':'Kurid',
    '366844':'Kurumkheta',
    '366900':'Kurund',
    '366860':'Kutmu',
    '366923':'Lali',
    '366874':'Lanka',
    '366927':'Lawagara',
    '366912':'Madandih',
    '366915':'Mail',
    '366854':'Manika',
    '366858':'Manikdih',
    '366918':'Matlaung',
    '366906':'Matnag',
    '366887':'Matnog',
    '366924':'Nadbelwa',
    '366899':'Naihara',
    '366857':'Namudag',
    '366862':'Nawadih',
    '366903':'Newar',
    '366894':'Pagar',
    '366919':'Palhea',
    '366896':'Pasagam',
    '366849':'Patki',
    '366883':'Patna',
    '366861':'Pokhri',
    '366920':'Puruipalhea',
    '366878':'Ranki Kalan',
    '366907':'Rewad Kalan',
    '366908':'Rewad Khurd',
    '366880':'Sadhwadih',
    '366911':'Salgi',
    '366898':'Sardandag',
    '366895':'Seldag',
    '366889':'Sewan',
    '366875':'Sewdhara',
    '366863':'Simri',
    '366853':'Sinjo',
    '366891':'Siris',
    '366851':'Siwacharan Tola',
    '366897':'Sonsdohar',
    '366916':'Uraontoli',

    }

village_list = {
    'Agardih Mandhania':'366879',
    'Ambatikar':'366847',
    'Antikheta':'366846',
    'Ara':'366917',
    'Aunratanr':'366922',
    'Bandua':'366881',
    'Banri':'366855',
    'Baraitola':'366871',
    'Baraitu':'366892',
    'Barkadih':'366926',
    'Barwadih':'366864',
    'Barwaia Kalan':'366884',
    'Barwaia Khurd':'366886',
    'Beang':'366902',
    'Betla':'366885',
    'Bhatko':'366868',
    'Bichlidag':'366913',
    'Bikra':'366904',
    'Bishunbandh':'366910',
    'Chama':'366888',
    'Chechendha':'366859',
    'Dasdih':'366867',
    'Deobar':'366925',
    'Doki':'366890',
    'Dumbi':'366865',
    'Dumri':'366872',
    'Dundu':'366914',
    'Ejamar':'366856',
    'Hatla':'366845',
    'Hesatu':'366893',
    'Humamara':'366850',
    'Jabla':'366848',
    'Jagtu':'366869',
    'Jalima':'366909',
    'Jamho':'366882',
    'Jamuna':'366852',
    'Jerua':'366870',
    'Jungur':'366921',
    'Khapiadih':'366866',
    'Koili':'366876',
    'Kope':'366873',
    'Kuchal':'366905',
    'Kui':'366877',
    'Kurid':'366901',
    'Kurumkheta':'366844',
    'Kurund':'366900',
    'Kutmu':'366860',
    'Lali':'366923',
    'Lanka':'366874',
    'Lawagara':'366927',
    'Madandih':'366912',
    'Mail':'366915',
    'Manika':'366854',
    'Manikdih':'366858',
    'Matlaung':'366918',
    'Matnag':'366906',
    'Matnog':'366887',
    'Nadbelwa':'366924',
    'Naihara':'366899',
    'Namudag':'366857',
    'Nawadih':'366862',
    'Newar':'366903',
    'Pagar':'366894',
    'Palhea':'366919',
    'Pasagam':'366896',
    'Patki':'366849',
    'Patna':'366883',
    'Pokhri':'366861',
    'Puruipalhea':'366920',
    'Ranki Kalan':'366878',
    'Rewad Kalan':'366907',
    'Rewad Khurd':'366908',
    'Sadhwadih':'366880',
    'Salgi':'366911',
    'Sardandag':'366898',
    'Seldag':'366895',
    'Sewan':'366889',
    'Sewdhara':'366875',
    'Simri':'366863',
    'Sinjo':'366853',
    'Siris':'366891',
    'Siwacharan Tola':'366851',
    'Sonsdohar':'366897',
    'Uraontoli':'366916',
}

def post_ration_req(logger, cookies=None, village_code=None, card_type=None, ration_number=None):
    logger.info('Fetch the Ration List for Village[%s] Card Type[%s]' % (village_code, card_type))

    if not cookies:        
        url="http://aahar.jharkhand.gov.in/district_monthly_reports/"
        response = requests.post(url)
        cookies = response.cookies

    headers = {
        'Origin': 'http://aahar.jharkhand.gov.in',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.97 Safari/537.36 Vivaldi/1.94.1008.44',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Referer': 'http://aahar.jharkhand.gov.in/secc_cardholders/searchRation',
        'Connection': 'keep-alive',
    }

    data = [
        ('_method', 'POST'),
        ('data[SeccCardholder][rgi_district_code]', '359'),
        ('data[SeccCardholder][rgi_block_code]', '02635'),
        ('r1', 'panchayat'),
        ('data[SeccCardholder][rgi_village_code]', village_code),
        ('data[SeccCardholder][dealer_id]', ''),
        ('data[SeccCardholder][cardtype_id]', card_type),
    ]
    if ration_number:
        data.append(('data[SeccCardholder][rationcard_no]', ration_number))
    logger.info('Data [%s]' % data)
    
    response = requests.post('http://aahar.jharkhand.gov.in/secc_cardholders/searchRationResults', headers=headers, cookies=cookies, data=data)

    filename = 'ration_list.html'
    if ration_number:
        filename = './ration/' + ration_number + '.html'
    if village_code:
        filename = './ration/' + village_codes[village_code] + '_' + card_types[card_type] + '.html'
    logger.info(filename)

    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.content)

    return response.content


def populate_ration_list(logger, cookies=None, village_code='366884', card_type='7'):
    logger.info('Fetch the Ration List for Village[%s] Card Type[%s]' % (village_code, card_type))

    ration_list_html = post_ration_req(logger, cookies=cookies, village_code=village_code, card_type=card_type)

    bs = BeautifulSoup(ration_list_html, 'html.parser')

    click_list = bs.findAll('a')
    logger.debug(str(click_list))

    for anchor in click_list:
        a = str(anchor)
        logger.debug(a)
        pos = a.find('onclick="javascript:send(')
        logger.debug(pos)
        if pos > 0:
            beg = a.find("('") + 2
            end = a.find("')") 
            ration_number = a[beg:end]  # 28:71
            logger.info('Fetching the dealer[%s]...' % ration_number)
            fetch_ration_details(logger, cookies=cookies, village_code=village_code, card_type=card_type, ration_number=ration_number)
            # ration_list.append(ration_number)
            # exit(0)

    return 'SUCCESS'

def fetch_ration_details(logger, cookies=None, village_code='366884', card_type='7', ration_number='202006979912'):
    logger.info('Getting the Ration Details')

    return post_ration_req(logger, cookies=cookies, village_code=village_code, card_type=card_type, ration_number=ration_number)


def fetch_ration(logger):
    logger.info('Getting the Ration Details')
    url='http://aahar.jharkhand.gov.in/secc_cardholders/searchRation'
    #url="http://aahar.jharkhand.gov.in/district_monthly_reports/"
    response = requests.post(url)
    cookies = response.cookies

    #ration_list = populate_ration_list(logger, cookies=cookies, village_code='366890', card_type='5')

    for village_code in village_codes.keys():
        for card_type in card_types.keys():
            ration_list_html = post_ration_req(logger, cookies=cookies, village_code=village_code, card_type=card_type)

    '''
        ration_list_html = post_ration_req(logger, cookies=cookies, village_code=village_code, card_type='5')
        ration_list_html = post_ration_req(logger, cookies=cookies, village_code=village_code, card_type='6')
        ration_list_html = post_ration_req(logger, cookies=cookies, village_code=village_code, card_type='7')
    # fetch_ration_details(logger, ration_list=ration_list)
    '''
    
    return 'SUCCESS'


def post_ration_reference(logger, cookies=None, district_code=None, block_code=None):
    logger.info('Fetch the Ration Summary Cookies[%s]' % cookies)

    if not cookies:        
        url='http://aahar.jharkhand.gov.in/secc_districts/districts'
        response = requests.post(url)
        cookies = response.cookies

    headers = {
        'Host': 'aahar.jharkhand.gov.in',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'http://aahar.jharkhand.gov.in/secc_blocks/blockCardholderCount',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    data = [
        ('_method', 'POST'),
        # ('data[SeccBlockReport][distId]', '365'),
        # ('data[SeccBlockReport][ide]', '02704'),
    ]

    if district_code:
        if block_code:
            data.append(('data[SeccBlockReport][distId]', district_code))
            data.append(('data[SeccBlockReport][ide]', block_code))
            logger.info('Posting with Data[%s]' % str(data))
            logger.info('Posting with district[%s] block [%s]' % (district_code, block_code))
            response = requests.post('http://aahar.jharkhand.gov.in/secc_village_wards/villageCardholderCount', headers=headers, cookies=cookies, data=data)
            filename = district_code + '_district_' + block_code + '_block.html'
        else:
            data.append(('data[SeccDistrictReport][ide]', district_code))
            logger.info('Posting with District [%s]' % district_code)
            logger.info('Posting with Data[%s]' % str(data))
            response = requests.post('http://aahar.jharkhand.gov.in/secc_blocks/blockCardholderCount', headers=headers, cookies=cookies, data=data)
            filename = district_code + '_district.html'
    else:
        response = requests.get('http://aahar.jharkhand.gov.in/secc_districts/districts', headers=headers, cookies=cookies)
        filename = 'blocks_reference.html'
        
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.content)

    return response.content


'''
def post_ration_districts(logger, cookies=None):
    logger.info('Fetch the Ration Summary Cookies[%s]' % cookies)

    if not cookies:        
        url='http://aahar.jharkhand.gov.in/secc_districts/districts'
        response = requests.post(url)
        cookies = response.cookies

    headers = {
        'Host': 'aahar.jharkhand.gov.in',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    response = requests.get('http://aahar.jharkhand.gov.in/secc_districts/districts', headers=headers, cookies=cookies)

    filename = 'district_reference.html'
    with open(filename, 'wb') as html_file:
        logger.info('Writing [%s]' % filename)
        html_file.write(response.content)

    return response.content
'''

def ration_block_fetch(logger, cookies=None, district_name=None):
    logger.info('Getting the Ration Block Lists for District[%s]' % district_name)
    block_ration_html = post_ration_reference(logger, cookies=cookies, district_code=district_lookup[district_name])
    logger.debug(block_ration_html)
    
    bs = BeautifulSoup(block_ration_html, 'html.parser')
    click_list = bs.findAll('a')
    logger.debug(str(click_list))

    for anchor in click_list:
        a = str(anchor)
        pos = a.find('onclick="javascript:send(')
        logger.debug(pos)
        if pos > 0:
            beg = a.find("('") + 2
            end = a.find("')")
            block_param = a[beg:end]
            logger.info('block_param[%s]...' % block_param)
            beg = a.find('<span name="') + len('<span name="data[SeccDistrictReport][i]" style="color:#0000FF; font-size:12px;">')
            end = a[beg:].find('</span>')
            block_name = a[beg:beg+end]
            logger.info(block_name)
            block_lookup[block_name] = block_param
    logger.info('Block Lookup[%s]' % block_lookup)


def ration_village_fetch(logger, cookies=None, district_name=None, block_name=None):
    logger.info('Getting the Ration Block Lists for District[%s] Block[%s]' % (district_name, block_name))
    village_ration_html = post_ration_reference(logger, cookies=cookies, district_code=district_lookup[district_name], block_code=block_lookup[block_name]) # '02635')
    logger.debug(village_ration_html)
    
    bs = BeautifulSoup(village_ration_html, 'html.parser')
    tr_list = bs.findAll('tr')
    logger.debug(str(tr_list))
    
    for tr in tr_list:
        td = tr.find('td')

        #logger.info('Name[%s] in Hindi[%s]' %(td.text.strip(), td.findNext('td').text.strip()))
        count = 11
        while count:
            count -= 1
            try:
                td = td.findNext('td')
            except:
                logger.error('Should not come here!')

        logger.info('Sl No[%s]' % td.text.strip())
        td = td.findNext('td')
                
        logger.info('Name[%s]' % td.text.strip())
        td = td.findNext('td')
                
        logger.info('Hindi[%s]' % td.text.strip())
        td = td.findNext('td')
                
        logger.info('PH Head[%s]' % td.text.strip())
        td = td.findNext('td')
                
        logger.info('PH Member[%s]' % td.text.strip())
        td = td.findNext('td')
                
        logger.info('AAY Head[%s]' % td.text.strip())
        td = td.findNext('td')
                
        logger.info('AAY Member[%s]' % td.text.strip())
        td = td.findNext('td')
                
        logger.info('Total Heads[%s]' % td.text.strip())
        td = td.findNext('td')
                
        logger.info('Total Members[%s]' % td.text.strip())
        td = td.findNext('td')
                
        logger.info('White Head[%s]' % td.text.strip())
        td = td.findNext('td')
                
        logger.info('White Member[%s]' % td.text.strip())
        td = td.findNext('td')
                
        '''
        while True:
            logger.info(td.text.strip())
            try:
                td = td.findNext('td')
            except:
                exit(0)
        '''
        exit(0)
        if False:
            # if pos > 0:
            beg = row.find("('") + 2
            end = row.find("')") 
            block_name = row[beg:end] 
            logger.info('Fetching the block[%s]...' % block_name)
            # fetch_dealer_detail(logger, dealer_code)
            a = row
            beg = a.find('<span') + len('value="')
            end = a[beg:].find('"')
            district_name = a[beg:beg+end]
            logger.info(district_name)
            # district_lookup[district_name] = district_param
    '''
    click_list = bs.findAll('a')
    logger.debug(str(click_list))

    for anchor in click_list:
        a = str(anchor)
        pos = a.find('onclick="javascript:send(')
        logger.debug(pos)
        if pos > 0:
            beg = a.find("('") + 2
            end = a.find("')")
            block_param = a[beg:end]
            logger.info('block_param[%s]...' % block_param)
            beg = a.find('<span name="') + len('<span name="data[SeccDistrictReport][i]" style="color:#0000FF; font-size:12px;">')
            end = a[beg:].find('</span>')
            block_name = a[beg:beg+end]
            logger.info(block_name)
            block_lookup[block_name] = block_param
    logger.info('Block Lookup[%s]' % block_lookup)
    '''

def ration_reports(logger):
    logger.info('Getting the Ration Summary')
    url='http://aahar.jharkhand.gov.in/secc_districts/districts'
    response = requests.post(url)
    cookies = response.cookies

    district_ration_html = post_ration_reference(logger, cookies=cookies)
    logger.debug(district_ration_html)
    
    bs = BeautifulSoup(district_ration_html, 'html.parser')
    click_list = bs.findAll('a')
    logger.debug(str(click_list))

    for anchor in click_list:
        a = str(anchor)
        pos = a.find('onclick="javascript:send(')
        logger.debug(pos)
        if pos > 0:
            beg = a.find("('") + 2
            end = a.find("')")
            district_param = a[beg:end]
            logger.info('district_param[%s]...' % district_param)
            beg = a.find('<span name="') + len('<span name="data[SeccDistrictReport][i]" style="color:#0000FF; font-size:12px ;">')
            end = a[beg:].find('</span>')
            district_name = a[beg:beg+end]
            logger.info(district_name)
            district_lookup[district_name] = district_param
    logger.info('District Lookup[%s]' % district_lookup)

    ration_block_fetch(logger, cookies, district_name='Latehar')    
    ration_village_fetch(logger, cookies, district_name='Latehar', block_name='Manika')
    
    # ration_block_fetch(logger, cookies, district_name='Khunti')
    # ration_block_fetch(logger, cookies, district_name='Ranchi')
    
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
        result = ration_reports(self.logger)
        self.assertEqual('SUCCESS', result)

if __name__ == '__main__':
    unittest.main()

