import csv
import time
from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import sys
import importlib
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
from nregaSettings import nregaRawDataDir
from libtechFunctions import writeFile,getFullFinYear,singleRowQuery
#Connect to MySQL Database
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from crawlFunctions import alterFTOHTML
from crawlFunctions import getDistrictParams
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for Downloading FTOs')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of ftos to be downloaded', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")

  limitString=''
  if args['limit']:
    limitString=' limit '+args['limit']
  if args['district']:
    districtName=args['district']
 
  logger.info("DistrictName "+districtName)
  finyear=args['finyear']
  
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  logger.info("finyear "+finyear)
  fullFinYear=getFullFinYear(finyear) 
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
#Query to get all the blocks



  ftorawfilepath=nregaRawDataDir.replace("districtName",districtName.lower())
  query="select id,blockCode,name from blocks order by rejectedPaymentDownloadDate DESC"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    blockCode=row[1]
    blockName=row[2]
    fullBlockCode=stateCode+districtCode+blockCode
    fullDistrictCode=stateCode+districtCode
    url="http://164.100.129.4/netnrega/FTO/rejection.aspx?lflag=eng&state_code=%s&state_name=%s&district_code=%s&page=d&Block_code=%s&Block_name=%s&district_name=%s&fin_year=%s&typ=I&linkr=X"  % (stateCode,stateName.upper(),fullDistrictCode,fullBlockCode,blockName.upper(),districtName.upper(),fullFinYear)
    logger.info(url)
    r=requests.get(url)
    time.sleep(300)
    inhtml=r.text
    ftorawfilename=ftorawfilepath+blockName.upper()+"/FTO/"+fullFinYear+"/rejected.html"
    writeFile(ftorawfilename,inhtml)
    query="update blocks set rejectedPaymentDownloadDate=NOW() where id=%s" % rowid
    logger.info(query)
    cur.execute(query)


  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
