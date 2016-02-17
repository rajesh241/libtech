from bs4 import BeautifulSoup
import datetime
import os
import requests
import xml.etree.ElementTree as ET
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from settings import sid,token
from globalSettings import maxTringoCallQueue,maxExotelCallQueue
from broadcastFunctions import scheduleGeneralBroadcastCall      

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Parsing Script for Testing Calls')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-bid', '--bid', help='BID of Broadcast', required=True)
  parser.add_argument('-phone', '--phone', help='Phone Number', required=True)

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
  bid=args['bid']
  phone=args['phone']

  logger.info("BID %s phone %s " % (str(bid),str(phone)))
  vendor='exotel'

  scheduleGeneralBroadcastCall(cur,bid,phone,vendor,1)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


if __name__ == '__main__':
  main()
