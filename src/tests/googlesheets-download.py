from bs4 import BeautifulSoup

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize


#######################
# Global Declarations
#######################

timeout = 20

versions = [ 1, 202, 203, 205, 206, 213, 223, 233, 270, 272, 287, 302, 361, 388, 391, 407, 420, 423, 462, 475, 523, 531, 558, 624, 625,
            626, 649, 668, 682, 714, 728, 743, 762, 777, 808, 816, 840, 868, 873, 880, 935, 943, 958, 975, 996,
]

sheet_id = '1UGtgX1goSh-VDY2Sqp0NH5kkxaxgm4IO-3zu9WROnuI'

csv_file='V1.4 Telugu Household Questionnaire, 2017 (Responses) - Form Responses 1.csv'

###

versions = [1, 129, 142, 158, 187, 212, 216, 229, 255, 257, 314, 326, 371, 405, 496, 517, 538, 551, 597, 625, 653, 703, 732, 829, 929, 983, 984, 989, 1051, 1059, 1060, 1076, 1092, 1128, 1130, 1317, 1430 ]

sheet_id = '1v_zYtjWeyFv2q9bz_LZIxXwx8lNzETmJ9rNZhEdDIgU'

csv_file='V1.6.3 Q5 Loop Telugu Household Questionnaire, 2017 (Responses) - Form Responses 1.csv'

###

url_base = "https://docs.google.com/spreadsheets/d/%s/export?format=csv&revision=" % sheet_id

#############
# Functions
#############

def runTestSuite():
  logger = loggerFetch("info")
  logger.info("BEGIN PROCESSING...")

  display = displayInitialize(1)
  driver = driverInitialize(path='/home/mayank/.mozilla/firefox/4s3bttuq.default/', timeout=timeout)

  driver.set_page_load_timeout(timeout)

  for version in versions:
    url = url_base + str(version)
    try:
      logger.info('Fetching URL[%s]' % url)
      driver.get(url)
      logger.info('After Fetch[%s]' % url)      
    except Exception as e:
      logger.info("Warning %s", e)
      if os.path.exists(csv_file):
        version_file = 'CSVs/' + str(version) + '.csv'
        logger.info('Writing %s' % version_file)
        os.rename(csv_file, version_file)
      else:
        logger.error('Missed file[%s] from URL[%s]' % (version_file, url))
    logger.info("CSV Fetched From [%s]" % url)

  driverFinalize(driver)
  displayFinalize(display)


  logger.info("...END PROCESSING")     


def main():
  runTestSuite()
  exit(0)

if __name__ == '__main__':
  main()
