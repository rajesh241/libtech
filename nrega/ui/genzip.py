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
sys.path.insert(0, fileDir+'/../scripts/')
from globalSettings import datadir,nregaDataDir,reportsDir,nregaDir,nregaArchiveDir
from crawlFunctions import getDistrictParams
#sys.path.insert(0, rootdir)

from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from libtechFunctions import singleRowQuery,writecsv,getFullFinYear
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIQuery2HTML
from crawlFunctions import getDistrictParams


def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='HouseKeeping Script for SurGUJA Database')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-d', '--district', help='Please enter the district', required=True)
  parser.add_argument('-limit', '--limit', help='Limit the number of entries that need to be processed', required=False)

  args = vars(parser.parse_args())
  return args


 
def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  if args['district']:
    districtName=args['district'].lower()
  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString="  "
  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)
 
  query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1 %s" % limitString
  #query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1 limit 1"
  cur.execute(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    panchayatName=row[2]
    panchayatCode=row[3]
    logger.info(blockName+"  "+panchayatName) 
    fileList=''
    fileList+=" %s/%s.html " %(districtName.upper(),districtName.upper())
    fileList+=" %s/css/* " %(districtName.upper())
    fileList+=" %s/%s/%s.html " %(districtName.upper(),blockName.upper(),blockName.upper())
    fileList+=" %s/%s/%s/%s.html " %(districtName.upper(),blockName.upper(),panchayatName.upper(),panchayatName.upper())
    fileList+=" %s/%s/%s/* " %(districtName.upper(),blockName.upper(),panchayatName.upper())
    fileList+=" %s/%s/FTO/* " %(districtName.upper(),blockName.upper())
    zipFileDir="%s/%s/%s/" %(nregaArchiveDir,districtName.upper(),blockName.upper())
    zipname="%s/%s.zip" % (zipFileDir,panchayatName.upper())
    mkdircmd="mkdir -p %s " %(zipFileDir)
    logger.info(mkdircmd)
    os.system(mkdircmd)
    cdcmd="cd %s " % (nregaDir)
    logger.info(cdcmd)
    os.system(cdcmd)
    os.chdir(nregaDir)
    zipcmd="zip -r %s %s " %(zipname,fileList)     
    logger.info(zipcmd)
    os.system(zipcmd)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()




#Files that need to be zipped


#districtName.html
#blockName.html

