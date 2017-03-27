import csv
from bs4 import BeautifulSoup
import requests
import MySQLdb
import re
import os
import sys
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fileDir+'/../../includes/')
sys.path.insert(0, fileDir+'/../../')
from wrappers.logger import loggerFetch
from wrappers.sn import driverInitialize,driverFinalize,displayInitialize,displayFinalize,waitUntilID
from wrappers.db import dbInitialize,dbFinalize
from crawlSettings import nregaDB 
from crawlFunctions import formatName

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='These scripts will initialize the Database for the district and populate relevant details')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  url="http://nrega.nic.in/netnrega/sthome.aspx"
  r=requests.get(url)
  myhtml=r.text
  htmlsoup=BeautifulSoup(myhtml)
  tables=htmlsoup.findAll('table')
  for table in tables:
    
    if "BIHAR" in str(table):
       logger.info("The Table Found")
       links=table.findAll('a')
       
       logger.info(str(len(links)))
       for link in links:
         #if "BIHAR" in str(link):
         if "state_name" in str(link):
           stateURL=link['href']+"&lflag=eng"
           logger.info(stateURL)
           r=re.findall('http://(.*?)\/',stateURL)
           crawlIP=r[0]
           r=requests.get(stateURL)
           myhtml=r.text
           htmlsoup=BeautifulSoup(myhtml)
           table=htmlsoup.find('table',id="gvdist")
           distLinks = table.findAll('a')
           for distLink in distLinks:
             districtURL=distLink['href']
             #r=re.findall('http://(.*?)\/',districtURL)
             #crawlIP=r[0]
             logger.info(districtURL)
             districtURLPrefix="http://%s/netnrega/" % crawlIP
             r=re.findall('district_code=(.*?)\&',districtURL)
             fullDistrictCode=r[0]
             districtCode=r[0][2:4]
             stateCode=r[0][0:2]
             r=re.findall('state_name=(.*?)\&',districtURL)
             stateName=r[0]
             r=re.findall('district_name=(.*?)\&',districtURL)
             rawDistrictName=r[0]
             logger.info("Crawl IP : %s " ,crawlIP) 
             logger.info("District Code : %s " ,districtCode) 
             logger.info("State Code : %s " ,stateCode) 
             logger.info("District Name : %s " ,rawDistrictName) 
             logger.info("State Name : %s " ,stateName)
             r=re.findall('district_code=(.*?)\"',str(distLink))
             query="select * from districts where fullDistrictCode='%s' " % (fullDistrictCode)
             cur.execute(query)
             if cur.rowcount == 0:
               query="insert into districts (fullDistrictCode) values ('%s')" % fullDistrictCode
               cur.execute(query)
             query="update districts set districtURL='%s',districtName='%s',rawDistrictName='%s',crawlIP='%s',stateName='%s',stateCode='%s',districtCode='%s' where fullDistrictCode='%s'" %(districtURLPrefix+districtURL,formatName(rawDistrictName),rawDistrictName,crawlIP,stateName,stateCode,districtCode,fullDistrictCode)
             logger.info(query)
             cur.execute(query) 
           #r=requests.get(stateURL)
           
           #r=re.findall('state_name=(.*?)\&',str(link))
           #rawBlockName=r[0]
          
  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
