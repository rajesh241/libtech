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
from libtechFunctions import singleRowQuery,getFullFinYear,writeFile
from globalSettings import nregaDir,nregaRawDir
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from crawlFunctions import alterMusterHTML,getMusterPaymentDate
from crawlFunctions import getDistrictParams
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-s', '--stateName', help='District for which you need to Download', required=True)
  parser.add_argument('-b', '--blockCode', help='BlockCode for  which you need to Download', required=False)
  parser.add_argument('-p', '--panchayatCode', help='panchayatCode for  which you need to Download', required=False)
  parser.add_argument('-limit', '--limit', help='District for which you need to Download', required=False)

  args = vars(parser.parse_args())
  return args


def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  #This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)
  regex1=re.compile(r'</td></font></td>',re.DOTALL)
  stateName=args['stateName']
  finyear=args['finyear']
  fullFinYear=getFullFinYear(finyear)

  db = dbInitialize(db=stateName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString=" limit 10000 "
  filepath="/home/libtech/gDrive/rejectedPayments/" 
  logger.info("stateNme  "+stateName)
  logger.info("Fin year "+fullFinYear)
  query="select id,name,districtCode,stateCode from districts where isDownloaded=0"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    rowid=str(row[0])
    districtName=row[1]
    districtCode=row[3]+row[2]
    url="http://164.100.129.4/netnrega/FTO/rejection.aspx?lflag=local&page=s&state_code=33&fin_year=fullFinYear&state_name=CHHATTISGARH&district_code=districtCode&district_name=districtName&typ=R&linkr=X"
    url=url.replace("fullFinYear",fullFinYear)
    url=url.replace("districtName",districtName)
    url=url.replace("districtCode",districtCode)
    logger.info(url)
    r=requests.get(url)
    time.sleep(600)
    myhtml=r.text
    if "Data not loaded" in myhtml:
      logger.info("Not Downloaded")
    else:
      filename="%s_rejected.html" % districtName
      #writeFile(myhtml,'/tmp/%s.html' % districtCode)
      filename="/home/libtech/%s.html" % districtCode
      f=open(filename,"w")
      f.write(myhtml.encode("UTF-8"))
      query="update districts set isDownloaded=1 where id=%s " % (rowid)
      cur.execute(query) 
  
 
 
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
