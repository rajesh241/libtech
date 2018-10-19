import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

import requests
import unittest
from bs4 import BeautifulSoup

import pandas as pd

from wrappers.logger import loggerFetch


#######################
# Global Declarations
#######################

#timeout = 10


#############
# Functions
#############

def create_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != os.errno.EEXIST:
            raise

def fetchBlockData(logger, dirname, block_name=None):
    filename = '%s.html' % block_name

    with open(filename, 'r') as html_file:
        logger.info('Reading [%s]' % filename)
        html_source = html_file.read()
    #df = pd.read_html(filename);
    bs = BeautifulSoup(html_source, 'html.parser')
    a_list = bs.findAll('a')
    logger.debug(a_list)

    for a in a_list:
        logger.debug(a)
        pattern = '../../citizen_html/panchregpeople.aspx?panchayat_code='
        code_index = len(pattern)
        anchor = str(a)
        if pattern in anchor:
            panchayat_name = a.text.strip()
            filename = dirname + panchayat_name + '.html'
            logger.info('Panchayat [%s]' % panchayat_name)
            panchayat_code = anchor[anchor.find(pattern)+code_index:anchor.find('&amp;')]
            panchayat_url = 'http://mnregaweb4.nic.in/netnrega/writereaddata/citizen_out/panchregpeople_%s_eng1819.html' % panchayat_code
            logger.info('Fetching [%s]' % panchayat_url)

            try:
                df = pd.read_html(panchayat_url)[3]
            except Exception as e:
                logger.error('Exception when reading HTML[%s]' % e)
                exit(0)
            logger.info(str(df.head()))
            logger.info('Dumping [%s]' % filename)
            df.to_html(filename)
            filename = filename.replace('.html', '.csv')
            logger.info('Exporting [%s]' % filename)
            df.to_csv(filename, index=False)

            
def fetchAppRegister(logger, dirname=None):
    create_dir(dirname)
    fetchBlockData(logger, dirname, 'Munagapaka')
    fetchBlockData(logger, dirname, 'Gangaraju Madugula')

    return 'SUCCESS'

def processAppRegister(logger, dirname=None):
    if not dirname:
        dirname = './Data/'
    create_dir(dirname)

    logger.info('Process HTMLs in [%s]' % dirname)
    
    count = 0
    for basename in os.listdir(dirname):
        filename=os.path.join(dirname,basename)
        logger.info('Reading [%s]' % filename)
        if 'sample' not in filename:
            logger.info('Skipping [%s]' % filename)
            continue
        try:
            df = pd.read_csv(filename, encoding='utf-8-sig')
        except Exception as e:
            logger.error('Exception when reading filename[%s] - EXCEPT[%s:%s]' % (filename, type(e), e))

        df_array = []
        sorted = df.sort_values(by='WorkerID')
        sorted['WorkerID'].to_csv(filename.replace('list', 'workers'), index=False)
        df_array.append(sorted['WorkerID'])
        
        sorted = df.sort_values(by='जॉब कार्ड')
        sorted['जॉब कार्ड'].drop_duplicates().to_csv(filename.replace('list', 'jobcards'), index=False)
        df_array.append(sorted['जॉब कार्ड'].drop_duplicates())

        sorted = df.sort_values(by='गांव')                               
        sorted['गांव'].drop_duplicates().to_csv(filename.replace('list', 'villages'), index=False)
        df_array.append(sorted['गांव'].drop_duplicates())
        
        concat = pd.concat(df_array)
        logger.info('Concatenated: \n%s' % concat.head())
        concat.to_csv(filename.replace('list', 'all'), index=False)
    
    return 'SUCCESS'


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = loggerFetch('info')
        self.logger.info('BEGIN PROCESSING...')

    def tearDown(self):
        self.logger.info('...END PROCESSING')

    def test_fetchAppRegister(self):
        dirname = './Data/'
        result = fetchAppRegister(self.logger, dirname=dirname)
        self.assertEqual(result, 'SUCCESS')
        
    def test_parseAppRegister(self):
        dirname = './Data/'
        result = parseAppRegister(self.logger, dirname=dirname)
        self.assertEqual(result, 'SUCCESS')
        
if __name__ == '__main__':
    unittest.main()
    
