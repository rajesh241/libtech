from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import time
import re
import sys
from MySQLdb import OperationalError
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../includes/')
sys.path.insert(0, fileDir+'/../')
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery
from globalSettings import datadir,nregaDataDir
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Populate Pds SHop codes from csv File')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-f', '--filename', help='Input csv name', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db="biharPDS", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  infilename=args['filename']
  
  logger.info(infilename)

  f = open(infilename, 'r') #This is the inpur filename (which contains FPS list)
  for eachline in f:
    strline = eachline.rstrip()
    strList = strline.split(',')
    print strList
    if (len(strList) == 6) and ("-Select-" not in strline):
      distVal = strList[0]
      blockVal = strList[2]
      fpsVal = strList[4]
      logger.info("Now Doing: " + distVal + ":" + blockVal + ":" + fpsVal)
      
      distName = strList[1]
      blockName = strList[3]
      fpsName1 = strList[5].replace("'","")
      fpsName2 = fpsName1.replace(" ", "_")
      fpsName3 = fpsName2.replace("/", "")
      fpsName = fpsName3.replace(".", "")

      query="select * from pdsShops where fpsCode='%s' " % (fpsVal)
      cur.execute(query)
      if cur.rowcount == 0:
        query="insert into pdsShops (fpsCode) values ('%s') " % (fpsVal)
        cur.execute(query)
      query="update pdsShops set distCode='%s',blockCode='%s',distName='%s',blockName='%s',fpsName='%s' where fpsCode='%s' " % (distVal,blockVal,distName,blockName,fpsName,fpsVal)
      logger.info(query) 
      cur.execute(query)


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors


  
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
