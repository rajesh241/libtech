import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)
print('RootDir[%s]' % rootdir)

import sys
sys.path.insert(0, rootdir)

repodir = os.path.dirname(rootdir)

djangodir = repodir + '/django/n.libtech.info/src'
print(djangodir)
sys.path.append(djangodir)

import requests
import unittest
from bs4 import BeautifulSoup

import pandas as pd

from wrappers.logger import loggerFetch

###

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libtech.settings')

import django

# This is so Django knows where to find stuff.
# This is so my local_settings.py gets loaded.
django.setup()

from nrega.models import State,District,Block,Panchayat,PaymentInfo,LibtechTag,CrawlQueue,Worker,Jobcard


#######################
# Global Declarations
#######################

#timeout = 10
column_names = ['S.No.', 'Head of HouseHold', 'Caste', 'IAY/LR Beneficiary', 'Name of Applicant', 'Father/Husband Name', 'Gender', 'Age', 'Date of receipt of application/<br>Request for Registration', 'No.).Append(Date of Job Card issued', 'Reasons, if Job Card NOT issued<br>&amp; any other remarks', 'Disabled', 'Minority', 'Job Card Verified on Date']

skip_columns = ['S.No.', 'Caste', 'IAY/LR Beneficiary', 'Age', 'Date of receipt of application/<br>Request for Registration', 'Reasons, if Job Card NOT issued<br>&amp; any other remarks', 'Disabled', 'Minority']
#column_names = ['S.No.', 'Head of HouseHold', 'Caste', 'IAY/LR Beneficiary', 'Name of Applicant', 'Father/Husband Name', 'Gender', 'Age', 'Date of receipt of application/<br>Request for Registration', 'No.).Append(Date of Job Card issued', 'Reason: Wants to surrender the Job-Card', 'Disabled', 'Minority', 'Job Card Verified on Date']

surrender_reason = 'Reason: Wants to surrender the Job-Card'
serial_no = 'S.No.'

#############
# Functions
#############

def create_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != os.errno.EEXIST:
            raise

def fetchBlockData(logger, dirname, block_name=None, url=None):
    filename = '%s.html' % block_name

    if not url:
        try:
            logger.info('Fetching URL[%s]' % url)
            response = requests.get(url)
        except Exception as e:
            logger.error('Caught Exception[%s]' % e)
        html_source = response.text
    else:
        with open(filename, 'r') as html_file:
            logger.info('Reading [%s]' % filename)
            html_source = html_file.read()

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

def getJobcard(row):
    #print('Row[%s]' % row)
    #print(row[9])
    jobcard = row[9].replace(row[8], '')
    print(jobcard)
    tjobcard = jobcard.replace('AP-03-011-0', '0302911').replace('/', '').replace('-', '')
    print(tjobcard)
    jobcard = Jobcard.objects.filter(jobcard=jobcard)
    if jobcard:
        print('Yippie!')
        print('query[%s]' % str(jobcard))
        print('Jobcard[%s] tjobcard[%s] village[%s]' % (jobcard, jobcard.tjobcard, jobcard.village.name))
        return (jobcard.tjobcard) # , jobcard.village.name)
    else:
        return tjobcard
            
def stripReason(row):
    #print('Row[%s]' % row)
    reason = row[10].strip(surrender_reason)
    #print(reason)
    return reason

def fetchAppRegister(logger, dirname=None):
    create_dir(dirname)
    fetchBlockData(logger, dirname, block_name='Munagapaka')
    fetchBlockData(logger, dirname, block_name='Gangaraju Madugula')
    
    #fetchBlockData(logger, dirname, url='')

    return 'SUCCESS'

def parseAppRegister(logger, dirname=None, block_code=None):
    if not dirname:
        dirname = './Data/'

    if not block_code:
        block_code='0203034'

    logger.info('Process HTMLs in [%s]' % dirname)

    panchayats = Panchayat.objects.filter(block__code=block_code)
    logger.info('Panchayats[%s]' % str(panchayats))

    files = os.listdir(dirname)
    logger.info('Files[%s]' % files)
    '''
    #count = 0
    for basename in os.listdir(dirname):
        filename=os.path.join(dirname,basename)
        logger.info('Reading [%s]' % filename)
        if '.csv' not in filename:
            logger.info('Skipping [%s]' % filename)
            continue

        if filename.replace('.csv', '') not in panchayats:
            logger.info('Oops [%s]' % filename)
            continue
    '''

    for panchayat in panchayats:
        panchayat_name = panchayat.name
        logger.info('Panchayat[%s]' % panchayat_name)
        if (panchayat_name + '.csv' not in files):
            logger.info('Not interested in [%s]' % panchayat_name)
            continue

        filename = dirname + panchayat_name + '.csv'
        logger.info('Filename[%s]' % filename)

        try:
            df = pd.read_csv(filename, encoding='utf-8-sig', header = None, names = column_names)
        except Exception as e:
            logger.error('Exception when reading filename[%s] - EXCEPT[%s:%s]' % (filename, type(e), e))

        print(df.head())

        df.fillna('', inplace=True)
        print(df.head())

        print('Columns[%s]' % df.columns)
        df = df.loc[df[df.columns[10]].str.contains(surrender_reason)]
        print('DF[%s]' % df.head())

        if False:
            logger.info('Panchayat ID[%s]' % panchayat.id)
            jobcards = Jobcard.objects.filter(panchayat_id=panchayat.id)[:5]
            logger.info('Jobcards[%s]' % jobcards)
            jobcard = Jobcard.objects.filter(jobcard='AP-03-020-031-035/010001')[0]
            logger.info('query[%s]' % str(jobcard))
            logger.info('Jobcard[%s] tjobcard[%s] village[%s]' % (jobcard, jobcard.tjobcard, jobcard.village.name))
        df[surrender_reason] = df.apply(lambda row: stripReason(row), axis=1)
        df['tjobcard'] = df.apply(lambda row: getJobcard(row), axis=1)
        print(df.head())

        if False:
            df.drop([df.columns[2]], axis = 1, inplace = True)
            df.drop([df.columns[2]], axis = 1, inplace = True)
            df.drop([df.columns[5]], axis = 1, inplace = True)
            df.drop([df.columns[5]], axis = 1, inplace = True)
            df.drop([df.columns[7]], axis = 1, inplace = True)
            df.drop([df.columns[7]], axis = 1, inplace = True)
        else:
            df.drop(skip_columns, axis = 1, inplace = True)
        
                
        print(df.head())
        if False:
            df.reset_index()
            df.columns[0] = serial_no
            df[serial_no] = df.index
        else:
            df.insert(0, serial_no, range(1, len(df)+1))

        print(df.head())
        exit(0)
        logger.info('Writing to [%s]' % filename)
        df.to_csv(filename, index=False)
        continue
        for worker in workers:
            jobcard_no = (worker.jobcard.tjobcard + '-0' + str(worker.applicantNo))
            if current_panchayat and (panchayat_name == current_panchayat and is_downloaded and (jobcard_no != current_jobcard)): 
                logger.debug('Skipping[%s]' % jobcard_no)
                continue            
            is_downloaded = False
            logger.info('Fetch details for jobcard_no[%s]' % jobcard_no)

            exit(0)

        exit(0)

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
        result = parseAppRegister(self.logger, dirname=dirname, block_code='0203011')
        self.assertEqual(result, 'SUCCESS')
        
if __name__ == '__main__':
    unittest.main()
    
