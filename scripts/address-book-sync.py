from __future__ import print_function
import httplib2
import os
import unittest

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from time import strftime

from wrappers.db import dbInitialize, dbFinalize
from wrappers.logger import loggerFetch

#######################
# Global Declarations
#######################

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


#############
# Functions
#############

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def pull_from_google_sheet(logger, db, region, spreadsheet_id=None, range_name=None):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """

    if not spreadsheet_id:
        spreadsheet_id = '13NWtMv211Yf3tSIzS9LoDmrar93NgwDaBA8LUvdE3Ec'

    if not range_name:
        range_name = 'Sheet1!A:J'

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    logger.debug(values)

# Mynk    master_query = 'select * from addressbook where region="%s"' % region
    
    if not values:
        logger.info('No data found.')
    else:
        # See the column names below for reference
        logger.debug('phone, name, district, block, panchayat, designation, gender, total_calls, success_percentage, updated')
        for row in values:
            ncols = len(row)
            logger.debug("RowCount[%d]" % ncols)
            logger.debug(row)

            if row[0] == 'phone':
                row.append('updated')
                continue
            else:
                while ncols < 10:
                    row.append('')
                    ncols += 1
            logger.debug(row)

            (phone, name, district, block, panchayat, designation, gender, total_calls, success_percentage, timestamp) = row

            # Print columns A thru J as desired
            # logger.info('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
            logger.info('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % (phone, name, district, block, panchayat, designation, gender, total_calls, success_percentage, timestamp))
            phone='9845155447'
            query = 'select totalCalls, successPercentage from addressbook where region="%s" and phone="%s"' % (region, phone)
            cur = db.cursor()
            logger.info('Executing query[%s]' % query)
            cur.execute(query)
            res = cur.fetchall()
            logger.info(res)
            timestamp = strftime('%Y-%m-%d %H:%M:%S')
            if res:
                # Update (totalCalls, successPercentage) = res[0]
                (row[7], row[8]) = res[0]
                
                # Add timestamp to the excel
                row[9] = timestamp 
                print(row)
                query = 'update addressbook set name="%s", district="%s", block="%s", panchayat="%s", designation="%s", gender="%s", ts="%s" where phone="%s"' % (name, district, block, panchayat, designation, gender, timestamp, phone)
                print(query)
            else:                
                query = 'insert into addressbook (phone, name, district, block, panchayat, designation , gender, ts) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (phone, name, district, block, panchayat, designation, gender, timestamp)
                print(query)

#          query = 'insert into jobcardDetails (jobcard, applicantNo, age, applicantName, gender, accountNo, aadharNo, bankNameOrPOName, IFSCCodeOrEMOCode, branchNameOrPOAddress, isDisabled) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (jobcard, worker_id, age, worker_name, gender, account_no, uid_no, paying_agency, ifsc_code, branch, is_disabled) + ' ON DUPLICATE KEY update jobcard="%s", applicantNo="%s", age="%s", applicantName="%s", gender="%s", accountNo="%s", aadharNo="%s", bankNameOrPOName="%s", IFSCCodeOrEMOCode="%s", branchNameOrPOAddress="%s", isDisabled="%s"' % (jobcard, worker_id, age, worker_name, gender, account_no, uid_no, paying_agency, ifsc_code, branch, is_disabled)



            return 0

        #logger.info(values)


    return 'SUCCESS'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    logger.debug(values)



#############
# Tests
#############


class TestSuite(unittest.TestCase):
  def setUp(self):
    self.logger = loggerFetch('info')
    self.db = dbInitialize(host='localhost', user='libtech', passwd='lt123', db='libtech')
    self.logger.info('BEGIN PROCESSING...')

  def tearDown(self):
    dbFinalize(self.db)
    self.logger.info('...END PROCESSING')
    
  def test_fetch(self):
    result = pull_from_google_sheet(self.logger, self.db, 'rscd')
    
    self.assertEqual('SUCCESS', result)


if __name__ == '__main__':
  unittest.main()

