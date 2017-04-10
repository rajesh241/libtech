#! /usr/bin/env python

from bs4 import BeautifulSoup
from time import strftime,strptime
from MySQLdb import IntegrityError

import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)

import csv

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize
from wrappers.db import dbInitialize,dbFinalize


#######################
# Global Declarations
#######################

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)
  parser.add_argument('-c', '--csv', help='CSV file to push into DB', required=False)
  parser.add_argument('-q', '--query', help='Query to specify the workset, E.g ... where id=147', required=False)


  args = vars(parser.parse_args())
  return args

def insertRow(logger, db, jobcard, name, phone, sssGroup, village, habitat):
  cur = db.cursor()

  query = 'insert into mateInfo (jobcard, name, phone, sssGroup, village, habitat) values ("%s", "%s", "%s", "%s", "%s", "%s")' % (jobcard, name, phone, sssGroup, village, habitat)
  logger.info('query[%s]' % query)
  cur.execute(query)

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")

  db = dbInitialize(db="mahabubnagar")
  
  csv_file = args['csv']
  logger.info("csv_file [%s]" % csv_file)
  csv_data = csv.reader(file(csv_file))
#  print csv_data
  for row in csv_data:
    (village, habitat, sssGroup, jobcard, name, phone) = row
    insertRow(logger, db, jobcard, name, phone, sssGroup, village, habitat)

  dbFinalize(db)


  logger.info("...END PROCESSING")


  exit(0)

if __name__ == '__main__':
  main()
