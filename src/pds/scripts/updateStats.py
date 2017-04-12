import os
import time
import re
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../nrega/crawl/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from crawlFunctions import alterHTMLTables
from pdsFunctions import cleanFPSName,writeFile
from globalSettings import datadir,nregaDataDir
from pdsSettings import pdsDB,pdsDBHost,pdsRawDataDir,pdsWebDirRoot
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate Pds SHop codes from csv File')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  db1 = dbInitialize(db='libtech', charset="utf8")  # The rest is updated automatically in the function
  cur1=db1.cursor()
  db1.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur1.execute(query)
  db = dbInitialize(db=pdsDB, host=pdsDBHost,charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  query="select id,fpsCode from fpsShops where districtCode!='1001' and isRequired=1"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    fpsCode=row[1]
    logger.info("%s - %s " % (rowid,fpsCode))
    query="select count(*) from pdsPhoneBook where fpsCode='%s' " % fpsCode
    cur1.execute(query)
    rowCount=cur1.fetchone()
    count=str(rowCount[0])
    query="update fpsShops set totalNumbers=%s where id=%s " % (count,rowid)
    cur.execute(query)
    logger.info("%s - %s - %s " % (rowid,fpsCode,count))
    
     
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  dbFinalize(db1) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
