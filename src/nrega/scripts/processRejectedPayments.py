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
from libtechFunctions import singleRowQuery,getjcNumber
from globalSettings import nregaDir,datadir,nregaDataDir
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable

from crawlFunctions import getDistrictParams
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script to Populate workDetail Table')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)
  parser.add_argument('-s', '--stateName', help='District for which you need to Download', required=True)
  args = vars(parser.parse_args())
  return args
  
 
def main():
  regex=re.compile(r'</td></font></td>',re.DOTALL)
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  
  limitSetting=''
  stateName=args['stateName'] 
  db = dbInitialize(db=stateName,charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  htmlDir='/home/libtech/gDrive/test/rejectedPayments'
  
  query="select id,districtCode,stateCode from districts"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    districtCode=row[1]
    stateCode=row[2]
    logger.info(rowid+"   "+districtCode)
    filename="%s/%s.html" % (htmlDir,stateCode+districtCode)
    logger.info(filename)
    f=open(filename,"r")
    myhtml=f.read()
    htmlsoup=BeautifulSoup(myhtml,"html.parser")
    errorflag=0
    try:
      table=htmlsoup.find('table',id="ctl00_ContentPlaceHolder1_grdShowRecords")
      rows = table.findAll('tr')
      logger.info("Found the Table")
    except:
      errorflag=1 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
