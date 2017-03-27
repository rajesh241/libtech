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
  parser.add_argument('-u', '--districtURL', help='Please enter the URL of the district page from the nrega site that you want to crawl', required=True)
  parser.add_argument('-jp', '--jobcardPrefix', help='Enter the Jobcard Prefix for the state for example chatisgarh is CH, and Karnataka is KN', required=True)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))

  logger.info("BEGIN PROCESSING...")
  #This is a Kludge to remove all the input tags from the html because for some reason Beautiful Soup does not parse the html correctly
  regex=re.compile(r'<input+.*?"\s*/>+',re.DOTALL)


  districtURL=args['districtURL']+"&"
  stateShortCode=args['jobcardPrefix']

  r=re.findall('http://(.*?)\/',districtURL)
  crawlIP=r[0]
  r=re.findall('district_code=(.*?)\&',districtURL)
  fullDistrictCode=r[0]
  districtCode=r[0][2:4]
  r=re.findall('state_Code=(.*?)\&',districtURL)
  stateCode=r[0]
  r=re.findall('state_name=(.*?)\&',districtURL)
  stateName=r[0]
  r=re.findall('district_name=(.*?)\&',districtURL)
  rawDistrictName=r[0]
  logger.info("Crawl IP : %s " ,crawlIP) 
  logger.info("District Code : %s " ,districtCode) 
  logger.info("State Code : %s " ,stateCode) 
  logger.info("District Name : %s " ,rawDistrictName) 
  logger.info("State Name : %s " ,stateName)
  db = dbInitialize(db=nregaDB, charset="utf8")  # The rest is updated automatically in the function
  cur=db.cursor()
  db.autocommit(True)
  #Query to set up Database to read Hindi Characters
  query="SET NAMES utf8"
  cur.execute(query)
  query="select * from districts where fullDistrictCode='%s' " % (fullDistrictCode)
  cur.execute(query)
  if cur.rowcount == 0:
    query="insert into districts (fullDistrictCode) values ('%s')" % fullDistrictCode
    cur.execute(query)
  query="update districts set districtName='%s',rawDistrictName='%s',crawlIP='%s',stateName='%s',stateShortCode='%s',stateCode='%s',districtCode='%s' where fullDistrictCode='%s'" %(formatName(rawDistrictName),rawDistrictName,crawlIP,stateName,stateShortCode,stateCode,districtCode,fullDistrictCode)
  logger.info(query)
  cur.execute(query) 
  r=re.findall('=(.*?)\&',districtURL)
  r=requests.get(districtURL)
  blockHTML=r.text
  htmlsoup=BeautifulSoup(blockHTML)
  table=htmlsoup.find('table',id="gvdpc")
  rows = table.findAll('tr')
  for row in rows:
    columns=row.findAll('td')
    for column in columns:
      r=re.findall('Block_Code=(.*?)\"',str(column))
      fullBlockCode=r[0]
      blockCode=r[0][4:8]
      r=re.findall('block_name=(.*?)\&',str(column))
      rawBlockName=r[0]
      logger.info("Block Code: %s BlockName : %s" % (blockCode,rawBlockName))

      query="select * from blockStatus where fullBlockCode='%s' " % fullBlockCode
      cur.execute(query)
      if cur.rowcount == 0:
        query="insert into blockStatus (fullBlockCode,rawBlockName) values ('%s','%s') " % (fullBlockCode,rawBlockName)
        logger.info(query)
        cur.execute(query)

      query="select * from blocks where fullBlockCode='%s' " % fullBlockCode
      cur.execute(query)
      if cur.rowcount == 0:
        query="insert into blocks (fullBlockCode) values ('%s') " % fullBlockCode
        cur.execute(query)
      query="update blocks set blockName='%s',rawBlockName='%s',districtName='%s',rawDistrictName='%s',stateName='%s',stateCode='%s',districtCode='%s',blockCode='%s' where fullBlockCode='%s'" % (formatName(rawBlockName),rawBlockName,formatName(rawDistrictName),rawDistrictName,stateName,stateCode,districtCode,blockCode,fullBlockCode)
      logger.info(query)
      cur.execute(query) 
      finyear='2015-2016'
      panchayaturl="http://%s/netnrega/Progofficer/PoIndexFrame.aspx?flag_debited=R&lflag=local&District_Code=%s&district_name=%s&state_name=%s&state_Code=%s&finyear=%s&check=1&block_name=%s&Block_Code=%s" %(crawlIP,fullDistrictCode,rawDistrictName.upper(),stateName.upper(),stateCode,finyear,rawBlockName.upper(),fullBlockCode)
      logger.info("URL "+panchayaturl)
      r  = requests.get(panchayaturl)
      htmlsource1=r.text
      htmlsoup1=BeautifulSoup(htmlsource1)
      table1=htmlsoup1.find('table',id="ctl00_ContentPlaceHolder1_gvpanch")
      try:
        table1.findAll('a')    
        noPanchayat=0
      except:
        noPanchayat=1
      if noPanchayat == 0:
        for eachPanchayat in table1.findAll('a'):
          rawPanchayatName=eachPanchayat.contents[0]
          panchayatLink=eachPanchayat.get('href')
          getPanchayat=re.findall(r'(?:Panchayat_Code=)\d{10}',panchayatLink)
          logger.info(getPanchayat[0])
          fullPanchayatCode=getPanchayat[0].replace("Panchayat_Code=","")
          panchayatCode=fullPanchayatCode[7:11]
          getPanchayat=re.findall(r'(?:Panchayat_Code=)\d{10}',panchayatLink)
          #fullPanchayatCode=getPanchayat[0]
          #panchayatCode=fullPanchayatCode[len(fullPanchayatCode)-3:len(fullPanchayatCode)]
          print rawPanchayatName+panchayatCode
          query="select * from panchayatStatus where fullPanchayatCode='%s' " % fullPanchayatCode
          cur.execute(query)
          if cur.rowcount == 0:
            query="insert into panchayatStatus (fullPanchayatCode,rawPanchayatName) values ('%s','%s') " % (fullPanchayatCode,rawPanchayatName)
            logger.info(query)
            cur.execute(query)

          query="select * from panchayats where fullPanchayatCode='%s' " % fullPanchayatCode
          cur.execute(query)
          if cur.rowcount == 0:
            query="insert into panchayats (fullPanchayatCode) values ('%s') " % fullPanchayatCode
            logger.info(query)
            cur.execute(query)
          query="update panchayats set fullBlockCode='%s',stateShortCode='%s',crawlIP='%s',panchayatName='%s',rawPanchayatName='%s',blockName='%s',rawBlockName='%s',districtName='%s',rawDistrictName='%s',stateName='%s',stateCode='%s',districtCode='%s',blockCode='%s',panchayatCode='%s' where fullPanchayatCode='%s'" % (fullBlockCode,stateShortCode,crawlIP,formatName(rawPanchayatName),rawPanchayatName,formatName(rawBlockName),rawBlockName,formatName(rawDistrictName),rawDistrictName,stateName,stateCode,districtCode,blockCode,panchayatCode,fullPanchayatCode)
          logger.info(query)
          cur.execute(query)
   

  dbFinalize(db) # Make sure you put this if there are other exit paths or errors
  logger.info("...END PROCESSING")     
  exit(0)
if __name__ == '__main__':
  main()
