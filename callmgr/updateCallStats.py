from bs4 import BeautifulSoup
import math
import time
import os
dirname = os.path.dirname(os.path.realpath(__file__))
rootdir = os.path.dirname(dirname)

import sys
sys.path.insert(0, rootdir)
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')

from libtechFunctions import singleRowQuery

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize
from wrappers.db import dbInitialize,dbFinalize
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for updaing success Percentage')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  
  query="select id,phone from addressbook "
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    phone=row[1]
    logger.info("ID  %s  Phone %s " % (rowid,phone)) 
    query="select count(*) from callLogs where phone='%s'" % (phone)
    totalCalls=singleRowQuery(cur,query)
    query="select count(*) from callLogs where phone='%s' and status='pass'" % (phone)
    totalSuccessCalls=singleRowQuery(cur,query)
    if totalCalls > 0:
      logger.info("Calculating Percentage")
      successP=math.trunc(totalSuccessCalls*100/totalCalls)
    else:
      successP=0
    logger.info("Total Calls %s Success Calls %s Success Percentage %s " % (str(totalCalls),str(totalSuccessCalls),str(successP)))
    query="update addressbook set totalCalls='%s',successPercentage='%s'  where id=%s " % (str(totalCalls),str(successP),rowid) 
    cur.execute(query)

if __name__ == '__main__':
  main()
