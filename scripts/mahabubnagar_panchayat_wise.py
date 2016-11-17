#! /usr/bin/env python


import unittest
import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.db import dbInitialize,dbFinalize
from wrappers.logger import loggerFetch


#######################
# Global Declarations
#######################

filename = 'panchayats.csv'


#############
# Functions
#############

def dump_csv(logger, db):
    for i in range(1, 25):
        panchayat_code = ("%03d" % i) 
        logger.info("Dumping for Panchayat [%s]" % panchayat_code)

        # Making a file for each panchayat and then cat the /tmp/file_*.csv into one file
        query = '''select * from musterTransactionDetails where blockCode='057' and finyear='17' and panchayatCode='%s' into outfile '/tmp/file_%s.csv' FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n';''' % (panchayat_code, panchayat_code)

        logger.info("Query for Panchayat [%s] is [%s]" % (panchayat_code, query))

        cur = db.cursor()
        cur.execute(query)

        # If the above does not work then there is the option of running on os.system(cmd) cmd = mysql --host=dbserver --user=dbadmin --password=sharedata mahabubnagar -e "select * from musterTransactionDetails where blockCode='057' and finyear='17' and panchayatCode='001' INTO OUTFILE  '/tmp/filename.csv'  FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n'"

    return 'SUCCESS'


#############
# Tests
#############


class TestSuite(unittest.TestCase):
  def setUp(self):
    self.logger = loggerFetch('info')
    self.db = dbInitialize(db="mahabubnagar")
    self.logger.info('BEGIN PROCESSING...')

  def tearDown(self):
    dbFinalize(self.db)
    self.logger.info("...END PROCESSING")
    
  def test_fetch(self):
    result = dump_csv(self.logger, self.db)
    
    self.assertEqual('SUCCESS', result)


if __name__ == '__main__':
  unittest.main()



