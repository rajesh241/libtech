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
from globalSettings import nregaDir
sys.path.insert(0, fileDir+'/../crawlDistricts/')
from bootstrap_utils import bsQuery2Html, bsQuery2HtmlV2,htmlWrapperLocal, getForm, getButton, getButtonV2,getCenterAligned,tabletUIQueryToHTMLTable,tabletUIReportTable
from crawlFunctions import getDistrictParams,alterMISHTML
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-f', '--finyear', help='Download musters for that finyear', required=True)
  parser.add_argument('-d', '--district', help='District for which you need to Download', required=True)
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
  districtName=args['district']

  db = dbInitialize(db=districtName.lower(), charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  crawlIP,stateName,stateCode,stateShortCode,districtCode=getDistrictParams(cur,districtName)

  if args['limit']:
    limitString=" limit %s " % (str(args['limit']))
  else:
    limitString=" limit 10000 "
  additionalFilters = ''
  if args['blockCode']:
    additionalFilters=" and b.blockCode='%s' " % args['blockCode']
  if args['panchayatCode']:
    additionalFilters+=" and m.panchayatCode like '%"+args['panchayatCode']+"%' " 
  infinyear=args['finyear']
 
  logger.info("DistrictName "+districtName)
  logger.info("Fin year "+infinyear)

#Query to get all the blocks
  logger.info("crawlIP "+crawlIP)
  logger.info("State Name "+stateName)
  query="use %s" % districtName.lower()
  cur.execute(query)
  fullfinyear=getFullFinYear(infinyear)
  baseDir="/home/libtech/media/work/surgujaMIS/"
  query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isRequired=1 %s " % (limitString)
  query="select b.name,b.blockCode,p.name,p.panchayatCode from panchayats p, blocks b where b.blockCode=p.blockCode and p.isSurvey=1 %s %s " % (additionalFilters,limitString)
  cur.execute(query)
  logger.info(query)
  results=cur.fetchall()
  for row in results:
    blockName=row[0]
    blockCode=row[1]
    panchayatName=row[2]
    panchayatCode=row[3]
    fullPanchayatCode=stateCode+districtCode+blockCode+panchayatCode
    fullBlockCode=stateCode+districtCode+blockCode
    fullDistrictCode=stateCode+districtCode
    curhtmlfile=baseDir+districtName.upper()+"/"+blockName.upper()+"/"+fullfinyear+"/"+panchayatName.upper()+"_14_1.html"
    curcsvfile=baseDir+districtName.upper()+"/"+blockName.upper()+"/"+fullfinyear+"/"+panchayatName.upper()+"_14_1.csv"
    logger.info(blockName+blockCode+panchayatName+panchayatCode)
    url="http://%s/netnrega/state_html/delay_comp_dtl.aspx?page=p&state_name=%s&state_code=%s&fin_year=%s&district_name=%s&district_code=%s&block_name=%s&block_code=%s&panchayat_name=%s&panchayat_code=%s&source=national"  % (crawlIP,stateName.upper(),stateCode,fullfinyear,districtName.upper(),fullDistrictCode,blockName.upper(),fullBlockCode,panchayatName.upper(),fullPanchayatCode)
    logger.info(url)
    r=requests.get(url)
    myhtml=r.text
    myhtml=myhtml.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    errorflag,outcsv=alterMISHTML(myhtml)
    writeFile(curhtmlfile,myhtml)
    writeFile(curcsvfile,outcsv)
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)


if __name__ == '__main__':
  main()
