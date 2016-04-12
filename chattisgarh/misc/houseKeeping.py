from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from globalSettings import datadir,nregaDataDir
def copyPhones(cur,logger):
  logger.info("Copy Start")
  query="use libtech"
  cur.execute(query)
  query="select jobcard,phone from jobcardPhone where jobcard like '%CH-05-%'" 
  cur.execute(query)
  results = cur.fetchall()
  query="use surguja"
  cur.execute(query)
  query="update jobcardRegister set phone='' "
  cur.execute(query)
  for row in results:
    jobcard=row[0]
    phone=row[1]
    logger.info(jobcard+phone)
    query="update jobcardRegister set phone='%s' where jobcard='%s' " % (phone,jobcard)
    cur.execute(query)

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='HouseKeeping Script for SurGUJA Database')
  parser.add_argument('-cp', '--copyPhones', help='Copies the phones from Libtech Addressbook to Surguja JobCardRegister', required=False,action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-district', '--district', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

  if args['copyPhones']:
    logger.info("Copying Phones from libtech to Surguja Database")
    copyPhones(cur,logger)

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
