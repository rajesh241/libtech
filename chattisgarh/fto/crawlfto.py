import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import os
import sys
import time
import re
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
from settings import dbhost,dbuser,dbpasswd,sid,token
#Error File Defination
errorfile = open('/tmp/crawlfto.log', 'w')

sys.path.insert(0, fileDir+'/../../')
#sys.path.insert(0, rootdir)
from libtechFunctions import singleRowQuery,getFullFinYear
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='Script for crawling, downloading & parsing musters')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-t', '--timeout', help='Time to wait before a page loads', required=False)
  parser.add_argument('-b', '--browser', help='Specify the browser to test with', required=False)
  parser.add_argument('-u', '--url', help='Specify the url to crawl', required=False)
  parser.add_argument('-d', '--directory', help='Specify directory to download html file to', required=False)
  parser.add_argument('-q', '--query', help='Query to specify the workset, E.g ... where id=147', required=False)
  parser.add_argument('-j', '--jobcard', help='Specify the jobcard to download/push', required=False)
  parser.add_argument('-c', '--crawl', help='Crawl the Disbursement Data', required=False)
  parser.add_argument('-f', '--fetch', help='Fetch the Jobcard Details', required=False)
  parser.add_argument('-finyear', '--finyear', help='Download musters for that finyear', required=False)
  parser.add_argument('-district', '--district', help='District for which you need to Download', required=False)
  parser.add_argument('-p', '--parse', help='Parse Jobcard HTML for Muster Info', required=False, action='store_const', const=True)
  parser.add_argument('-r', '--process', help='Process downloaded HTML files for Muster Info', required=False, action='store_const', const=True)
  parser.add_argument('-P', '--push', help='Push Muster Info into the DB on the go', required=False, action='store_const', const=True)
  parser.add_argument('-J', '--jobcard-details', help='Fetch the Jobcard Details for DB jobcardDetails table', required=False, action='store_const', const=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  #This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)

  db = dbInitialize(db="libtech", charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)

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
  fullFinyear=getFullFinYear(finyear) 
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

  query="select stateCode,districtCode,blockCode,name from blocks where isActive=1"
  cur.execute(query)
  results = cur.fetchall()
  for row in results:
    stateCode=row[0]
    districtCode=row[1]
    blockCode=row[2]
    blockName=row[3]
    fullBlockCode=stateCode+districtCode+blockCode
    logger.info(stateCode+districtCode+blockCode+blockName)
    url="http://"+crawlIP+"/netnrega/FTO/fto_reprt_detail.aspx?lflag=local&flg=W&page=b&state_name="+stateName.upper()+"&state_code="+stateCode+"&district_name="+districtName.upper()+"&district_code="+stateCode+districtCode+"&block_name="+blockName+"&block_code="+stateCode+districtCode+blockCode+"&fin_year="+fullFinyear+"&typ=pb&mode=b"
    logger.info(url)
    r  = requests.get(url)
    htmlsource=r.text
    htmlsoup=BeautifulSoup(htmlsource)
    for fto in htmlsoup.find_all('a'):
      ftoNo=fto.contents[0]
      #ftoURL="http://164.100.112.66/netnrega/FTO/"+fto.get('href')
      if fullBlockCode in ftoNo:
        query="insert into ftoDetails (ftoNo,stateCode,districtCode,blockCode,finyear) values ('"+ftoNo+"','"+stateCode+"','"+districtCode+"','"+blockCode+"','"+finyear+"');"
        try:
          logger.info(query)
          cur.execute(query)
        except MySQLdb.IntegrityError,e:
          errormessage=(time.strftime("%d/%m/%Y %H:%M:%S "))+str(e)+"\n"
          errorfile.write(errormessage)
        continue
   


if __name__ == '__main__':
  main()
