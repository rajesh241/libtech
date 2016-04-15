import csv
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
from libtechFunctions import getFullFinYear,singleRowQuery
from globalSettings import datadir,nregaDataDir
from settings import dbhost,dbuser,dbpasswd,sid,token
from globalSettings import datadir
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
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
  display = displayInitialize()
  driver = driverInitialize()
  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  limitString=''
  if args['limit']:
    limitString=' limit '+args['limit']
  if args['district']:
    districtName=args['district']
  else:
    districtName='surguja'
 
  logger.info("DistrictName "+districtName)
  if args['finyear']:
    finyear=args['finyear']
  else:
    finyear='16'
  logger.info("finyear "+finyear)
#Query to get all the blocks
  query="use libtech"
  cur.execute(query)
  query="select crawlIP from crawlDistricts where name='%s'" % districtName.lower()
  crawlIP=singleRowQuery(cur,query)
  query="select state from crawlDistricts where name='%s'" % districtName.lower()
  stateName=singleRowQuery(cur,query)
  logger.info("crawlIP "+crawlIP)
  logger.info("State Name "+stateName)
  query="use %s" % districtName.lower()
  cur.execute(query)



  ftofilepath=nregaDataDir.replace("stateName",stateName.title())+"/"+districtName.upper()+"/"
#
  url="http://services.ptcmysore.gov.in/emo/Trackfto.aspx"
  #ftofilepath="/home/libtech/libtechdata/CHATTISGARH/"+districtName+"/"
  query="select b.name,f.ftoNo,f.stateCode,f.districtCode,f.blockCode,f.finyear,f.id from ftoDetails f,blocks b where TIMESTAMPDIFF(HOUR, f.statusDownloadDate, now()) > 48  and f.isStatusDownloaded=0 and f.finyear='%s' and f.blockCode=b.blockCode and f.stateCode=b.stateCode and f.districtCode=b.districtCode %s;" % (finyear,limitString)
  #query="select b.name,f.ftoNo,f.stateCode,f.districtCode,f.blockCode,f.finyear,f.id from ftoDetails f,blocks b where f.isDownloaded=0 and f.blockCode=b.blockCode and f.stateCode=b.stateCode and f.districtCode=b.districtCode and b.blockCode='003';"
  cur.execute(query)
  if cur.rowcount:
    logger.info("Number of records tobe processed:" +str(cur.rowcount))
    results = cur.fetchall()
    for row in results:
      blockName=row[0]
      ftono=row[1]
      stateCode=row[2]
      districtCode=row[3]
      blockCode=row[4]
      finyear=row[5]
      ftoid=row[6]
      fullBlockCode=stateCode+districtCode+blockCode
      fullDistrictCode=stateCode+districtCode
      fullfinyear=getFullFinYear(finyear) 
      logger.info(stateCode+districtCode+blockCode+blockName)
      
      ftofilename=ftofilepath+blockName+"/FTO/"+fullfinyear+"/"+ftono+"_status.html"
      if not os.path.exists(os.path.dirname(ftofilename)):
        os.makedirs(os.path.dirname(ftofilename))
      
      logger.info(ftofilename)
      driver.get(url)
      driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtFTO").clear()
      #driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtFTO").send_keys("CH3305003_081015FTO_142597")
      driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtFTO").send_keys(ftono)
      driver.find_element_by_id("ctl00_ContentPlaceHolder1_Button1").click()
      html_source = driver.page_source
      html_source=html_source.replace('<head>','<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
     # print html_source
      f = open(ftofilename, 'w')
      f.write(html_source.encode("UTF-8"))
      query="update ftoDetails set isStatusDownloaded=1,statusDownloadDate=now() where id="+str(ftoid)
      logger.info(query)
      cur.execute(query)
   
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
