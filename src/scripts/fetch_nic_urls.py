import re
import unittest
from wrappers.logger import loggerFetch
import sys
import os
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(CUR_DIR)
REPO_DIR = os.path.dirname(ROOT_DIR)

sys.path.insert(0, ROOT_DIR)


#######################
# Global Declarations
#######################

curl_cmd = """curl 'http://mnregaweb4.nic.in/netnrega/MISreport4.aspx' -H 'Host: mnregaweb4.nic.in' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:45.0) Gecko/20100101 Firefox/45.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-GB,en;q=0.5' -H 'Accept-Encoding: gzip, deflate' -H 'Referer: http://mnregaweb4.nic.in/netnrega/MISreport4.aspx' -H 'Cookie: ASP.NET_SessionId=0v5asq45xeuubu453f0sivjb' -H 'Connection: keep-alive' -H 'Content-Type: application/x-www-form-urlencoded' --data '__EVENTTARGET=ctl00%24ContentPlaceHolder1%24ddl_States&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=WVzi9Ka7Y43Jcoh3DQrk9Hl6AbFqppTnX7m671rxPyWUJrJcMpX7yN47Ymd%2BB67%2B47nHL%2BNMGu%2B7a5WXNPlyFNtSTmqgfZw3jHWlvDoGUKLj%2BI3lvH%2BVFgPOQVPnIng%2FIgUw6jBZ%2FSVOBJpjnFeNEJGAhVg4ODqH5D0I2XBYgXNW2se%2BeiSZjuH2AD%2FzflYUfa1QXNwYbCkaUSO7JlWIPBNfCKuH4EQSpYV7I0CFHFP2TCbl&__VIEWSTATEENCRYPTED=&__EVENTVALIDATION=f%2B8DvUyjjse8EhC6ftqZpXY55rNwx0jUaLrM2hvG4kQNJJnyr1vb5YqDdzuWm3uDhl4KfRlClnpa5Fq5OsGEgu57rODtaFBZcClghlaqXBIDRq7aanwvmGvbEQ4yF%2Fmm1wWYE0SUj2tB%2FOcb1aI3zjFqWFE0CU%2FUXBhK%2FHh43BvqPaIXjdmlkQvVyEd1ziyWeqhRWbWeufdEdWvrKrsh4zEOZs8yVswreyLau8AE8FWSMohTktDdywAkml%2BNCCu%2BmnFCvsuQLvlsCCDEK3%2BfkmNq91Clexq684NINV1vhbbLDE%2Fyboa%2BaVCGwtQ%2FaUQzAQYH57Flq74FJ6MdzW5D%2F7AMgHYhEGoTlDiwNfjvecVFwWTqhH0JwY%2FRgCw59dFAiYfBHuAUz%2FNrCIqyakUrdJWypyL7tJ6cLOGmv%2BJqfgYmoTaJiLexkAxfi%2BAU58gvd3kUU4QOs2WIXLSe%2ByUoDxfsKy4%3D&ctl00%24ContentPlaceHolder1%24txtCaptcha=&ctl00%24ContentPlaceHolder1%24hfCaptcha=26&ctl00%24ContentPlaceHolder1%24ddlfinyr=2017-2018&ctl00%24ContentPlaceHolder1%24ddl_States=15DKNY'"""

states = [
    '01SANN',
    '02 APY',
    '03SARY',
    '04DASY',
    '05SBHY',
    '06DCGY',
    '33RCHY',
    '07 DNN',
    '08 DDN',
    '10 GON',
    '11SGJY',
    '12SHRY',
    '13DHPY',
    '14SJKY',
    '34DJHY',
    '15DKNY',
    '16RKLY',
    '19 LKN',
    '17DMPY',
    '18SMHY',
    '20SMNY',
    '21SMGY',
    '22SMZY',
    '23SNLY',
    '24SORY',
    '25SPCY',
    '26SPBY',
    '27SRJY',
    '28SSKY',
    '29RTNY',
    '36 TSY',
    '30STRY',
    '31RUPY',
    '35DUTY',
    '32RWBY',
]

finyears = [
    '2016-2017',
    '2017-2018',
    '2018-2019',
]

# dirname = '/tmp/'
dirname = './html'

#############
# Functions
#############


# Get the reports via curl cmd directly
def fetch_reports_cmd(logger):

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    '''
    filename = dirname + 'nic.html'
    #cmd = curl_cmd.replace('curl', 'curl -L -o nic.html') 
    cmd = curl_cmd + ' | gunzip > %s' % filename

    logger.info('Executing [%s]' % cmd)
    os.system(cmd)
    logger.info('File [%s] written' % filename)
    '''

    for state in states:
        state_cmd = re.sub(
            'ddl_States=[A-Z0-9]{6}', 'ddl_States=30STRY', curl_cmd)

        for finyear in finyears:
            filename = '%s/%s_%s.html' % (dirname, state, finyear)
            filename = filename.replace(' ', '_')
            cmd = re.sub('ddlfinyr=[^&]{9}', finyear,
                         state_cmd) + ' | gunzip > %s' % filename
            logger.info('Executing [%s]' % cmd)
            os.system(cmd)
            logger.info('File [%s] written' % filename)

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

    def test_direct_cmd(self):
        result = fetch_reports_cmd(self.logger)
        self.assertEqual('SUCCESS', result)

    @unittest.skip('Skipping direct command approach')
    def test_fetch_reports(self):
        result = fetch_reports(self.logger)
        self.assertEqual('SUCCESS', result)


if __name__ == '__main__':
    unittest.main()
