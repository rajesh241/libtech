import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import time
import re
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
from libtechFunctions import singleRowQuery,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from crawlSettings import nregaDB 
def updatePanchayatStats(cur,logger):
  logger.info("Update Panchayat Status")
  query="select fullPanchayatCode from panchayats where isRequired=1"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [fullPanchayatCode]=row
    query="select count(*) from jobcards where fullPanchayatCode='%s' " % fullPanchayatCode
    logger.info(query)
    cur.execute(query)
    row1=cur.fetchone()
    totalJobcards=row1[0]
    query="update panchayatStatus set totalJobcards=%s where fullPanchayatCode='%s' " % (str(totalJobcards),fullPanchayatCode)
    logger.info(query)
    cur.execute(query)

def selectRandomDistricts(cur,logger):
  logger.info("Selecting Random Districts")
  query="select count(*),stateName from districts group by stateName"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [count,stateName]=row
    if count <=5 :
      query="update districts set jRequired=1 where stateName='%s' " % (stateName)
      cur.execute(query)
    else:
      query="select id from districts where stateName='%s' order by RAND() limit 5" % (stateName)
      cur.execute(query)
      results1=cur.fetchall()
      for row1 in results1:
        rowid=str(row1[0])
        query="update districts set jRequired=1 where id=%s " %str(rowid)
        cur.execute(query)
 
def updateMusterStats(cur,logger):
  logger.info("Updating Muster Statistics")
  query="select id,fullBlockCode,musterNo,finyear from musters where wdProcessed=1 "
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    [rowid,fullBlockCode,musterNo,finyear] = row
    query="select count(*) from workDetails where finyear='%s' and fullBlockCode='%s' and musterNo='%s' " % (finyear,fullBlockCode,musterNo)
    cur.execute(query)
    row1=cur.fetchone()
    totalCount=row1[0] 
    query="select count(*) from workDetails where musterStatus!='Credited' and finyear='%s' and fullBlockCode='%s' and musterNo='%s' " % (finyear,fullBlockCode,musterNo)
    cur.execute(query) 
    row1=cur.fetchone()
    totalPending=row1[0] 
    totalSuccess=totalCount-totalPending
    logger.info("musterid : %s totalSuccess:%s totalCount:%s totalPending:%s " % (str(rowid),str(totalSuccess),str(totalCount),str(totalPending)))
    query="update musters set totalCount=%s,totalSuccess=%s,totalPending=%s where id=%s " % (str(totalCount),str(totalSuccess),str(totalPending),str(rowid))
    cur.execute(query)
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-ums', '--updateMusterStats', help='update Statistics in Muster Table', required=False,action='store_const', const=1)
  parser.add_argument('-srd', '--selectRandomDistricts', help='Select Random Districts', required=False,action='store_const', const=1)
  parser.add_argument('-ups', '--updatePanchayatStats', help='update Panchayat Status', required=False,action='store_const', const=1)
  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  
  if args['updateMusterStats']:
    updateMusterStats(cur,logger) 
  if args['selectRandomDistricts']:
    selectRandomDistricts(cur,logger)
  if args['updatePanchayatStats']:
    updatePanchayatStats(cur,logger)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
